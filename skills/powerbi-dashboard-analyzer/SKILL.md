---
name: powerbi-dashboard-analyzer
description: "[DEPRECATED] This skill has been merged into powerbi-analyst. Use powerbi-analyst instead with the ANALYZE workflow."
---

# Power BI Dashboard Analyzer

> **⚠️ DEPRECATED:** This skill has been consolidated into `powerbi-analyst`.
>
> The `powerbi-analyst` skill now includes the **ANALYZE workflow** which provides:
> - Business-friendly dashboard documentation
> - Metrics glossary with plain-language explanations
> - Page-by-page analysis
> - Filter and interaction guide
>
> **Trigger the ANALYZE workflow by saying:**
> - "Explain what this dashboard does"
> - "Document this report for the business team"
> - "What does this page show?"
>
> **Please use `powerbi-analyst` instead.**

---

## Legacy Documentation (for reference)

Analyzes existing Power BI dashboards to provide clear, business-friendly summaries of what each page does, how metrics are defined, and how users interact with the dashboard.

## When to Use This Skill

This skill should be invoked when users want to **understand** an existing Power BI dashboard rather than **modify** it. Use for queries like:

- "Tell me what this dashboard is doing and how the definitions of the metrics work"
- "I need help understanding this dashboard and what is contained in this page"
- "Help me figure out how this metric is created and what this graph is telling me"
- "Explain the Sales page in business terms"
- "What filters are available on this report?"

**Do NOT use this skill for:**
- Fixing issues or bugs (use `/evaluate-pbi-project-file` instead)
- Creating new measures or visuals (use `/create-pbi-artifact` instead)
- Implementing changes (use `/implement-deploy-test-pbi-project-file` instead)

## Usage Pattern

```bash
Analyze the dashboard at: <path-to-pbip-folder>
```

The skill will create a timestamped analysis report in `agent_scratchpads/<timestamp>-dashboard-analysis/` containing business-friendly explanations of:
- Each page and its purpose
- Visuals on each page (detailed descriptions)
- Metrics and their definitions (with dependencies)
- Filters and slicers
- Page interactions (cross-filtering, drillthrough, tooltips)

## Workflow

### Phase 1: Project Validation

Verify the Power BI project structure using the same validation logic as `/evaluate-pbi-project-file`:

1. Check if the provided path is valid
2. Detect project format (Power BI Project .pbip, pbi-tools extracted, or model.bim)
3. Ensure required folders exist:
   - `.SemanticModel/definition/` - for measures and data model
   - `.Report/` - for pages and visuals (required for page analysis)

**If `.Report/` folder missing:** Inform user that page/visual analysis requires Power BI Project format with .Report folder. Only data model summary can be provided.

### Phase 2: Create Analysis Workspace

1. Generate timestamp: `YYYYMMDD-HHMMSS`
2. Create folder: `agent_scratchpads/<timestamp>-dashboard-analysis/`
3. Create report file: `dashboard_analysis.md` using template from `assets/analysis_report_template.md`

### Phase 3: Extract Dashboard Structure

Use bundled scripts to extract information:

**3.1 Extract Page and Visual Information**

Run `scripts/parse_pbir_pages.py` to extract from `.Report/` folder:
- Page names and order
- Visual types and positions on each page
- Visual data bindings (fields used)
- Page-level filters
- Visual-level filters

**3.2 Extract Measure Definitions**

Run `scripts/extract_measure_info.py` to parse TMDL files in `.SemanticModel/definition/`:
- All measures and their DAX formulas
- Calculated columns
- Measure dependencies (which measures reference which other measures)
- Tables and relationships

### Phase 4: Generate Business-Friendly Analysis

For each component, translate technical details into business language:

**4.1 Page Summaries**

For each page, write:
- Page name and purpose (inferred from visuals and naming)
- List of visuals with detailed descriptions (Option 3B: Detailed)
- Filters available on the page
- Interactions between visuals on the page

Example visual description format:
```
**Sales by Region Chart**
- Type: Clustered bar chart
- Purpose: Compare total sales across geographic regions
- Details: Region on Y-axis, Total Sales on X-axis, color-coded by Product Category
- Interactivity: Clicking a bar filters other visuals on the page
```

**4.2 Metric Explanations**

For each measure referenced in visuals, write:
- Business-friendly definition of what it calculates
- List of dependent measures it uses (Option 2C)
- Any important logic (filters, time intelligence, etc.)

Example measure explanation format:
```
**Year-over-Year Growth %**
- Definition: Shows the percentage increase or decrease in sales compared to the same period last year. Returns 0% if there were no sales in the prior year.
- Dependencies: Total Sales, Prior Year Sales
- Business Logic: Calculates the difference between current and prior year sales, divided by prior year sales. Uses DIVIDE function to handle zero denominators safely.
```

**4.3 Interaction Documentation**

Document how pages and visuals interact:
- Cross-filtering behavior (which visuals filter which others)
- Drillthrough paths (right-click navigation)
- Tooltips (hover behaviors with additional context)
- Page navigation (buttons, links between pages)

Consult `references/interaction_patterns.md` for common interaction patterns and how to describe them in business terms.

### Phase 5: Compile Final Report

Use `scripts/generate_dashboard_analysis.py` to orchestrate the full analysis and populate the markdown template with:

1. **Dashboard Overview** - High-level summary of what the dashboard does
2. **Page-by-Page Analysis** - Detailed breakdown of each page
3. **Key Metrics Glossary** - Business definitions of all important measures
4. **Filter & Interaction Guide** - How users navigate and filter the dashboard

### Phase 6: Present Results

Display to the user:
- Path to the generated analysis report
- High-level summary of findings (number of pages, key metrics, main purpose)
- Invitation to ask follow-up questions about specific pages or metrics

## Bundled Resources

### Scripts

- **`parse_pbir_pages.py`** - Extracts page structure, visual types, and layout from .Report folder JSON files
- **`extract_measure_info.py`** - Parses TMDL files to find measure definitions and dependencies
- **`generate_dashboard_analysis.py`** - Main orchestrator that combines all information into the final report

Usage examples provided within each script.

### References

Consult these references when generating business-friendly explanations:

- **`visual_types.md`** - Guide to Power BI visual types and how to describe them in business terms
- **`dax_common_patterns.md`** - Common DAX patterns and their business language translations
- **`interaction_patterns.md`** - Cross-filtering, drillthrough, and tooltip behaviors explained

These files help translate technical Power BI concepts into language that non-technical business users can understand.

### Assets

- **`analysis_report_template.md`** - Markdown template structure for the dashboard analysis report

## Translation Guidelines

When translating technical details to business language:

1. **Focus on "what" and "why", not "how"**
   - Good: "Total Sales excluding returns and discounts"
   - Avoid: "SUMX function iterating over filtered table context"

2. **Explain dependencies without overwhelming detail**
   - Good: "Depends on: Total Sales, Prior Year Sales"
   - Avoid: Full nested DAX code blocks

3. **Use business terminology**
   - Good: "Year-over-year comparison"
   - Avoid: "SAMEPERIODLASTYEAR time intelligence function"

4. **Describe visual purpose, not just visual type**
   - Good: "Line chart tracking monthly revenue trends over time"
   - Avoid: "Line chart with Date on X-axis and Revenue on Y-axis"

5. **Include just enough technical detail for credibility**
   - Show simplified code snippets when helpful
   - Reference specific table/column names when relevant
   - Note important logic (filters, conditions, time intelligence)

## Example Output Structure

```markdown
# Dashboard Analysis: Sales Performance Dashboard

**Created**: 2025-01-19 14:30:00
**Project**: C:\Projects\SalesReport

## Dashboard Overview

This dashboard provides sales leadership with real-time visibility into revenue performance, regional comparisons, and year-over-year growth trends. Users can filter by time period, region, and product category to analyze performance at different levels of granularity.

## Pages

### 1. Executive Summary

**Purpose**: High-level KPIs and trends for executive stakeholders

**Visuals**:
- **Total Revenue Card**: Displays current total revenue
  - Shows: $2.4M
  - Metric: Total Sales (excludes returns)

- **YoY Growth Card**: Year-over-year revenue growth percentage
  - Shows: +12.5%
  - Metric: YoY Growth %
  - Dependency: Total Sales, Prior Year Sales

[... more visuals ...]

**Filters**: Year, Quarter (affects all visuals on page)

**Interactions**: Clicking any region in the map cross-filters the trend chart

### 2. Regional Breakdown

[... continues ...]

## Key Metrics Glossary

### Total Sales
- **Definition**: Sum of all invoice amounts excluding returns and cancelled orders
- **Dependencies**: Sales Amount (column from Invoices table)
- **Business Logic**: Filters out records where Status = "Cancelled" or Return = TRUE

[... more metrics ...]

## Filter & Interaction Guide

[... interaction patterns ...]
```

## Error Handling

- **Project not found**: Report clear error with path validation
- **No .Report folder**: Explain that page/visual analysis requires .pbip format with .Report folder
- **Empty dashboard**: Report that no pages were found in the .Report folder
- **Measure parsing errors**: Note which measures couldn't be analyzed and continue with others
