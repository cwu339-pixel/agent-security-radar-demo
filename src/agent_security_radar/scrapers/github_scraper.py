"""GitHub Trending scraper filtered for agent security keywords."""
import logging
import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from agent_security_radar.models.content_item import ContentItem, SourceType
from agent_security_radar.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

AGENT_SECURITY_KEYWORDS = [
    "agent security", "agent safety", "agent guardrails", "agent sandbox",
    "agent auth", "agent permissions", "tool use security",
    "prompt injection", "prompt guard", "llm firewall", "llm guard",
    "ai guardrails", "ai safety", "ai security", "ai sandbox",
    "runtime security", "policy engine", "runtime guardrail",
    "agent observability", "agent audit", "agent monitoring",
    "mcp security", "function calling security", "tool calling",
    "red team", "jailbreak", "adversarial", "alignment",
]


class GitHubScraper(BaseScraper):
    """Scrape GitHub Trending page and return ContentItem list."""

    BASE_URL = "https://github.com/trending"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36"
        )
    }

    def source_name(self) -> str:
        return "GitHub Trending"

    def fetch(
        self,
        language: Optional[str] = None,
        since: str = "daily",
        **kwargs,
    ) -> List[ContentItem]:
        """Fetch trending projects from GitHub."""
        url = (
            f"{self.BASE_URL}/{language}" if language else self.BASE_URL
        )
        params = {"since": since}

        try:
            response = requests.get(
                url, headers=self.HEADERS, params=params, timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Failed to fetch GitHub Trending: %s", e)
            return []

        return self._parse_trending_page(response.text)

    def _parse_trending_page(self, html: str) -> List[ContentItem]:
        """Parse trending page HTML into ContentItem list."""
        soup = BeautifulSoup(html, "html.parser")
        items = []

        for article in soup.find_all("article", class_="Box-row"):
            try:
                item = self._parse_single_article(article)
                if item is not None:
                    items.append(item)
            except Exception as e:
                logger.warning("Failed to parse project: %s", e)

        return items

    def _parse_single_article(self, article) -> Optional[ContentItem]:
        """Parse a single <article> element."""
        h2 = article.find("h2", class_="h3")
        if not h2:
            return None

        repo_link = h2.find("a")
        if not repo_link:
            return None

        repo_name = repo_link.get("href", "").strip("/")
        repo_url = f"https://github.com{repo_link.get('href', '')}"

        desc_elem = article.find("p", class_="col-9")
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        lang_elem = article.find(
            "span", attrs={"itemprop": "programmingLanguage"}
        )
        language = lang_elem.get_text(strip=True) if lang_elem else "Unknown"

        stars_elem = article.find(
            "span", class_="d-inline-block float-sm-right"
        )
        stars_text = (
            stars_elem.get_text(strip=True) if stars_elem else "0"
        )
        stars = (
            re.sub(r"[^\d]", "", stars_text.split("today")[0])
            if "today" in stars_text
            else "0"
        )

        return ContentItem(
            title=repo_name,
            description=description,
            url=repo_url,
            source=SourceType.GITHUB,
            engagement=stars,
            content_type=language,
        )


def get_agent_security_trending() -> List[ContentItem]:
    """Convenience: fetch agent-security-related trending projects."""
    scraper = GitHubScraper()
    all_projects = scraper.fetch(since="daily")
    return scraper.filter_by_keywords(all_projects, AGENT_SECURITY_KEYWORDS)
