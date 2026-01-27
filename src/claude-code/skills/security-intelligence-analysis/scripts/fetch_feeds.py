#!/usr/bin/env python3
"""
RSS Feed Fetcher Script for Security Intelligence Analysis Skill

Fetches cybersecurity news from RSS/Atom feeds and outputs JSON to stdout.
This script is designed to be run by Claude via bash as part of the
security-intelligence-analysis skill.

Usage:
    python fetch_feeds.py [--hours HOURS] [--feeds FEED_URLS...]

Examples:
    # Fetch last 24 hours from default feeds
    python fetch_feeds.py

    # Fetch last 48 hours
    python fetch_feeds.py --hours 48

    # Fetch from specific feeds
    python fetch_feeds.py --feeds "https://example.com/feed1" "https://example.com/feed2"
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

try:
    import feedparser
except ImportError:
    print(json.dumps({"error": "feedparser not installed. Run: pip install feedparser"}))
    sys.exit(1)

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests not installed. Run: pip install requests"}))
    sys.exit(1)


def load_default_feeds() -> List[str]:
    """Load default feed URLs from config file"""
    # Look for config in same skill directory
    script_dir = Path(__file__).parent
    config_paths = [
        script_dir.parent / "config" / "default_feeds.json",
        script_dir / "default_feeds.json",
        Path.cwd() / "config" / "default_feeds.json",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('feeds', [])
            except Exception as e:
                print(f"Warning: Error loading {config_path}: {e}", file=sys.stderr)
                continue

    # Fallback to hardcoded defaults
    return [
        "https://krebsonsecurity.com/feed/",
        "https://www.bleepingcomputer.com/feed/",
        "https://thehackernews.com/feeds/posts/default",
        "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "https://www.schneier.com/blog/atom.xml",
        "https://www.darkreading.com/rss.xml",
        "https://www.securityweek.com/feed/",
        "https://nakedsecurity.sophos.com/feed/",
    ]


def fetch_rss_feeds(feed_urls: List[str], hours_back: int = 24) -> Dict[str, Any]:
    """
    Fetch and parse RSS feeds, returning recent entries

    Args:
        feed_urls: List of RSS/Atom feed URLs
        hours_back: Only return entries from the last N hours

    Returns:
        Dictionary with entries list and metadata
    """
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    all_entries = []
    errors = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for url in feed_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            feed_title = feed.feed.get('title', url)

            for entry in feed.entries:
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                # Filter by date if available
                if published and published < cutoff_time:
                    continue

                # Clean up summary (remove HTML if present)
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    # Basic HTML tag removal
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = summary.strip()[:500]  # Limit length

                all_entries.append({
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': summary,
                    'published': published.isoformat() if published else None,
                    'source': feed_title
                })

        except requests.exceptions.Timeout:
            errors.append(f"Timeout fetching {url}")
        except requests.exceptions.RequestException as e:
            errors.append(f"Error fetching {url}: {str(e)[:100]}")
        except Exception as e:
            errors.append(f"Error parsing {url}: {str(e)[:100]}")

    # Sort by published date (newest first)
    all_entries.sort(key=lambda x: x['published'] or '', reverse=True)

    return {
        "entries": all_entries,
        "count": len(all_entries),
        "feeds_fetched": len(feed_urls),
        "hours_back": hours_back,
        "timestamp": datetime.now().isoformat(),
        "errors": errors if errors else None
    }


def main():
    parser = argparse.ArgumentParser(
        description='Fetch cybersecurity news from RSS feeds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--hours', '-H',
        type=int,
        default=24,
        help='Fetch entries from the last N hours (default: 24)'
    )
    parser.add_argument(
        '--feeds', '-f',
        nargs='*',
        help='RSS feed URLs to fetch (uses defaults if not specified)'
    )
    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    # Get feed URLs
    feed_urls = args.feeds if args.feeds else load_default_feeds()

    if not feed_urls:
        print(json.dumps({"error": "No feed URLs provided or found"}))
        sys.exit(1)

    # Fetch feeds
    result = fetch_rss_feeds(feed_urls, args.hours)

    # Output JSON
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
