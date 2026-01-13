---
name: threat-report-generator
description: Generate formatted markdown threat reports from analyzed security content with metadata. Use when creating human-readable reports from JSON analysis outputs.
allowed-tools: Read, Write
---

# Threat Report Generator

Transforms structured security analysis data (JSON) into professional, human-readable markdown reports with accompanying metadata.

## When to Use This Skill

Use this skill when the user requests:
- Human-readable markdown reports from JSON analysis
- Distribution-ready threat briefings
- Formatted reports for stakeholders
- Conversion of structured JSON data to narrative format

This skill accepts JSON output from:
- `security-intelligence-analysis` skill (daily/weekly briefs)
- Custom security analysis JSON matching expected structure

The user typically asks:
- "Generate a report from the daily brief"
- "Create a markdown version of the analysis"
- "Format the briefing for distribution"

## Workflow

### Step 1: Load Templates

Read both templates:
```
Read('./templates/markdown-report.md.template')
Read('./templates/json-metadata.json')
```

### Step 2: Read Input JSON

Read the security analysis JSON file provided:
```
Read('[provided-json-path]')
```

Expected input structure (from security-intelligence-analysis):
```json
{
  "executive_summary": "...",
  "categories": {
    "critical_alerts": [...],
    "vulnerabilities": [...],
    "breaches_incidents": [...],
    "advisories": [...],
    "industry_news": [...]
  },
  "metadata": { ... }
}
```

Or weekly format:
```json
{
  "executive_summary": "...",
  "top_critical_items": [...],
  "trends": { ... },
  "metadata": { ... }
}
```

### Step 3: Generate Report Sections

For each category in the input, generate formatted markdown sections:

**Critical Alerts Section:**
```markdown
## Critical Alerts

### [Article Title]
**Source:** [Source Name] | **Severity:** [Level] | **Date:** [Date]

[Summary paragraph]

**Impact:** [Impact description]

**Affected Systems:** [Systems/vendors]

**Recommended Actions:**
- [Action 1]
- [Action 2]

**Reference:** [Link]

---
```

**Vulnerabilities Section:**
```markdown
## Vulnerabilities & CVEs

### [CVE-ID or Title]
**Severity:** [Level] (CVSS: [Score]) | **Source:** [Source]

[Description]

**Affected:** [Vendors/Products/Versions]

**Mitigation:** [Patches or workarounds]

**Reference:** [Link]

---
```

Apply similar formatting for:
- Breaches & Incidents
- Security Advisories
- Industry News

**For Weekly Reports:**

Include additional trends section:
```markdown
## Threat Trends

### Emerging Threats
- [Threat 1]: [Description]
- [Threat 2]: [Description]

### Persistent Vulnerabilities
- [Vuln 1]: [Description and status]

### Patches & Mitigations
- [Update 1]: [What was fixed]
```

### Step 4: Populate Template

Replace template placeholders with generated content:

- `{date}`: Report date (YYYY-MM-DD)
- `{report_type}`: "Daily Brief" or "Weekly Summary"
- `{timestamp}`: Full ISO 8601 timestamp
- `{executive_summary}`: From input JSON
- `{critical_alerts_section}`: Generated markdown
- `{vulnerabilities_section}`: Generated markdown
- `{breaches_section}`: Generated markdown
- `{advisories_section}`: Generated markdown
- `{industry_news_section}`: Generated markdown
- `{trends_section}`: Generated markdown (for weekly)
- `{recommendations_section}`: Top 3-5 action items
- `{total_items}`: Count from metadata
- `{critical_count}`: Count of critical severity items
- `{sources_list}`: Unique sources as bullet list
- `{coverage_period}`: Date range

### Step 5: Generate Metadata JSON

Populate the JSON metadata template:

```json
{
  "report_id": "report-[date]-[type]",
  "report_type": "daily|weekly",
  "generated_date": "2026-01-13T14:30:00Z",
  "coverage_period": {
    "start": "2026-01-12T14:30:00Z",
    "end": "2026-01-13T14:30:00Z"
  },
  "statistics": {
    "total_items": 25,
    "critical_count": 3,
    "high_count": 8,
    "medium_count": 10,
    "low_count": 4,
    "categories": {
      "critical_alerts": 3,
      "vulnerabilities": 8,
      "breaches_incidents": 5,
      "advisories": 4,
      "industry_news": 5
    }
  },
  "sources": ["Source A", "Source B", "Source C"],
  "top_threats": [
    "Threat 1 title",
    "Threat 2 title",
    "Threat 3 title"
  ],
  "keywords": ["ransomware", "zero-day", "data breach"],
  "metadata": {
    "generator": "cybersec-news-agent",
    "version": "1.0",
    "format": "markdown"
  }
}
```

### Step 6: Write Output Files

Write both the markdown report and JSON metadata:

**Markdown Report:**
```
/app/outputs/threat-report-[type]-YYYY-MM-DD.md
```

**JSON Metadata:**
```
/app/outputs/threat-report-[type]-YYYY-MM-DD-metadata.json
```

### Step 7: Validation

Verify outputs:

- ✅ Markdown file exists and is readable
- ✅ JSON metadata file exists with valid JSON
- ✅ All sections have content (or "No items" message)
- ✅ Links are properly formatted
- ✅ Severity levels are consistent
- ✅ Dates are formatted correctly
- ✅ Metadata statistics match content

## Formatting Guidelines

**Markdown Best Practices:**

1. **Headers:** Use consistent hierarchy (##, ###, ####)
2. **Links:** Always use markdown link format `[Text](URL)`
3. **Emphasis:** Use **bold** for important terms
4. **Lists:** Use `-` for unordered, `1.` for ordered
5. **Horizontal rules:** Use `---` to separate items
6. **Code blocks:** Use ` ``` ` for technical content
7. **Tables:** Use markdown tables for structured data

**Content Guidelines:**

1. **Executive Summary:** 3-5 sentences, cover key highlights
2. **Item Summaries:** 2-3 sentences, clear and concise
3. **Recommendations:** Actionable, specific, prioritized
4. **References:** Always include source links
5. **Severity:** Use consistent terminology (Critical/High/Medium/Low)

## Example Output Preview

Present summary to user:

```
✅ Threat Report Generated

Report: /app/outputs/threat-report-daily-2026-01-13.md
Metadata: /app/outputs/threat-report-daily-2026-01-13-metadata.json

Report Type: Daily Brief
Coverage: 2026-01-12 to 2026-01-13
Total Items: 25
Critical: 3 | High: 8 | Medium: 10 | Low: 4

Top Threats:
1. [First critical item title]
2. [Second critical item title]
3. [Third critical item title]

Report ready for distribution.
```

## Error Handling

- **Input JSON not found:** Display clear error with expected path
- **Invalid JSON structure:** Attempt to parse what's available, note issues
- **Missing categories:** Generate sections with "No items in this category"
- **Template not found:** Use basic formatting as fallback
- **Write permission issues:** Log error with specific path

## Notes

- Reports should be professional and distribution-ready
- Maintain consistent formatting across all report types
- Include all available context from input JSON
- Metadata enables automated report processing
- Reports can be emailed, posted, or archived
- Consider generating PDF in future iterations
