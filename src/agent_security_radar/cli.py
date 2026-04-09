"""Command-line interface for Agent Security Radar."""
import argparse
import json
import logging
import os
import sys
import time
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agent_security_radar.analyzer.event_tracker import deduplicate_items
from agent_security_radar.models.content_item import ContentItem
from agent_security_radar.pipeline import (
    build_company_cards,
    load_signals,
    rank_companies,
)
from agent_security_radar.render import render_brief

logger = logging.getLogger(__name__)

AVAILABLE_SOURCES = ("github", "x", "reddit", "hackernews")

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Security Radar - continuous agent security company scanner",
    )

    subparsers = parser.add_subparsers(dest="command")

    demo_parser = subparsers.add_parser(
        "demo", help="Run with sample data (no API key needed)"
    )
    demo_parser.add_argument(
        "--output-dir", default="outputs", help="Output directory"
    )

    scan_parser = subparsers.add_parser(
        "scan", help="Live scan from real sources (requires OPENAI_API_KEY)"
    )
    scan_parser.add_argument(
        "--sources",
        nargs="+",
        choices=[*AVAILABLE_SOURCES, "all"],
        default=["all"],
        help="Data sources to scan",
    )
    scan_parser.add_argument(
        "--max", type=int, default=20,
        help="Max items to classify",
    )
    scan_parser.add_argument(
        "--per-source", type=int, default=5,
        help="Max items per source",
    )
    scan_parser.add_argument(
        "--output-dir", default="outputs", help="Output directory"
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo(args)
    elif args.command == "scan":
        run_scan(args)
    else:
        parser.print_help()


def run_demo(args) -> None:
    """Run pipeline with sample data."""
    print("=" * 50)
    print("Agent Security Radar - Demo Mode")
    print("=" * 50)
    print()

    signals = load_signals(ROOT / "data" / "sample_signals.json")
    print(f"Loaded {len(signals)} sample signals")

    ranked = rank_companies(build_company_cards(signals))
    _write_outputs(ranked, args.output_dir)


def run_scan(args) -> None:
    """Run live scanning pipeline."""
    run_start = time.time()

    print("=" * 50)
    print("Agent Security Radar - Live Scan")
    print("=" * 50)
    print()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found")
        print("Set it in .env file or environment variable")
        print("For demo mode without API key: python -m agent_security_radar.cli demo")
        return

    sources = (
        list(AVAILABLE_SOURCES)
        if "all" in args.sources
        else list(args.sources)
    )

    all_items = _scrape_all_sources(sources, per_source=args.per_source)

    if not all_items:
        print("No content found from configured sources")
        return

    deduped, original_count = deduplicate_items(all_items)
    print(f"Event dedup: {original_count} -> {len(deduped)}")
    print()

    selected = deduped[: args.max]

    print(f"Classifying {len(selected)} items with LLM...")
    from agent_security_radar.analyzer.classifier import SignalClassifier

    classifier = SignalClassifier()
    signals = classifier.classify_batch(selected, max_items=args.max)
    metrics = classifier.get_metrics()
    print(
        f"  Classified: {metrics['success']}/{metrics['total']} "
        f"(failed: {metrics['failed']})"
    )
    print()

    if not signals:
        print("No signals classified successfully")
        return

    ranked = rank_companies(build_company_cards(signals))

    elapsed = time.time() - run_start
    _write_outputs(ranked, args.output_dir)

    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"  Sources: {', '.join(sources)}")
    print(f"  Scraped: {original_count}")
    print(f"  Deduped: {len(deduped)}")
    print(f"  Classified: {len(signals)}")
    print(f"  Companies: {len(ranked)}")


def _scrape_all_sources(
    sources: list[str], per_source: int = 5
) -> list[ContentItem]:
    """Run all requested scrapers."""
    all_items: list[ContentItem] = []

    if "github" in sources:
        all_items.extend(_scrape_github())

    if "x" in sources:
        all_items.extend(_scrape_x())

    if "reddit" in sources:
        all_items.extend(_scrape_reddit())

    if "hackernews" in sources:
        all_items.extend(_scrape_hackernews())

    return all_items


def _scrape_github() -> list[ContentItem]:
    print("Scanning GitHub Trending (agent security)...")
    try:
        from agent_security_radar.scrapers.github_scraper import (
            AGENT_SECURITY_KEYWORDS,
            GitHubScraper,
        )

        scraper = GitHubScraper()
        all_projects = scraper.fetch(since="daily")
        filtered = scraper.filter_by_keywords(
            all_projects, AGENT_SECURITY_KEYWORDS
        )
        print(f"  Found {len(filtered)} agent-security-related repos")
        return filtered
    except Exception as e:
        logger.warning("GitHub scrape failed: %s", e)
        print(f"  GitHub failed: {e}")
        return []


def _scrape_x() -> list[ContentItem]:
    print("Scanning X feeds (Nitter RSS)...")
    try:
        from agent_security_radar.scrapers.x_scraper import XScraper

        scraper = XScraper()
        items = scraper.fetch(max_items=15, per_handle=3)
        if not scraper.handles:
            print("  No X handles configured, skipping")
            return []
        print(f"  Found {len(items)} posts from {len(scraper.handles)} handles")
        return items
    except Exception as e:
        logger.warning("X scrape failed: %s", e)
        print(f"  X failed: {e}")
        return []


def _scrape_reddit() -> list[ContentItem]:
    print("Scanning Reddit (r/cybersecurity, r/netsec)...")
    try:
        from agent_security_radar.scrapers.reddit_scraper import RedditScraper

        items: list[ContentItem] = []
        for sub in ["cybersecurity", "netsec", "ArtificialIntelligence"]:
            scraper = RedditScraper(subreddit=sub, sort="hot")
            sub_items = scraper.fetch(max_items=10)
            items.extend(sub_items)
        print(f"  Found {len(items)} Reddit posts")
        return items
    except Exception as e:
        logger.warning("Reddit scrape failed: %s", e)
        print(f"  Reddit failed: {e}")
        return []


def _scrape_hackernews() -> list[ContentItem]:
    print("Scanning Hacker News...")
    try:
        from agent_security_radar.scrapers.hackernews_scraper import (
            HackerNewsScraper,
        )

        scraper = HackerNewsScraper(min_points=10)
        items = scraper.fetch(max_items=15)
        print(f"  Found {len(items)} HN stories")
        return items
    except Exception as e:
        logger.warning("HN scrape failed: %s", e)
        print(f"  HN failed: {e}")
        return []


def _write_outputs(ranked: list[dict], output_dir: str) -> None:
    """Write ranking JSON and markdown brief."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ranking_path = out / "ranking.json"
    ranking_path.write_text(json.dumps(ranked, indent=2, ensure_ascii=False))
    print(f"Wrote {ranking_path}")

    brief_path = out / "daily_brief.md"
    brief_path.write_text(
        render_brief(ranked, generated_on=str(date.today()))
    )
    print(f"Wrote {brief_path}")

    core = [c for c in ranked if c["universe_tier"] == "core"]
    adjacent = [c for c in ranked if c["universe_tier"] == "adjacent"]
    excluded = [c for c in ranked if c["universe_tier"] == "out_of_scope"]

    print()
    print(f"Results: {len(core)} core, {len(adjacent)} adjacent, {len(excluded)} out of scope")
    if core:
        print(f"Top candidate: {core[0]['display_name']} (score: {core[0]['total_score']})")


if __name__ == "__main__":
    main()
