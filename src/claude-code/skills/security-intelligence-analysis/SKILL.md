---
name: security-intelligence-analysis
description: Analyze cybersecurity RSS feeds and generate structured intelligence reports (daily or weekly). Use when you need consistent JSON output for security briefings.
allowed-tools: Read, Write, mcp__rss_fetcher__fetch_rss_feeds, mcp__text_analyzer__extract_key_points, mcp__text_analyzer__summarize_text
---

# Security Intelligence Analysis

Analyzes cybersecurity content from RSS feeds and generates structured JSON reports following strict templates.

## When to Use This Skill

Use this skill when the user requests:
- Daily cybersecurity news briefings
- Weekly security summaries
- Structured intelligence reports with consistent JSON output

## Workflow

### Step 1: Determine Analysis Type

Determine the analysis type from the user's request. Default to daily analysis.

- **Daily**: Analyze last 24 hours (user asks for "today's news", "daily brief", etc.)
- **Weekly**: Analyze last 7 days (user asks for "weekly summary", "this week's threats", etc.)

### Step 2: Load Template

Read the appropriate template from the templates directory:

**For Daily:**
```
Read('./templates/daily-output.json')
```

**For Weekly:**
```
Read('./templates/weekly-output.json')
```

### Step 3: Fetch RSS Feeds

Use the RSS fetcher MCP tool to collect recent articles:

**For Daily:**
```
mcp__rss_fetcher__fetch_rss_feeds(hours_back=24)
```

**For Weekly:**
```
mcp__rss_fetcher__fetch_rss_feeds(hours_back=168)
```

### Step 4: Analyze Content

For each article fetched:

1. **Extract key points** using `mcp__text_analyzer__extract_key_points`
2. **Assess severity** based on content (critical, high, medium, low)
3. **Categorize** the article:
   - **critical_alerts**: Active threats, zero-days, widespread attacks
   - **vulnerabilities**: CVEs, security flaws, patches
   - **breaches_incidents**: Data breaches, security incidents
   - **advisories**: Security advisories, warnings
   - **industry_news**: General security news, tool releases

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

Create the output file using the Write tool:

**For Daily:**
```
/app/outputs/daily-brief-YYYY-MM-DD.json
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

- ✅ Output file exists at expected path
- ✅ File contains valid JSON (no markdown wrappers)
- ✅ Structure matches the template
- ✅ Executive summary is present and informative
- ✅ Articles are properly categorized
- ✅ Severity levels are assigned
- ✅ Metadata is complete with accurate counts
- ✅ All timestamps are ISO 8601 format

## Example Output Preview

After writing the file, present a brief summary to the user:

```
✅ Security Intelligence Analysis Complete

Type: [Daily/Weekly]
Output: /app/outputs/[filename]

Executive Summary:
[First 2 sentences of the executive summary]

Critical Items: [count]
Total Articles Analyzed: [count]

Full analysis saved to output file.
```

## Error Handling

If issues occur:

- **No articles fetched**: Check RSS feeds are accessible, create output with empty categories
- **MCP tool fails**: Log error, attempt to continue with available data
- **Template not found**: Log clear error message with expected path
- **Invalid analysis type**: Default to daily analysis

## Notes

- This skill enforces strict output formatting for downstream automation
- Templates define the contract - never deviate from template structure
- Filtering and categorization should be conservative - when in doubt, include the item
- Weekly analysis should consolidate duplicate coverage across days
- Severity assessment should consider: exploit availability, affected user base, ease of exploitation
