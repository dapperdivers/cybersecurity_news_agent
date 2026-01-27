# Cybersecurity News Agent

A Claude Code-based cybersecurity news aggregation and analysis system using skill-based architecture with progressive loading.

## Features

- **Skill-Based Architecture**: Uses Claude Code Skills with Level 3 resources (scripts loaded as needed)
- **Claude Code CLI**: Official [@anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code)
- **Python Scripts**: RSS feed fetching via bash-executable scripts
- **Pre-configured Agents**:
  - `news-aggregator`: Fetches and organizes cybersecurity news from RSS feeds
  - `security-analyst`: Analyzes and summarizes security content, CVEs, and threat reports
- **Pre-built Skills**:
  - `security-intelligence-analysis`: Structured JSON intelligence reports (daily/weekly)
  - `cve-deep-dive`: Detailed CVE analysis with IOC extraction
  - `threat-report-generator`: Markdown report generation from JSON analysis
- **Default Feeds**: 8+ curated cybersecurity news sources

## Quick Start

### Prerequisites

- Python 3 with `feedparser` and `requests` packages
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- OR Docker (optional, for containerized usage)

### Option 1: Run Locally (Recommended)

1. **Install dependencies:**
   ```bash
   pip install feedparser requests
   ```

2. **Start Claude Code:**
   ```bash
   cd cybersecurity_news_agent
   claude
   ```

3. **Generate a threat report:**
   ```
   Create a daily threat report
   ```

   Claude will automatically:
   - Load the `security-intelligence-analysis` skill
   - Run `scripts/fetch_feeds.py` to fetch RSS feeds
   - Analyze and categorize articles
   - Generate JSON and markdown reports

### Option 2: Using Docker

**Setup:**
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Claude Code OAuth token:
   ```bash
   CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-your-token-here
   ```

3. Build and run:
   ```bash
   docker-compose build
   docker-compose run --rm cybersec-agent
   ```

## Directory Structure

```
cybersecurity_news_agent/
├── src/claude-code/
│   ├── agents/                    # Sub-agent definitions
│   │   ├── news-aggregator.md
│   │   └── security-analyst.md
│   ├── skills/                    # Reusable workflows
│   │   ├── security-intelligence-analysis/
│   │   │   ├── SKILL.md           # Skill instructions (Level 2)
│   │   │   ├── scripts/           # Executable scripts (Level 3)
│   │   │   │   └── fetch_feeds.py
│   │   │   ├── config/
│   │   │   │   └── default_feeds.json
│   │   │   └── templates/
│   │   │       ├── daily-output.json
│   │   │       └── weekly-output.json
│   │   ├── cve-deep-dive/
│   │   └── threat-report-generator/
│   └── .mcp.json                  # MCP config (empty - using skills)
├── outputs/                       # Generated reports
├── Dockerfile                     # Optional container
└── docker-compose.yml
```

## Skills

### security-intelligence-analysis

Analyzes cybersecurity RSS feeds and generates structured intelligence reports.

**How it works:**
1. Claude reads `SKILL.md` when triggered (Level 2 - instructions)
2. Claude runs `python3 scripts/fetch_feeds.py` via bash (Level 3 - script)
3. Claude analyzes the JSON output directly (no external API needed)
4. Claude writes structured reports to `outputs/`

**Output Modes:**
- Daily briefs (last 24 hours)
- Weekly summaries (last 7 days)

**Output Location:** `outputs/daily-brief-YYYY-MM-DD.json`

### cve-deep-dive

Performs comprehensive CVE vulnerability analysis with IOC extraction.

**Output Formats:**
1. Standard CVE Analysis - CVSS scores, IOCs, mitigations
2. Package Vulnerability Format - For dependency scanning

### threat-report-generator

Transforms JSON analysis into professional markdown reports.

## RSS Feed Script

The `fetch_feeds.py` script fetches RSS feeds and outputs JSON:

```bash
# Fetch last 24 hours (default)
python3 scripts/fetch_feeds.py

# Fetch last 48 hours
python3 scripts/fetch_feeds.py --hours 48

# Fetch last 7 days (weekly)
python3 scripts/fetch_feeds.py --hours 168

# Pretty-print output
python3 scripts/fetch_feeds.py --pretty
```

**Output format:**
```json
{
  "entries": [
    {
      "title": "Article title",
      "link": "https://...",
      "summary": "...",
      "published": "2026-01-27T10:00:00",
      "source": "Feed Name"
    }
  ],
  "count": 42,
  "feeds_fetched": 8,
  "hours_back": 24
}
```

## Default RSS Feeds

Configured in `src/claude-code/skills/security-intelligence-analysis/config/default_feeds.json`:

- Krebs on Security
- Bleeping Computer
- The Hacker News
- CISA Advisories
- Schneier on Security
- Dark Reading
- SecurityWeek
- Naked Security (Sophos)

## Customization

### Add More Feeds

Edit `src/claude-code/skills/security-intelligence-analysis/config/default_feeds.json`:

```json
{
  "feeds": [
    "https://your-feed-url.com/rss",
    "https://another-feed.com/atom.xml"
  ]
}
```

### Create Custom Skills

Add new skill directories in `src/claude-code/skills/`:

```
src/claude-code/skills/your-skill-name/
├── SKILL.md                    # Instructions
├── scripts/                    # Executable scripts
│   └── your-script.py
└── templates/                  # Output templates
    └── your-template.json
```

## Architecture

This project uses **Level 3 Skills** from the Claude Code skill architecture:

| Level | When Loaded | Content |
|-------|-------------|---------|
| Level 1 | Always (startup) | Skill `name` and `description` in YAML frontmatter |
| Level 2 | When triggered | SKILL.md body with instructions |
| Level 3 | As needed | Scripts, templates, config files |

**Benefits over MCP servers:**
- No daemon processes to manage
- Scripts run on-demand via bash
- Claude analyzes content directly (no redundant API calls)
- Simpler deployment and debugging

## Troubleshooting

**Script fails to run:**
- Check Python dependencies: `pip install feedparser requests`
- Verify script is executable: `chmod +x scripts/fetch_feeds.py`

**No articles returned:**
- RSS feeds may be down or URLs changed
- Check network connectivity
- Verify feed URLs in `config/default_feeds.json`

**Permission errors on outputs:**
- Ensure `outputs/` directory exists and is writable
- Check ownership: `ls -la outputs/`

## License

This project is open source.

## Credits

- Built with [Claude Code CLI](https://code.claude.com/docs)
- Powered by [Claude](https://www.anthropic.com/claude) from Anthropic
