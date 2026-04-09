"""Hacker News scraper via Algolia HN Search API (no auth required)."""
import logging
import time
from typing import List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from agent_security_radar.models.content_item import ContentItem, SourceType
from agent_security_radar.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

_DEFAULT_KEYWORDS = [
    "agent security", "AI security", "AI safety",
    "prompt injection", "guardrails", "LLM firewall",
    "agent sandbox", "tool use", "function calling",
    "AI red team", "jailbreak", "alignment",
    "MCP security", "agent auth",
]

_HEADERS = {
    "User-Agent": "agent-security-radar/1.0 (automated research tool)"
}

_HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
_HN_ITEM_BASE = "https://news.ycombinator.com/item?id="
_HN_TIMEOUT_SECONDS = 10


def _build_session() -> requests.Session:
    """Create a requests session with lightweight retry."""
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class HackerNewsScraper(BaseScraper):
    """Fetch agent-security-related stories from HN via Algolia Search API."""

    def __init__(
        self,
        keywords: List[str] | None = None,
        min_points: int = 10,
        hours_back: int = 48,
    ) -> None:
        self._keywords = (
            keywords if keywords is not None else _DEFAULT_KEYWORDS
        )
        self._min_points = min_points
        self._hours_back = hours_back
        self._session = _build_session()
        self._network_unavailable = False

    def source_name(self) -> str:
        return "Hacker News"

    def fetch(self, max_items: int = 20, **kwargs) -> List[ContentItem]:
        """Return agent-security-related HN stories."""
        seen_ids: set[str] = set()
        all_hits: List[dict] = []

        for keyword in self._keywords:
            if self._network_unavailable:
                break
            hits = self._search_keyword(keyword)
            for hit in hits:
                story_id = hit.get("objectID", "")
                if story_id and story_id not in seen_ids:
                    seen_ids.add(story_id)
                    all_hits.append(hit)

        all_hits.sort(
            key=lambda h: h.get("points", 0) or 0, reverse=True
        )

        items: List[ContentItem] = []
        for hit in all_hits[:max_items]:
            item = self._hit_to_item(hit)
            if item is not None:
                items.append(item)
        return items

    def _search_keyword(self, keyword: str) -> List[dict]:
        since_ts = int(time.time()) - self._hours_back * 3600
        params = {
            "query": keyword,
            "tags": "story",
            "numericFilters": f"points>={self._min_points},created_at_i>{since_ts}",
            "hitsPerPage": 20,
        }

        try:
            response = self._session.get(
                _HN_SEARCH_URL,
                headers=_HEADERS,
                params=params,
                timeout=_HN_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json().get("hits", [])
        except requests.RequestException as exc:
            if isinstance(
                exc,
                (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                ),
            ):
                self._network_unavailable = True
            logger.warning(
                "HN Algolia fetch failed for '%s': %s", keyword, exc
            )
            return []

    def _hit_to_item(self, hit: dict) -> ContentItem | None:
        try:
            title = hit.get("title", "").strip()
            story_text = hit.get("story_text") or ""
            description = story_text[:500].strip() if story_text else ""
            url = hit.get("url") or f"{_HN_ITEM_BASE}{hit.get('objectID', '')}"
            points = hit.get("points", 0) or 0
            created_at = hit.get("created_at")
            author = hit.get("author", "")

            return ContentItem(
                title=title,
                description=description,
                url=url,
                source=SourceType.HACKERNEWS,
                published_date=created_at,
                engagement=str(points),
                content_type=author,
            )
        except Exception as exc:
            logger.warning(
                "Failed to parse HN hit %s: %s",
                hit.get("objectID"),
                exc,
            )
            return None
