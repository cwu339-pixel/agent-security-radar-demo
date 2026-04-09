"""LLM-powered signal classifier for agent security relevance.

Takes raw ContentItem from scrapers and classifies into the signal format
expected by pipeline.py (company_ref, tags, category_hint).
"""
import json
import logging
import os
import re
import time
from datetime import date
from typing import Any, Dict, List, Optional

from openai import OpenAI, RateLimitError

from agent_security_radar.models.content_item import ContentItem
from agent_security_radar.pipeline import TAG_WEIGHTS, CORE_CATEGORY_HINTS

logger = logging.getLogger(__name__)

VALID_TAGS = list(TAG_WEIGHTS.keys())
VALID_CATEGORIES = [
    *list(CORE_CATEGORY_HINTS),
    "adjacent_ai_security",
    "out_of_scope",
]

SYSTEM_PROMPT = """You are an agent security investment analyst.

Given a content signal (from GitHub, X, Reddit, HN, etc.), extract:
1. company_ref: the company name this signal is about (if identifiable)
2. tags: relevant tags from this list: {tags}
3. category_hint: one of {categories}

If no specific company is identifiable, use the project/org name.
If the signal is about the agent security field in general (not a company), set company_ref to the most relevant entity mentioned.

Output ONLY valid JSON, no other text."""

USER_PROMPT = """Signal:
- Source: {source}
- Title: {title}
- Description: {description}
- URL: {url}
- Engagement: {engagement}

Extract company_ref, tags (array), and category_hint.
Output JSON only:
{{"company_ref": "...", "tags": [...], "category_hint": "..."}}"""


class SignalClassifier:
    """Classify raw content items into structured signals for the pipeline."""

    _MAX_RETRIES = 2
    _RETRY_BACKOFF = 5

    def __init__(self, api_key: Optional[str] = None):
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Set it in .env or environment."
            )
        self.model_id = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=resolved_key)
        self._last_call_ts: float = 0.0
        rpm = int(os.getenv("OPENAI_RPM", "60"))
        self._request_interval = 60.0 / max(rpm, 1)
        self._metrics: Dict[str, int] = {
            "total": 0, "success": 0, "failed": 0,
        }

    def classify_item(self, item: ContentItem) -> Optional[Dict[str, Any]]:
        """Classify a single ContentItem into a pipeline signal dict."""
        self._metrics["total"] += 1

        prompt = USER_PROMPT.format(
            source=item.source.value,
            title=item.title,
            description=(item.description or "")[:400],
            url=item.url,
            engagement=item.engagement or "N/A",
        )

        system = SYSTEM_PROMPT.format(
            tags=", ".join(VALID_TAGS),
            categories=", ".join(VALID_CATEGORIES),
        )

        for attempt in range(self._MAX_RETRIES):
            self._wait_for_rate_limit()
            try:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                )
                text = response.choices[0].message.content or "{}"
                parsed = self._parse_json(text)
                signal = self._normalize(parsed, item)
                self._metrics["success"] += 1
                return signal

            except RateLimitError:
                if attempt < self._MAX_RETRIES - 1:
                    time.sleep(self._RETRY_BACKOFF)
                    continue
                logger.warning(
                    "Rate limited classifying '%s'", item.title
                )
                self._metrics["failed"] += 1
                return self._fallback_signal(item)
            except Exception as e:
                logger.warning(
                    "Error classifying '%s': %s", item.title, e
                )
                self._metrics["failed"] += 1
                return self._fallback_signal(item)

        return self._fallback_signal(item)

    def classify_batch(
        self, items: List[ContentItem], max_items: int = 30
    ) -> List[Dict[str, Any]]:
        """Classify a batch of ContentItems into pipeline signals."""
        signals = []
        for item in items[:max_items]:
            signal = self.classify_item(item)
            if signal is not None:
                signals.append(signal)
        return signals

    def get_metrics(self) -> Dict[str, int]:
        return {**self._metrics}

    def _wait_for_rate_limit(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_call_ts
        if elapsed < self._request_interval:
            time.sleep(self._request_interval - elapsed)
        self._last_call_ts = time.monotonic()

    @staticmethod
    def _parse_json(text: str) -> Dict:
        content = text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", content)
            if not match:
                raise
            return json.loads(match.group(0))

    @staticmethod
    def _normalize(
        parsed: Dict, item: ContentItem
    ) -> Dict[str, Any]:
        company_ref = str(parsed.get("company_ref", item.title)).strip()
        raw_tags = parsed.get("tags", [])
        tags = [t for t in raw_tags if t in VALID_TAGS] or [
            "ai_security_adjacent"
        ]
        category_hint = str(
            parsed.get("category_hint", "out_of_scope")
        ).strip()
        if category_hint not in VALID_CATEGORIES:
            category_hint = "out_of_scope"

        return {
            "source": item.source.value.capitalize(),
            "source_type": item.source.value,
            "company_ref": company_ref,
            "url": item.url,
            "headline": item.title,
            "published_at": (
                item.published_date or str(date.today())
            )[:10],
            "tags": tags,
            "category_hint": category_hint,
        }

    @staticmethod
    def _fallback_signal(item: ContentItem) -> Dict[str, Any]:
        return {
            "source": item.source.value.capitalize(),
            "source_type": item.source.value,
            "company_ref": item.title.split("/")[-1]
            if "/" in item.title
            else item.title,
            "url": item.url,
            "headline": item.title,
            "published_at": (
                item.published_date or str(date.today())
            )[:10],
            "tags": ["ai_security_adjacent"],
            "category_hint": "adjacent_ai_security",
        }
