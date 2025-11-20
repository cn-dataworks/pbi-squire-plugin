# Power BI Dashboard Analyzer Skill

**Created:** 2025-01-19

A Claude Code skill that analyzes existing Power BI dashboards and provides business-friendly summaries of pages, visuals, metrics, filters, and interactions.

## What This Skill Does

This skill takes a Power BI project (.pbip format) and generates a comprehensive markdown analysis report that:

1. **Summarizes each dashboard page** - What it shows, its purpose
2. **Describes all visuals** - Detailed descriptions in business language (e.g., "Clustered bar chart comparing sales across regions")
3. **Explains metrics** - Translates DAX formulas into plain English with dependency tracking
4. **Documents interactions** - Cross-filtering, drillthrough, tooltips, and navigation
5. **Lists filters** - Page-level, report-level, and visual-specific filters

## Output Preferences (As Specified)

- **Metric Explanations**: Business language + list of dependent measures (Option C)
- **Visual Descriptions**: Detailed (Option B) - includes axes, colors, data roles
- **Interactions**: Yes - documents cross-filtering, drillthrough, and tooltips
- **Report Format**: Markdown file saved in `agent_scratchpads` folder

## Example Triggers

The skill responds to requests like:

- "Tell me what this dashboard is doing and how the definitions of the metrics work"
- "I need help understanding this dashboard in specifics about what is contained in this page"
- "Help me figure out how this metric is created and what this graph is telling me"
- "Analyze the Sales Dashboard and explain each page"

## How It Works

### Workflow

1. **Project Validation** - Verifies .pbip structure (similar to `/evaluate-pbi-project-file`)
2. **Data Extraction** - Parses .Report folder for visuals and .SemanticModel for measures
3. **Business Translation** - Converts technical details to business-friendly language
4. **Report Generation** - Creates markdown analysis in `agent_scratchpads`

### Skill Contents

**Scripts:**
- `parse_pbir_pages.py` - Extracts page/visual structure from .Report folder
- `extract_measure_info.py` - Parses TMDL files for measure definitions
- `generate_dashboard_analysis.py` - Main orchestrator

**References:**
- `visual_types.md` - Power BI visual types in business language
- `dax_common_patterns.md` - DAX pattern translations
- `interaction_patterns.md` - Cross-filtering, drillthrough, tooltip patterns

**Assets:**
- `analysis_report_template.md` - Markdown report template

## Installation

The skill is packaged as `powerbi-dashboard-analyzer.skill` in the `.claude/skills` folder.

To install:
1. Copy `powerbi-dashboard-analyzer.skill` to your Claude Code skills directory
2. Restart Claude Code or reload skills
3. The skill will automatically trigger when you ask to analyze a dashboard

## Example Usage

```
User: "Analyze the dashboard at C:\Projects\SalesReport and tell me what it does"

Claude: [Invokes powerbi-dashboard-analyzer skill]
        - Validates project structure
        - Extracts pages, visuals, and measures
        - Generates business-friendly analysis report
        - Saves to agent_scratchpads/20250119-143000-dashboard-analysis/
```

## Output Example

The generated report includes:

### Dashboard Overview
"This Power BI dashboard contains 3 pages with 12 metrics defined across 5 tables..."

### Page 1: Executive Summary
**Visual 1: Total Revenue Card**
- Type: Card visual
- Purpose: Display current total revenue as a single KPI
- Shows: $2.4M
- Metric: Total Sales (excludes returns)

**Visual 2: YoY Growth Card**
- Type: KPI visual
- Purpose: Track year-over-year revenue growth
- Shows: +12.5%
- Metrics: YoY Growth % (depends on Total Sales, Prior Year Sales)

### Key Metrics Glossary

**Total Sales**
- Definition: Sum of all invoice amounts excluding returns and cancelled orders
- Dependencies: Sales[Amount] (column)
- Business Logic: Filters out Status = "Cancelled" or Return = TRUE

**YoY Growth %**
- Definition: Percentage increase/decrease in sales compared to same period last year
- Dependencies: Total Sales, Prior Year Sales
- Business Logic: (Current - Prior) / Prior, using SAMEPERIODLASTYEAR function

## Design Decisions

1. **Business-First Language** - Avoids DAX jargon, focuses on what metrics mean to business users
2. **Dependency Tracking** - Shows which measures depend on others (Option C preference)
3. **Detailed Visual Descriptions** - Includes axes, color coding, data roles (Option B preference)
4. **Full Interaction Documentation** - Cross-filtering, drillthrough, tooltips (Yes preference)
5. **Persistent Reports** - Saves to agent_scratchpads for reference

## Limitations

- Requires Power BI Project (.pbip) format with .Report folder for full page/visual analysis
- pbi-tools and model.bim formats only support data model analysis (no visual analysis)
- Custom visual types may require manual description enhancement
- Complex DAX patterns may need human review for business translation accuracy

## Next Steps

After creating the skill, it should be tested with real Power BI projects to:
1. Verify PBIR parsing accuracy
2. Refine DAX-to-business translations
3. Improve visual description quality
4. Add more interaction pattern recognition

## Files Included

```
powerbi-dashboard-analyzer/
├── SKILL.md (main skill instructions)
├── scripts/
│   ├── parse_pbir_pages.py
│   ├── extract_measure_info.py
│   └── generate_dashboard_analysis.py
├── references/
│   ├── visual_types.md
│   ├── dax_common_patterns.md
│   └── interaction_patterns.md
└── assets/
    └── analysis_report_template.md
```

## Packaged File

- **Location**: `.claude/skills/powerbi-dashboard-analyzer.skill`
- **Format**: Zip archive with .skill extension
- **Size**: ~100KB
