---
name: security-intelligence-analysis
description: Analyze cybersecurity RSS feeds and generate structured intelligence reports. Use when the user requests daily or weekly threat briefings, security news summaries, or structured intelligence reports.
---

# Security Intelligence Analysis

Analyzes cybersecurity content from RSS feeds and generates structured JSON reports following strict templates.

## When to Use This Skill

Use this skill when the user requests:

- Daily cybersecurity news briefings
- Weekly security summaries
- Structured intelligence reports with consistent JSON output
- Threat reports or security digests

## Workflow

### Step 1: Determine Analysis Type

Determine the analysis type from the user's request. Default to daily analysis.

- **Daily**: Analyze last 24 hours (user asks for "today's news", "daily brief", etc.)
- **Weekly**: Analyze last 7 days (user asks for "weekly summary", "this week's threats", etc.)

### Step 2: Load Template

Read the appropriate template from the templates directory:

**For Daily:**
```bash
cat ./templates/daily-output.json
```

**For Weekly:**
```bash
cat ./templates/weekly-output.json
```

### Step 3: Fetch RSS Feeds

Run the feed fetcher script to collect recent articles:

**For Daily (24 hours):**
```bash
python3 ./scripts/fetch_feeds.py --hours 24
```

**For Weekly (168 hours = 7 days):**
```bash
python3 ./scripts/fetch_feeds.py --hours 168
```

The script outputs JSON with this structure:
```json
{
  "entries": [
    {
      "title": "Article title",
      "link": "https://...",
      "summary": "Article summary...",
      "published": "2026-01-27T10:00:00",
      "source": "Feed Name"
    }
  ],
  "count": 42,
  "feeds_fetched": 8,
  "hours_back": 24,
  "timestamp": "2026-01-27T16:00:00"
}
```

### Step 4: Analyze Content

For each article fetched, analyze it directly (no external API needed):

1. **Assess severity** based on content:
   - **critical**: Active zero-days, widespread attacks, critical infrastructure threats
   - **high**: Significant vulnerabilities, major breaches, APT activity
   - **medium**: Notable security news, patches, advisories
   - **low**: General industry news, research, tool releases

2. **Categorize** the article:
   - **critical_alerts**: Active threats, zero-days, widespread attacks
   - **vulnerabilities**: CVEs, security flaws, patches
   - **breaches_incidents**: Data breaches, security incidents
   - **advisories**: Security advisories, warnings
   - **industry_news**: General security news, tool releases

3. **Extract key information**:
   - Impact assessment
   - Affected systems/vendors
   - Recommended actions

4. **Filter out noise**: Remove marketing content, duplicates, low-value stories

### Step 5: Generate Analysis

**For Daily Analysis:**

1. Create 3-5 sentence executive summary highlighting most critical items
2. Populate each category with relevant articles
3. For each article include:
   - Title (clear, descriptive)
   - Source (publication name)
   - Date (ISO 8601 format)
   - Summary (2-3 sentences covering what happened)
   - Impact (who/what is affected)
   - Affected systems (specific vendors/products if mentioned)
   - Severity (critical/high/medium/low)
   - Recommended actions (what to do)
   - Link (original article URL)

4. Fill metadata:
   - total_articles: Count of all articles fetched
   - analyzed_count: Count of articles included in output
   - timestamp: Current time in ISO 8601
   - analysis_type: "daily"

**For Weekly Analysis:**

1. Create executive summary of the week's threat landscape
2. Identify top 5-7 most critical items from entire week
3. For each critical item:
   - Title
   - days_mentioned: How many days it appeared
   - Summary: Consolidated summary across mentions
   - Impact: Overall impact assessment
   - Trend: "emerging" (new threat), "persistent" (ongoing), "resolved" (patched/mitigated)
   - Recommended actions

4. Analyze trends:
   - emerging_threats: New threats that appeared this week
   - persistent_vulnerabilities: Ongoing issues mentioned multiple times
   - patches_mitigations: What got fixed or mitigated

5. Fill metadata:
   - reports_analyzed: Number of days analyzed (typically 7)
   - date_range: "YYYY-MM-DD to YYYY-MM-DD"
   - timestamp: Current time in ISO 8601

### Step 6: Write Output

Create the output file:

**For Daily:**
```
/app/outputs/daily-brief-YYYY-MM-DD.json
```
Or if running locally:
```
./outputs/daily-brief-YYYY-MM-DD.json
```

**For Weekly:**
```
/app/outputs/weekly-summary-YYYY-MM-DD.json
```

**CRITICAL OUTPUT REQUIREMENTS:**

1. **Pure JSON only** - No markdown code blocks, no wrappers
2. **Start with `{`** and end with `}`
3. **No explanatory text** before or after the JSON
4. **Match template structure exactly**
5. **Use ISO 8601 dates** throughout (YYYY-MM-DDTHH:MM:SSZ)
6. **All required fields must be present** even if empty arrays

### Step 7: Validation

Before considering the task complete, verify:

- Output file exists at expected path
- File contains valid JSON (no markdown wrappers)
- Structure matches the template
- Executive summary is present and informative
- Articles are properly categorized
- Severity levels are assigned
- Metadata is complete with accurate counts
- All timestamps are ISO 8601 format

## Example Output Preview

After writing the file, present a brief summary to the user:

```
Security Intelligence Analysis Complete

Type: [Daily/Weekly]
Output: /path/to/output/file.json

Executive Summary:
[First 2 sentences of the executive summary]

Critical Items: [count]
Total Articles Analyzed: [count]

Full analysis saved to output file.
```

## Script Reference

### fetch_feeds.py

Location: `./scripts/fetch_feeds.py`

**Arguments:**
- `--hours N` or `-H N`: Fetch entries from the last N hours (default: 24)
- `--feeds URL1 URL2...` or `-f`: Override default feeds with custom URLs
- `--pretty` or `-p`: Pretty-print JSON output

**Examples:**
```bash
# Default: last 24 hours from default feeds
python3 ./scripts/fetch_feeds.py

# Last 48 hours
python3 ./scripts/fetch_feeds.py --hours 48

# Weekly (7 days)
python3 ./scripts/fetch_feeds.py --hours 168

# Custom feeds
python3 ./scripts/fetch_feeds.py --feeds "https://example.com/feed"
```

### Configuration

Default feeds are configured in `./config/default_feeds.json`. Edit this file to add or remove RSS sources.

## Error Handling

If issues occur:

- **Script fails**: Check Python dependencies (feedparser, requests). Install with: `pip install feedparser requests`
- **No articles fetched**: Check internet connectivity, verify feed URLs are accessible
- **Template not found**: Ensure templates directory exists with daily-output.json and weekly-output.json
- **Invalid analysis type**: Default to daily analysis

## Notes

- This skill enforces strict output formatting for downstream automation
- Templates define the contract - never deviate from template structure
- Filtering and categorization should be conservative - when in doubt, include the item
- Weekly analysis should consolidate duplicate coverage across days
- Severity assessment should consider: exploit availability, affected user base, ease of exploitation
- No external API calls needed for text analysis - Claude analyzes content directly
