---
name: analyze-pbi-dashboard
description: Analyze existing Power BI dashboard pages and provide business-friendly summaries of visuals, metrics, filters, and page interactions
pattern: ^/analyze-pbi-dashboard\s+(.+)$
---

# Analyze Power BI Dashboard

This slash command creates comprehensive business-friendly documentation for existing Power BI dashboards by:
1. Validating the Power BI project structure
2. Discovering all report pages and visuals
3. Analyzing DAX measures, filters, and visual configurations
4. Synthesizing technical details into clear, business-facing summaries

## Usage

```bash
/analyze-pbi-dashboard --project <path-to-pbip-folder> [--output <output-file-path>]
```

### Parameters

- `--project` (required): Path to the Power BI Project folder (the folder containing the .pbip file structure)
- `--output` (optional): Path to save the analysis markdown file. Defaults to `dashboard_analysis.md` in the current directory

### Examples

```bash
# Basic usage - analyze dashboard and create report
/analyze-pbi-dashboard --project "C:\Projects\SalesReport"

# Specify custom output location
/analyze-pbi-dashboard --project "./MyReport" --output "./docs/dashboard-overview.md"

# Analyze dashboard with both .Report and .SemanticModel
/analyze-pbi-dashboard --project "C:\Reports\FinanceDashboard.Report"
```

## Workflow

### Phase 1: Project Validation & Setup

This phase validates the Power BI project structure, using the `powerbi-verify-pbiproject-folder-setup` agent.

**Step 1: Parse Arguments and Create Workspace**

1. Parse command arguments:
   - `--project`: Project path (required)
   - `--output`: Output file path (optional, defaults to `dashboard_analysis.md`)

2. Generate timestamp: `YYYYMMDD-HHMMSS` format

3. Create analysis workspace folder: `agent_scratchpads/<timestamp>-dashboard-analysis/`

4. Create empty analysis file with Dashboard Analysis header

**Step 2: Invoke Verification Agent**

Invoke the `powerbi-verify-pbiproject-folder-setup` agent:
```
project_path: <from --project argument>
findings_file_path: <workspace-path>/analysis.md
user_action: none
visual_changes_expected: false
```

**Step 3: Read Prerequisites Section**

After agent returns, read the Prerequisites section from analysis.md and parse these fields:
- `Status`: One of `validated`, `action_required`, `error`
- `validated_project_path`: Path to use for analysis (if status=validated)
- `format`: Project format type (if status=validated)
- `requires_compilation`: Boolean (if status=validated)

**Step 4: Branch Based on Status**

**If Status = validated:**
- Extract `validated_project_path` from Prerequisites
- Display success message with project format
- Continue to Phase 2 (page discovery)

**If Status = action_required:**
- Handle PBIX extraction or pbi-tools installation as needed
- Follow same logic as evaluate-pbi-project-file command
- Exit workflow if user chooses manual conversion

**If Status = error:**
- Display error message to user
- Exit workflow with error code 1

---

### Phase 2: Page and Visual Discovery

**Purpose**: Identify all report pages and catalog visuals on each page

**Step 1: Locate Report Definition**

1. Check project format from Prerequisites:
   - If format includes .Report folder: Use validated_project_path/.Report/
   - If format is pbi-tools or pbix-extracted-pbitools: Look for report.json or equivalent
   - If no report structure found: Display message and exit (semantic model only, no visuals to analyze)

2. Locate the report definition file:
   - Power BI Project format: Look for `definition.pbir` in .Report folder
   - pbi-tools format: Look for `Report/` folder structure

**Step 2: Discover Pages**

1. Read report definition to extract page list:
   - Power BI Project: Parse definition.pbir for page sections
   - pbi-tools: Read Report/pages/ directory

2. For each page discovered, extract:
   - Page name / display name
   - Page GUID or identifier
   - Path to page definition file

3. Create page inventory in analysis file:
   ```markdown
   ## Pages Discovered

   | Page Name | Page ID | Path |
   |-----------|---------|------|
   | Sales Overview | abc123 | .Report/definition/pages/abc123/page.json |
   | Regional Performance | def456 | .Report/definition/pages/def456/page.json |
   ```

**Step 3: Catalog Visuals per Page**

For each page:

1. Read page definition file (page.json or equivalent)

2. Extract all visuals on the page:
   - Visual name / title
   - Visual type (bar chart, line chart, table, card, slicer, etc.)
   - Visual position (x, y coordinates)
   - Visual size (width, height)
   - Data bindings (fields, measures used)
   - Filters applied to the visual

3. Create visual inventory:
   ```markdown
   ### Page: Sales Overview

   | Visual Title | Type | Position | Size | Fields Used |
   |--------------|------|----------|------|-------------|
   | Total Revenue | Card | (100,50) | 200x150 | [Total Revenue] |
   | Sales by Region | Bar Chart | (350,50) | 500x300 | Region, [Total Sales] |
   ```

---

### Phase 3: Measure and Filter Analysis

**Purpose**: Analyze DAX measures referenced by visuals and identify filter logic

**Step 1: Invoke Dashboard Analysis Agent**

Invoke a new specialized agent: `powerbi-dashboard-analysis-agent`

**Agent Input**:
- Project path (validated_project_path)
- Analysis file path
- Page inventory (from Phase 2)
- Visual inventory (from Phase 2)

**Agent Tasks**:

1. **Measure Analysis**:
   - For each measure referenced in visuals:
     - Locate measure definition in .SemanticModel/definition/tables/
     - Read DAX expression
     - Identify:
       - Base tables referenced
       - Columns used
       - Functions used (SUM, CALCULATE, FILTER, etc.)
       - Time intelligence patterns (YoY, MTD, YTD, etc.)
       - Conditional logic (IF, SWITCH, etc.)

2. **Filter Analysis**:
   - For each visual, identify filters:
     - Visual-level filters
     - Page-level filters
     - Report-level filters (from definition.pbir)
   - Document filter conditions and columns

3. **Interaction Analysis**:
   - Identify slicers on each page
   - Document which visuals are affected by which slicers
   - Identify any cross-page filters or drill-through actions

**Agent Output** (appends to analysis.md):

```markdown
## Section 1: Technical Analysis

### Measures Referenced

#### [Total Revenue]
**Definition**:
```dax
Total Revenue = SUM(Sales[Revenue])
```

**Business Logic**:
- Sums the Revenue column from the Sales table
- No filters or conditions applied
- Affected by all slicers and filters in context

**Referenced By**:
- Sales Overview > Total Revenue (Card)
- Regional Performance > Revenue Trend (Line Chart)

---

#### [YoY Revenue Growth %]
**Definition**:
```dax
YoY Revenue Growth % =
VAR CurrentRevenue = [Total Revenue]
VAR PriorRevenue = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Calendar[Date]))
RETURN DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)
```

**Business Logic**:
- Compares current period revenue to same period last year
- Uses Calendar table for time intelligence
- Returns percentage change
- Returns 0 if prior period has no revenue (avoids division by zero)

**Referenced By**:
- Sales Overview > YoY Growth (Card)

---

### Page-Level Filters

#### Sales Overview
- **Date Filter**: Date >= 2023-01-01
- **Region Filter**: Region in ("North America", "Europe")

#### Regional Performance
- **No page-level filters applied**

---

### Slicers and Interactions

#### Sales Overview Page

**Slicer: Date Range**
- Field: Calendar[Year-Month]
- Type: Dropdown
- Affects: All visuals on page

**Slicer: Product Category**
- Field: Products[Category]
- Type: Tile
- Affects: Sales by Region, Product Performance Table
- Does NOT affect: Total Revenue Card (interaction disabled)

```

---

### Phase 4: Business-Friendly Synthesis

**Purpose**: Translate technical details into clear, business-facing language

**Step 1: Invoke Business Summary Agent**

Invoke a second specialized agent: `powerbi-business-summary-agent`

**Agent Input**:
- Analysis file (with Section 1 completed)
- Page inventory
- Visual inventory
- Measure analysis

**Agent Tasks**:

1. **Page Purpose Summaries**:
   - For each page, write 2-3 paragraph summary describing:
     - What business questions the page answers
     - What metrics are displayed
     - What interactions are available to users
   - Use simple language, avoid technical terms
   - Focus on business outcomes, not technical implementation

2. **Metric Definitions**:
   - For each measure, create business-friendly definition:
     - What the metric represents in business terms
     - How it's calculated (conceptually, not DAX)
     - When to use this metric
     - Any caveats or edge cases

3. **User Guide Content**:
   - How to use filters and slicers
   - How to interpret the visuals
   - What interactions are available (drill-through, cross-filtering, etc.)

**Agent Output** (appends to analysis.md):

```markdown
## Section 2: Business-Friendly Dashboard Overview

### Executive Summary

This dashboard provides a comprehensive view of sales performance across regions and time periods. Users can track total revenue, compare year-over-year growth, and analyze sales trends by product category and region.

---

### Pages

#### Sales Overview

**Purpose**: Provides a high-level snapshot of current sales performance and growth trends.

**What You'll See**:
- **Total Revenue**: The sum of all sales revenue for the selected time period. This updates automatically based on your date filter selections.
- **Year-over-Year Growth**: Shows how revenue has changed compared to the same period last year, expressed as a percentage. For example, 15% means revenue is 15% higher than last year.
- **Sales by Region**: A bar chart comparing revenue across different geographic regions, making it easy to identify top-performing markets.

**How to Use**:
- Use the Date Range slicer to focus on specific months or years
- Select a Product Category to filter all visuals to that category
- Note: The Total Revenue card always shows all categories, even when a category filter is applied

**Key Insights Available**:
- Which regions are driving the most revenue
- Whether sales are growing or declining compared to last year
- Seasonal trends in sales performance

---

#### Regional Performance

**Purpose**: Deep dive into geographic sales patterns and regional comparisons.

**What You'll See**:
- **Revenue by Country**: Detailed breakdown of sales within each region
- **Growth Trends**: Line charts showing how each region's performance has changed over time
- **Market Share**: Pie chart showing what percentage of total revenue each region contributes

**How to Use**:
- This page inherits any date filters from other pages
- Click on a region in the bar chart to filter other visuals to that region
- Use the drill-through option (right-click on a region) to see product-level details for that market

---

### Metrics Explained

#### Total Revenue

**What It Means**: The total amount of money generated from all sales transactions.

**How It's Calculated**: We add up the revenue from every sale in the selected time period. This includes all product categories and all regions unless filters are applied.

**When to Use**: Use this metric to track overall business performance and to compare total sales across different time periods or market segments.

**Important Notes**:
- This metric updates automatically when you apply filters
- Currency is displayed in USD
- Excludes returns and refunds (those are tracked separately)

---

#### Year-over-Year Revenue Growth %

**What It Means**: How much revenue has increased or decreased compared to the same period last year.

**How It's Calculated**: We compare revenue in the selected period to revenue from the exact same period one year ago, then express the difference as a percentage. For example, if last year's Q1 revenue was $100K and this year's Q1 revenue is $115K, the growth is 15%.

**When to Use**: Use this metric to understand whether your business is growing, staying flat, or declining. It's especially useful for identifying trends and setting performance expectations.

**Important Notes**:
- This metric requires at least one full year of historical data to calculate
- If there was no revenue in the prior year period, the metric shows as 0%
- Seasonal businesses should compare similar seasons (e.g., Q4 to Q4) for meaningful insights

---

### Filters and Interactions

#### Date Range Filter

**Purpose**: Lets you focus on specific time periods (months, quarters, or years).

**How to Use**: Click the dropdown and select the date range you want to analyze. The dashboard will automatically update all metrics and visuals to show only data from that period.

**Available Everywhere**: This filter affects all pages in the dashboard.

---

#### Product Category Slicer

**Purpose**: Allows you to analyze performance for specific product lines.

**How to Use**: Click on one or more categories to filter the dashboard. To see all categories again, click "Clear Filters" or deselect all options.

**Note**: The Total Revenue card on the Sales Overview page always shows all categories to provide context.

```

---

### Phase 5: Output Generation

**Step 1: Compile Final Report**

1. Combine all sections into final analysis markdown file
2. Add table of contents
3. Add metadata (analysis date, project path, analyst info)
4. Include section for technical appendix with full DAX code

**Final Report Structure**:

```markdown
# Power BI Dashboard Analysis Report

**Dashboard**: Sales Performance Dashboard
**Analyzed**: 2025-11-19 10:30 AM
**Project Path**: C:\Projects\SalesReport
**Format**: Power BI Project (.pbip)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Pages](#pages)
   - [Sales Overview](#sales-overview)
   - [Regional Performance](#regional-performance)
3. [Metrics Explained](#metrics-explained)
4. [Filters and Interactions](#filters-and-interactions)
5. [Technical Appendix](#technical-appendix)

---

[... Business-friendly content from Section 2 ...]

---

## Technical Appendix

This section contains detailed technical information for Power BI developers and analysts.

### DAX Measures

[... Complete DAX code from Section 1 ...]

### Page Configuration

[... Technical details about page layout, visual IDs, etc. ...]

### Data Model

[... Information about tables, relationships, columns ...]

```

**Step 2: Save to Output Location**

1. Copy compiled report to user-specified output path (or default location)
2. Display success message with clickable link to file

**Step 3: Display Summary**

```
✅ Dashboard Analysis Complete

📊 Pages Analyzed: 3
📈 Metrics Documented: 12
🎛️ Filters Identified: 8

📄 Report saved to: C:\Projects\SalesReport\dashboard_analysis.md

This report provides:
- Business-friendly explanations of all dashboard pages
- Metric definitions in plain language
- User guide for filters and interactions
- Technical appendix with DAX code and configuration details
```

---

## Error Handling

- **Project not found**: "Error: Power BI project folder not found at '<path>'. Please verify the path points to a valid .pbip project directory."
- **No report structure**: "Info: This project contains only a semantic model (no .Report folder). There are no visuals to analyze. Use /evaluate-pbi-project-file to analyze measures and data model."
- **Invalid project structure**: "Error: The specified folder does not appear to be a valid Power BI project (missing .SemanticModel or definition folders)."
- **Output path not writable**: "Error: Cannot write to output path '<path>'. Please check permissions or specify a different location."
- **Agent failure**: Report which agent failed and why, preserve partial analysis file

---

## Key Differences from Evaluation Workflow

This analysis workflow differs from `/evaluate-pbi-project-file`:

1. **No Problem Statement**: This is exploratory documentation, not problem-solving
2. **No Data Context Retrieval**: We analyze structure and definitions, not actual data
3. **No Proposed Changes**: Read-only analysis, no Section 2 with modifications
4. **Business Focus**: Output is optimized for business users, not technical implementation
5. **Comprehensive Coverage**: Analyzes ALL pages and visuals, not just objects related to a specific issue
6. **Two-Phase Synthesis**: Technical analysis followed by business translation

---

## Output Structure

The generated analysis file follows this structure:

```markdown
# Power BI Dashboard Analysis Report

**Created**: <Timestamp>
**Project**: <Project Path>
**Pages**: <Count>
**Measures**: <Count>

---

## Prerequisites

[Project validation details from powerbi-verify-pbiproject-folder-setup]

---

## Page Inventory

[Table of pages with names, IDs, and visual counts]

---

## Section 1: Technical Analysis

[Detailed DAX measures, filters, visual configurations - for developers]

---

## Section 2: Business-Friendly Dashboard Overview

[Plain-language explanations and user guide - for business users]

---

## Technical Appendix

[Complete DAX code, page configurations, data model details]
```

## Notes

- This command is designed for comprehensive dashboard documentation
- For troubleshooting specific issues, use `/evaluate-pbi-project-file` instead
- For creating new artifacts, use `/create-pbi-artifact`
- The analysis preserves full technical details while creating business-accessible summaries
- Output is designed to serve both technical and non-technical audiences
