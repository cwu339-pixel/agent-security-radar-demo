"""Event deduplication for multi-source signals."""

from __future__ import annotations

import re
from typing import List, Sequence, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from agent_security_radar.models.content_item import ContentItem

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "to",
    "with", "will", "after", "new",
}

_DROP_QUERY_PREFIXES = (
    "utm_", "fbclid", "gclid", "ref", "source",
)


def canonicalize_url(url: str) -> str:
    """Normalize URL for cross-source deduplication."""
    raw = str(url or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
    except Exception:
        return raw
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/")
    if not path:
        path = "/"
    query_pairs = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=False)
        if not any(
            k.lower().startswith(prefix)
            for prefix in _DROP_QUERY_PREFIXES
        )
    ]
    query = urlencode(sorted(query_pairs))
    return urlunparse((scheme, netloc, path, "", query, ""))


def tokenize_text(text: str) -> List[str]:
    """Tokenize text for similarity matching."""
    clean = re.sub(r"\s+", " ", str(text or "").strip().lower())
    if not clean:
        return []
    words = re.findall(r"[a-z0-9]+", clean)
    return list(
        dict.fromkeys(tok for tok in words if tok not in _STOPWORDS)
    )


def _jaccard(a: Sequence[str], b: Sequence[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def _source_priority(source_value: str) -> int:
    order = {
        "x": 5,
        "github": 4,
        "hackernews": 3,
        "reddit": 2,
        "linkedin": 4,
        "news": 5,
        "blog": 3,
        "website": 2,
    }
    return order.get(str(source_value or "").lower(), 1)


def _to_int(value) -> int:
    try:
        return int(str(value or "0").replace(",", ""))
    except Exception:
        return 0


def _item_rank_score(item: ContentItem) -> float:
    return (
        float(_source_priority(item.source.value)) * 10_000.0
        + float(_to_int(item.engagement))
        + float(len(item.description or ""))
    )


def deduplicate_items(
    items: Sequence[ContentItem],
    similarity_threshold: float = 0.58,
) -> Tuple[List[ContentItem], int]:
    """Deduplicate same events across sources.

    Returns (deduped_items, original_count).
    """
    clusters: List[dict] = []

    for item in items:
        canonical_url = canonicalize_url(item.url)
        tokens = tokenize_text(f"{item.title} {item.description}")
        best_idx = -1
        best_score = 0.0

        for idx, cluster in enumerate(clusters):
            if canonical_url and canonical_url in cluster["urls"]:
                best_idx = idx
                break
            score = _jaccard(tokens, cluster["tokens"])
            if score >= similarity_threshold and score > best_score:
                best_idx = idx
                best_score = score

        if best_idx == -1:
            clusters.append({
                "items": [item],
                "tokens": tokens,
                "urls": [canonical_url] if canonical_url else [],
            })
            continue

        cluster = clusters[best_idx]
        cluster["items"].append(item)
        cluster["tokens"] = list(
            dict.fromkeys([*cluster["tokens"], *tokens])
        )
        if canonical_url and canonical_url not in cluster["urls"]:
            cluster["urls"].append(canonical_url)

    deduped: List[ContentItem] = []
    for cluster in clusters:
        representative = sorted(
            cluster["items"],
            key=lambda it: _item_rank_score(it),
            reverse=True,
        )[0]
        deduped.append(representative)

    return deduped, len(items)
