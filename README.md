# Cybersecurity News Agent Container

A self-contained Docker container with Claude Code CLI, Python MCP servers, and pre-configured cybersecurity agents for news aggregation and analysis.

## Features

- **Claude Code CLI**: Official [@anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code) installed via npm
- **Node.js Runtime**: Node 20 (Bookworm Debian base)
- **Python Support**: Python 3 with data processing libraries (requests, feedparser, beautifulsoup4)
- **MCP Servers**: Custom Python tools for RSS feed fetching and text analysis
- **Pre-configured Agents**:
  - `news-aggregator`: Fetches and organizes cybersecurity news from RSS feeds
  - `security-analyst`: Analyzes and summarizes security content, CVEs, and threat reports
- **Pre-built Skills**:
  - `security-intelligence-analysis`: Structured JSON intelligence reports (daily/weekly)
  - `cve-deep-dive`: Detailed CVE analysis with IOC extraction
  - `threat-report-generator`: Markdown report generation from JSON analysis
- **Default Feeds**: 10+ curated cybersecurity news sources
- **Security**: Runs as non-root user by default

## Quick Start

### Prerequisites

- Docker installed
- Docker Compose installed (optional, but recommended for local development)
- Claude Code OAuth token (get from https://console.anthropic.com/)

### Option 1: Using Pre-built Image from GitHub Container Registry (Easiest)

Pull the latest pre-built image:

```bash
docker pull ghcr.io/dapperdivers/cybersecurity_news_agent:latest
```

Run it:

```bash
docker run -it \
  -e CLAUDE_CODE_OAUTH_TOKEN=your-token-here \
  -v $(pwd)/outputs:/app/outputs \
  ghcr.io/dapperdivers/cybersecurity_news_agent:latest
```

**Available tags:**
- `latest` - Latest build from main branch
- `v1.0.0` - Specific version releases
- `main-sha-abc123` - Specific commit builds

### Option 2: Using Docker Compose (Recommended for Local Development)

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
   # Build the container
   docker-compose build

   # Run interactively
   docker-compose run --rm cybersec-agent
   ```

**Benefits:**
- Automatically loads environment variables from `.env` file
- Mounts source directories for live code editing (no rebuild needed)
- Mounts `outputs/` directory for easy access to generated reports
- Proper user/group ID mapping (configurable via `USER_ID` and `GROUP_ID` in `.env`)

**Development workflow:**
- Edit files in `src/` locally
- Changes are immediately reflected in the container
- No need to rebuild after code changes
- Generated reports appear in `./outputs/`

**Common commands:**
```bash
# Start interactive shell
docker-compose run --rm cybersec-agent

# Rebuild after Dockerfile changes
docker-compose build

# View logs (if running as service)
docker-compose logs -f

# Clean up
docker-compose down
```

### Option 3: Building Locally

#### Build the Container

**Basic build:**
```bash
docker build -t cybersec-agent .
```

**Build with custom user/group IDs (recommended):**
```bash
docker build \
  --build-arg USER_ID=$(id -u) \
  --build-arg GROUP_ID=$(id -g) \
  -t cybersec-agent .
```

This matches the container user to your host user, preventing permission issues with volume mounts.

### Run Interactively

```bash
docker run -it \
  -e ANTHROPIC_API_KEY=your-api-key-here \
  -v $(pwd)/outputs:/app/outputs \
  cybersec-agent
```

**Note:** Container runs as non-root user `agent` (UID 1000 by default) for security.

### Using the Agents

Once inside the container, start Claude Code:

```bash
claude-code
```

Then invoke agents using the Task tool:

**Fetch today's cybersecurity news:**
```
Use the news-aggregator agent to fetch today's cybersecurity news
```

**Analyze a security article:**
```
Use the security-analyst agent to analyze [article/CVE/report]
```

## Directory Structure

### Project Structure (Local)

```
cybersecurity_news_agent/
├── src/                         # Source files for Docker image
│   ├── claude-code/             # Claude Code configuration
│   │   ├── agents/              # Sub-agent definitions
│   │   │   ├── news-aggregator.md
│   │   │   └── security-analyst.md
│   │   └── skills/              # Reusable workflows with templates
│   │       ├── security-intelligence-analysis/
│   │       │   ├── SKILL.md
│   │       │   └── templates/   # JSON output templates
│   │       ├── cve-deep-dive/
│   │       │   ├── SKILL.md
│   │       │   └── templates/   # CVE analysis templates
│   │       └── threat-report-generator/
│   │           ├── SKILL.md
│   │           └── templates/   # Markdown report templates
│   └── mcp-servers/             # Python MCP servers
│       ├── rss_fetcher/         # RSS feed fetching tools
│       └── text_analyzer/       # Text summarization tools
├── outputs/                     # Local outputs (mount as volume)
├── docs/                        # Documentation
├── Dockerfile                   # Container definition
└── README.md                    # This file
```

### Container Structure (Inside Docker)

```
/app/
├── mcp-servers/                 # Python MCP servers
│   ├── rss_fetcher/
│   └── text_analyzer/
└── outputs/                     # Report outputs (volume mount point)

/home/agent/                     # Non-root user home directory
└── .claude/
    ├── agents/                  # Agent definitions
    │   ├── news-aggregator.md
    │   └── security-analyst.md
    ├── skills/                  # Reusable workflows
    └── settings.json            # MCP server registration
```

**Security:** Container runs as non-root user `agent` (UID/GID 1000 by default) with sudo access for package installation if needed.

## Environment Variables

### Required

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude API access

### Optional

- `DEFAULT_FEEDS_PATH`: Path to custom feeds.json (default: `/app/mcp-servers/rss_fetcher/config/default_feeds.json`)
- `OUTPUT_DIR`: Output directory for reports (default: `/app/outputs`)

## MCP Tools Available

### RSS Fetcher Tools

**fetch_rss_feeds**
- Fetches and parses RSS/Atom feeds
- Parameters:
  - `feed_urls` (optional): List of feed URLs (uses defaults if not provided)
  - `hours_back` (optional): Hours of history to fetch (default: 24)

**load_default_feeds**
- Returns the list of configured default feeds

### Text Analyzer Tools

**summarize_text**
- Summarizes text content using Claude API
- Parameters:
  - `text` (required): Text to summarize
  - `style` (optional): "concise" (bullets) or "paragraph" (default: "concise")
  - `max_points` (optional): Max bullet points (default: 5)

**extract_key_points**
- Extracts key points with threat assessment
- Parameters:
  - `text` (required): Text to analyze
  - `num_points` (optional): Number of points to extract (default: 5)

## Skills

### security-intelligence-analysis

Analyzes cybersecurity RSS feeds and generates structured intelligence reports in JSON format.

**Output Modes:**
- Daily briefs (last 24 hours)
- Weekly summaries (last 7 days)

**Features:**
- Strict JSON schema enforcement
- Article categorization (critical alerts, vulnerabilities, breaches, advisories, industry news)
- Severity assessment
- Automated filtering and deduplication
- Template-driven output for consistent formatting

**Output Location:** `/app/outputs/daily-brief-YYYY-MM-DD.json` or `/app/outputs/weekly-summary-YYYY-MM-DD.json`

**Usage:** Invoked by the `news-aggregator` agent

### cve-deep-dive

Performs comprehensive CVE vulnerability analysis with IOC extraction.

**Output Formats:**
1. **Standard CVE Analysis** - Detailed analysis with CVSS scores, IOCs, affected systems, and mitigations
2. **Package Vulnerability Format** - GitHub package search compatible format for dependency scanning

**Features:**
- CVSS score extraction and severity assessment
- IOC extraction (IPs, domains, file hashes, indicators)
- Affected system identification
- Mitigation and patch documentation
- Exploitation status tracking
- Template-driven JSON output

**Output Location:** `/app/outputs/cve-analysis-[CVE-ID]-YYYY-MM-DD.json` or `/app/outputs/package-vulnerabilities-YYYY-MM-DD.json`

**Usage:** Invoked by the `security-analyst` agent

### threat-report-generator

Transforms structured security analysis JSON into professional markdown reports.

**Features:**
- Converts JSON analysis to human-readable markdown
- Generates accompanying metadata JSON
- Professional formatting with sections, tables, and links
- Distribution-ready output
- Supports both daily and weekly report formats

**Output Location:** `/app/outputs/threat-report-[type]-YYYY-MM-DD.md` and `/app/outputs/threat-report-[type]-YYYY-MM-DD-metadata.json`

**Usage:** Optionally invoked by either agent for stakeholder distribution

## Agents

### news-aggregator

Fetches cybersecurity news from RSS feeds and generates formatted reports.

**Capabilities:**
- Fetches from 10+ default security news sources
- Filters and categorizes articles
- Generates markdown reports with priority sections
- Saves outputs to `/app/outputs/news-YYYY-MM-DD.md`

**Example prompts:**
- "Fetch today's cybersecurity news"
- "Get the latest security articles from the past 12 hours"
- "Aggregate news from [specific feeds]"

### security-analyst

Analyzes and summarizes security content including CVEs, threat reports, and articles.

**Capabilities:**
- Summarizes complex security content
- Extracts key findings and threat levels
- Identifies affected systems and mitigations
- Formats analysis in structured reports

**Example prompts:**
- "Analyze this CVE article: [content or file path]"
- "Summarize this threat intelligence report"
- "Extract key points from this security advisory"

## Default RSS Feeds

The container comes pre-configured with feeds from:

- Krebs on Security
- Bleeping Computer
- The Hacker News
- CISA Alerts
- Schneier on Security
- Threatpost
- Dark Reading
- SecurityWeek
- Naked Security (Sophos)
- CSO Online

To customize feeds, either:
1. Modify `src/claude-code/config/default_feeds.json` before building, or
2. Mount a custom feeds.json file and set `DEFAULT_FEEDS_PATH`

## Customization

### Add More Feeds

Edit `src/claude-code/config/default_feeds.json`:

```json
{
  "feeds": [
    "https://your-feed-url.com/rss",
    "https://another-feed.com/atom.xml"
  ]
}
```

### Create Custom Agents

Add new agent definitions to `src/claude-code/agents/` directory:

```markdown
---
name: your-agent-name
description: What your agent does
model: sonnet
---

Your agent's system prompt and instructions...
```

### Add Custom Skills

The container comes with 3 pre-built skills. To add more reusable workflows, create new skill directories in `src/claude-code/skills/`:

```
src/claude-code/skills/your-skill-name/
├── SKILL.md                    # Skill instructions
└── templates/                  # Optional templates
    └── your-template.json
```

Skills are automatically available to all agents once the container is rebuilt.

### Extend MCP Servers

Add new Python MCP servers in `src/mcp-servers/` and register them in `src/claude-code/.mcp.json`.

## Volume Mounts

**Recommended mounts:**

```bash
docker run -it \
  -e ANTHROPIC_API_KEY=your-key \
  -v $(pwd)/outputs:/app/outputs \           # Persist reports
  -v $(pwd)/custom-feeds.json:/app/mcp-servers/rss_fetcher/config/default_feeds.json \  # Custom feeds
  -v $(pwd)/custom-agents:/root/.claude/agents \  # Custom agents
  cybersec-agent
```

## Development

### Testing MCP Servers Locally

You can test MCP servers before building the container:

```bash
# Test RSS fetcher
cd src/mcp-servers/rss_fetcher
python3 server.py

# Test text analyzer (requires ANTHROPIC_API_KEY)
cd src/mcp-servers/text_analyzer
export ANTHROPIC_API_KEY=your-key
python3 server.py
```

### Building with Custom Node.js Version

If you need a different Node.js version:

```dockerfile
FROM node:18-bookworm-slim  # Use Node 18 instead of 20
# ... rest of Dockerfile
```

## Troubleshooting

**MCP servers not working:**
- Check that `ANTHROPIC_API_KEY` is set for text_analyzer
- Verify Python scripts have execute permissions
- Check logs: `tail -f /var/log/mcp-server.log`

**Agents not found:**
- Verify `.md` files are in `/home/agent/.claude/agents/`
- Check YAML frontmatter format is correct
- Restart Claude Code CLI

**No news articles returned:**
- RSS feeds may be down or changed URLs
- Check network connectivity
- Verify feed URLs in default_feeds.json

**Permission errors on outputs:**
- Build with matching user IDs: `--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)`
- Ensure the mounted volume directory exists and is writable by your user
- Check ownership: `ls -la outputs/`

**Container runs as root despite USER directive:**
- Some orchestration systems override USER - check your docker-compose or k8s config
- Verify with: `docker run -it cybersec-agent whoami` (should output: agent)

## Contributing

Feel free to:
- Add more cybersecurity RSS feeds
- Create new specialized agents
- Enhance MCP server capabilities
- Improve documentation

## License

This project is open source. Components used:
- Base image: Node.js official Docker image (MIT License)
- Claude Code CLI: [@anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code) (Anthropic)

## Credits

- Built with [Claude Code CLI](https://code.claude.com/docs) - Official CLI from Anthropic
- Powered by [Claude](https://www.anthropic.com/claude) from Anthropic
- Uses [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Claude API Documentation](https://docs.anthropic.com/)
