# Power BI Visual Types - Business Language Guide

This reference helps translate Power BI visual types into business-friendly descriptions.

## Common Visual Types

### Card Visuals

**Technical**: `card`, `multiRowCard`

**Business Description Pattern**:
"[Metric name] card displaying [what it shows] as a single value"

**Examples**:
- "Total Revenue card showing current month's revenue as $2.4M"
- "Active Customers card displaying the count of customers with orders in the last 90 days"

**Key Details to Include**:
- The specific metric being displayed
- What the number represents in business terms
- Time context if relevant (current month, YTD, etc.)

---

### Bar and Column Charts

**Technical**: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`

**Business Description Pattern**:
"[Clustered/Stacked] [bar/column] chart comparing [metric] across [dimension]"

**Examples**:
- "Clustered bar chart comparing total sales across geographic regions, with each region showing sales broken down by product category"
- "Stacked column chart showing monthly revenue composition by product line over the past 12 months"

**Key Details to Include**:
- Orientation (horizontal bars vs vertical columns)
- Whether clustered (side-by-side) or stacked
- What's being measured (Y-axis or X-axis)
- What's being compared (categories)
- Color coding if meaningful (e.g., by subcategory)

---

### Line Charts

**Technical**: `lineChart`, `areaChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`

**Business Description Pattern**:
"Line chart tracking [metric] over [time period]"

**Examples**:
- "Line chart tracking daily website traffic over the past 30 days, with separate lines for mobile and desktop users"
- "Area chart showing cumulative revenue growth over the fiscal year"
- "Combo chart combining monthly sales columns with a rolling 3-month average trend line"

**Key Details to Include**:
- Time granularity (daily, monthly, yearly)
- Time range shown
- Multiple lines if present (what each represents)
- Trend insight if obvious (growing, declining, seasonal)

---

### Pie and Donut Charts

**Technical**: `pieChart`, `donutChart`

**Business Description Pattern**:
"[Pie/Donut] chart showing the distribution of [metric] by [category]"

**Examples**:
- "Pie chart showing the percentage breakdown of revenue by product category"
- "Donut chart displaying market share distribution among top 5 competitors"

**Key Details to Include**:
- What total is being divided (revenue, count, etc.)
- Categories in the breakdown
- Note if showing percentages or absolute values

---

### Tables and Matrices

**Technical**: `tableEx`, `pivotTable`, `matrix`

**Business Description Pattern**:
"[Table/Matrix] showing [rows] with columns for [metrics]"

**Examples**:
- "Table listing all customers with columns for Customer Name, Total Purchases, Last Order Date, and Lifetime Value"
- "Matrix showing sales by Region (rows) and Product Category (columns), with subtotals and grand totals"

**Key Details to Include**:
- What each row represents
- Key columns and what they show
- Whether it includes totals/subtotals
- Any conditional formatting (e.g., highlighting high values)

---

### Maps

**Technical**: `map`, `filledMap`, `azureMap`, `shapeMap`

**Business Description Pattern**:
"Map visualizing [metric] by [geographic dimension]"

**Examples**:
- "Filled map showing total sales by state, with darker colors indicating higher revenue"
- "Bubble map displaying store locations sized by annual revenue"

**Key Details to Include**:
- Geographic level (country, state, city, custom regions)
- What the visual encoding represents (color intensity, bubble size, etc.)
- The metric being visualized

---

### Scatter and Bubble Charts

**Technical**: `scatterChart`, `bubbleChart`

**Business Description Pattern**:
"Scatter chart comparing [X metric] vs [Y metric] across [entities]"

**Examples**:
- "Scatter chart comparing Customer Lifetime Value (X-axis) against Customer Age (Y-axis) with each dot representing one customer"
- "Bubble chart showing Product Profitability (X) vs Market Share (Y), with bubble size indicating total revenue"

**Key Details to Include**:
- X-axis metric
- Y-axis metric
- What each point represents
- Bubble size meaning if applicable
- Color coding if meaningful

---

### Slicers

**Technical**: `slicer`

**Business Description Pattern**:
"[Type] slicer allowing users to filter by [dimension]"

**Examples**:
- "Dropdown slicer allowing users to filter the entire page by fiscal year"
- "Date range slicer enabling users to select a custom time period for analysis"
- "Multi-select slicer for filtering by product category (users can select multiple categories)"

**Key Details to Include**:
- Slicer style (dropdown, list, date range, buttons)
- What dimension it filters
- Scope (page-level, report-level, or visual-level)
- Whether single or multi-select

---

### KPI Visuals

**Technical**: `kpi`

**Business Description Pattern**:
"KPI visual tracking [metric] against [target], showing [status]"

**Examples**:
- "Revenue KPI showing $2.4M actual vs $2.5M target (96% achievement), with downward trend indicator"
- "Customer Satisfaction KPI displaying 4.2/5.0 rating with green status indicator showing performance above goal"

**Key Details to Include**:
- Primary metric value
- Target or goal
- Status indicator (above/below target)
- Trend direction if shown

---

### Gauge Charts

**Technical**: `gauge`

**Business Description Pattern**:
"Gauge chart measuring [metric] against [min-max range or target]"

**Examples**:
- "Gauge showing current month's sales ($1.8M) toward the monthly goal of $2.0M (90% complete)"
- "Performance gauge indicating quality score at 87 out of 100, in the 'Good' range"

**Key Details to Include**:
- Current value
- Maximum value or target
- Color zones if present (red/yellow/green thresholds)

---

### Funnel Charts

**Technical**: `funnel`

**Business Description Pattern**:
"Funnel chart showing conversion through [process stages]"

**Examples**:
- "Sales funnel showing leads → qualified → proposal → closed, with conversion rates at each stage"
- "Website conversion funnel tracking visitors → sign-ups → purchases"

**Key Details to Include**:
- Stages in order
- What metric is being measured (count, value, etc.)
- Conversion rates between stages if visible

---

### Waterfall Charts

**Technical**: `waterfallChart`

**Business Description Pattern**:
"Waterfall chart breaking down [total] into [contributing factors]"

**Examples**:
- "Waterfall chart showing how Gross Revenue ($5M) breaks down to Net Profit ($1.2M) after deducting COGS, Operating Expenses, and Taxes"
- "Budget variance waterfall explaining how planned expenses ($500K) increased to actual expenses ($550K) due to specific cost overruns"

**Key Details to Include**:
- Starting value
- Ending value
- Major contributing increases and decreases
- Business meaning of the breakdown

---

### Treemaps

**Technical**: `treemap`

**Business Description Pattern**:
"Treemap showing hierarchical breakdown of [total] by [categories]"

**Examples**:
- "Treemap visualizing total revenue broken down by region, then by product category within each region, with box size proportional to revenue"
- "Organization headcount treemap showing employee distribution by department and sub-department"

**Key Details to Include**:
- What the total represents
- Hierarchy levels (e.g., region → product)
- What size represents
- Color coding if meaningful

---

### Custom Visuals

**Technical**: Various custom visual IDs (e.g., `PBI_CV_*`)

**Business Description Pattern**:
"[Custom visual name] showing [what it displays]"

**Examples**:
- "Word cloud displaying frequently mentioned product features from customer reviews"
- "Sankey diagram showing customer journey flow from acquisition channel through conversion"

**Key Details to Include**:
- Name of the custom visual
- What data it displays
- How to interpret it (if non-standard)

---

## General Description Guidelines

For ANY visual type:

1. **Lead with purpose**: "Shows comparison of...", "Tracks trend of...", "Displays breakdown of..."
2. **Include the metric**: What specific measure is being visualized
3. **Include the dimension**: What categories/time periods/entities are being analyzed
4. **Note key interactions**: Click-to-filter, drillthrough available, etc.
5. **Describe color/size encoding**: If meaningful (not just decorative)

## Visual Position & Layout

When describing visual placement on a page:

- **Position**: Top-left, top-right, center, bottom panel, sidebar
- **Size**: Full-width, half-page, card-sized, large central visual
- **Grouping**: Visuals arranged together (e.g., "Three KPI cards across the top")

**Example**:
"At the top of the page, three KPI cards display Total Revenue, YoY Growth %, and Active Customers. Below that, a large line chart tracking monthly trends occupies the center, with a region slicer in the left sidebar."
