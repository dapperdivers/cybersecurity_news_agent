#!/usr/bin/env python3
"""
RSS Fetcher MCP Server
Provides tools to fetch and parse RSS/Atom feeds for cybersecurity news
"""

import json
import sys
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os


def fetch_rss_feeds(feed_urls: List[str], hours_back: int = 24) -> List[Dict[str, Any]]:
    """
    Fetch and parse RSS feeds, returning recent entries

    Args:
        feed_urls: List of RSS/Atom feed URLs
        hours_back: Only return entries from the last N hours (default: 24)

    Returns:
        List of feed entries with title, link, summary, and published date
    """
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    all_entries = []

    for url in feed_urls:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

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

                all_entries.append({
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': published.isoformat() if published else None,
                    'source': feed.feed.get('title', url)
                })

        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            continue

    # Sort by published date (newest first)
    all_entries.sort(key=lambda x: x['published'] or '', reverse=True)

    return all_entries


def load_default_feeds(config_path: str = None) -> List[str]:
    """Load default feed URLs from config file"""
    if config_path is None:
        config_path = os.environ.get('DEFAULT_FEEDS_PATH',
                                     '/app/mcp-servers/rss_fetcher/config/default_feeds.json')

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('feeds', [])
    except Exception as e:
        print(f"Error loading default feeds: {e}", file=sys.stderr)
        return []


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool calls"""

    if tool_name == "fetch_rss_feeds":
        feed_urls = arguments.get('feed_urls')
        hours_back = arguments.get('hours_back', 24)

        # If no URLs provided, use defaults
        if not feed_urls:
            feed_urls = load_default_feeds()

        if not feed_urls:
            return {
                "error": "No feed URLs provided and no default feeds configured"
            }

        entries = fetch_rss_feeds(feed_urls, hours_back)
        return {
            "entries": entries,
            "count": len(entries)
        }

    elif tool_name == "load_default_feeds":
        feeds = load_default_feeds()
        return {
            "feeds": feeds,
            "count": len(feeds)
        }

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def main():
    """MCP Server main loop - stdio protocol"""

    # Tools definition
    tools = [
        {
            "name": "fetch_rss_feeds",
            "description": "Fetch and parse RSS/Atom feeds, returning recent entries",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feed_urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of RSS/Atom feed URLs (optional, uses defaults if not provided)"
                    },
                    "hours_back": {
                        "type": "integer",
                        "description": "Only return entries from the last N hours (default: 24)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "load_default_feeds",
            "description": "Load the list of default RSS feed URLs",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]

    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())

            if request.get('method') == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "rss_fetcher",
                            "version": "1.0.0"
                        }
                    }
                }

            elif request.get('method') == 'tools/list':
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "tools": tools
                    }
                }

            elif request.get('method') == 'tools/call':
                params = request.get('params', {})
                tool_name = params.get('name')
                arguments = params.get('arguments', {})

                result = handle_tool_call(tool_name, arguments)

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }

            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            print(json.dumps(response), flush=True)

        except Exception as e:
            print(f"Error processing request: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
