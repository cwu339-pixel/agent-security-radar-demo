"""Unified content item model for all data sources."""
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class SourceType(Enum):
    GITHUB = "github"
    X = "x"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    LINKEDIN = "linkedin"
    NEWS = "news"
    BLOG = "blog"
    WEBSITE = "website"


@dataclass(frozen=True)
class ContentItem:
    """Immutable data model for content from any source.

    Fields:
        title: Display name (repo name for GitHub, article title for news)
        description: Content summary or body excerpt
        url: Source link
        source: Which scraper produced this item
        published_date: ISO date string
        engagement: Stars for GitHub, upvotes for Reddit/HN
        content_type: Language for GitHub, flair/tag for others
    """

    title: str
    description: str
    url: str
    source: SourceType
    published_date: Optional[str] = None
    engagement: Optional[str] = None
    content_type: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict representation."""
        result = asdict(self)
        result["source"] = self.source.value
        return result
