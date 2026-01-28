# Power BI Interaction Patterns - Business Language Guide

This reference explains common Power BI dashboard interactions in business-friendly terms.

## Cross-Filtering

### What It Is

Cross-filtering is when clicking or selecting data in one visual automatically filters the data shown in other visuals on the same page.

### Business Description Patterns

**Basic Pattern**:
"Clicking [element] in the [visual name] filters other visuals on the page to show only data related to the selected [element]"

**Examples**:
- "Clicking a region on the map filters all charts to show only that region's data"
- "Selecting a product category in the bar chart updates the revenue trend line to show only that category"
- "Clicking a customer segment in the pie chart filters the sales table to show only customers in that segment"

### How to Document

When documenting a page, note cross-filtering patterns:

```markdown
**Interactions**:
- Clicking any region on the Sales by Region map filters all other visuals to show only that region's performance
- Selecting a time period in the Date slicer updates all visuals to show data for the selected dates
- All visuals cross-filter each other except the KPI cards at the top (which always show totals)
```

### Disabled Cross-Filtering

Some visuals are set to NOT filter others:

**Business Description**:
"[Visual name] does not filter other visuals when clicked - it always shows the overall total"

**Example**:
- "The Total Revenue KPI card always shows company-wide revenue and is not affected by selections in other visuals"

---

## Drillthrough

### What It Is

Drillthrough allows users to right-click on a data point and navigate to a detailed page showing more information about that specific item.

### Business Description Patterns

**Basic Pattern**:
"Right-clicking on [data element] and selecting 'Drill through to [page name]' navigates to a detailed view showing [what details]"

**Examples**:
- "Right-clicking on any customer in the Customer List and selecting 'Drill through to Customer Details' opens a dedicated page showing that customer's full order history, lifetime value, and contact information"
- "Right-clicking a product in the sales chart allows drilling through to the Product Performance page with detailed sales trends for that specific product"
- "Users can right-click any region and drill through to Regional Details to see store-level breakdowns"

### How to Document

```markdown
**Drillthrough Available**:
- From any customer name → Customer Details page (shows order history, lifetime value, recent activity)
- From any product → Product Performance page (shows sales trends, margin analysis, inventory levels)
- From any sales representative → Rep Performance page (shows individual KPIs, territory details, commission breakdown)
```

### Drillthrough Filters

**Description**:
"The drillthrough target page automatically filters to show only data related to the selected [entity]"

**Example**:
- "When drilling through to the Customer Details page, all visuals on that page automatically filter to show only the selected customer's data"

---

## Drill Down / Drill Up

### What It Is

Drill down allows navigating through hierarchical levels within a single visual (e.g., Year → Quarter → Month → Day, or Country → State → City).

### Business Description Patterns

**Basic Pattern**:
"Click the drill-down icon (↓) to expand into more detailed levels: [hierarchy path]"

**Examples**:
- "The Revenue Trend chart supports drill-down from Year → Quarter → Month → Day. Click the down arrow to see more granular time periods"
- "The Regional Sales map allows drill-down from Country → State → City to see increasingly detailed geographic breakdowns"
- "Product sales can be drilled from Category → Subcategory → Product to analyze at different levels of detail"

### How to Document

```markdown
**Drill-Down Hierarchy**:
- Time hierarchy: Year → Quarter → Month → Day
  - Click ↓ to expand to next level, ↑ to return to previous level
  - Double-click any data point to drill into that specific branch

**Navigation**:
- ↓ icon: Drill down one level for all categories
- ↑ icon: Drill back up one level
- Double-click: Drill down into specific item only
```

---

## Tooltips

### What It Is

Tooltips are pop-up windows that appear when hovering over a visual, providing additional context or related metrics.

### Business Description Patterns

**Default Tooltips**:
"Hovering over [visual element] displays [what information]"

**Examples**:
- "Hovering over any bar in the sales chart displays the exact sales amount, product name, and percentage of total"
- "Hovering over data points in the trend line shows the date and value"

**Custom Report Page Tooltips**:
"Hovering over [visual element] displays a custom tooltip page showing [detailed information]"

**Examples**:
- "Hovering over any product in the revenue chart displays a custom tooltip showing product margin, units sold, and inventory status"
- "Hovering over customer segments shows a detailed breakdown of customer count, average order value, and retention rate"

### How to Document

```markdown
**Tooltips**:
- Hovering over any bar shows: Product Name, Total Sales, Percentage of Total
- Hovering over customer names displays a custom tooltip page with:
  - Customer Lifetime Value
  - Total Orders (count)
  - Average Order Value
  - Days Since Last Purchase
```

---

## Slicers and Filters

### Page-Level Filters

**What It Is**: Filters that affect all visuals on the current page only.

**Business Description**:
"[Filter name] at [location] filters all visuals on this page to show only [what]"

**Examples**:
- "The Year slicer at the top-left filters all visuals on the Executive Summary page to the selected year(s)"
- "The Product Category dropdown in the sidebar filters all sales charts and tables to show only the selected categories"

### Report-Level Filters

**What It Is**: Filters that affect all pages in the report.

**Business Description**:
"[Filter name] applies to the entire report across all pages"

**Examples**:
- "The Region filter applies globally - when you select 'West', all pages in the report show only Western region data"
- "The Date Range slicer persists across pages, maintaining the selected time period as you navigate through the report"

### Visual-Level Filters

**What It Is**: Filters that only affect a specific visual.

**Business Description**:
"[Visual name] is filtered to show only [condition]"

**Examples**:
- "The Top 10 Products chart is pre-filtered to show only the highest-selling products"
- "The Customer table is filtered to show only active customers (excluding inactive accounts)"

### How to Document

```markdown
**Filters on This Page**:

**Page-Level Filters** (affect all visuals on this page):
- Year Slicer (multi-select dropdown) - Filter by fiscal year
- Region Slicer (button array) - Filter by geographic region
- Product Category (dropdown) - Filter by product category

**Report-Level Filters** (affect entire report):
- Date Range (date picker) - Select custom date range for analysis
- Sales Channel (multi-select) - Include/exclude Online, Store, Phone channels

**Visual-Specific Filters**:
- Top Products chart: Pre-filtered to top 10 by sales
- Active Customers table: Filtered to customers with orders in last 90 days
```

---

## Page Navigation

### Navigation Buttons

**What It Is**: Buttons that navigate to different pages in the report.

**Business Description**:
"Click the '[Button Text]' button to navigate to the [Page Name] page"

**Examples**:
- "Click the 'View Details' button to navigate to the detailed Sales Analysis page"
- "Navigation buttons at the top allow quick access to Executive Summary, Regional Breakdown, and Product Performance pages"

### Bookmark Navigation

**What It Is**: Buttons that restore specific view states (filters, focus, zoom).

**Business Description**:
"Click '[Bookmark Name]' to switch to a pre-configured view showing [what]"

**Examples**:
- "Click 'Current Year' to filter all visuals to YTD data"
- "Toggle between 'Revenue View' and 'Units View' to switch the focus metric across all charts"

### How to Document

```markdown
**Navigation**:
- Top navigation bar provides links to:
  - Executive Summary (main overview page)
  - Sales Analysis (detailed sales breakdowns)
  - Customer Insights (customer segmentation and behavior)
  - Product Performance (product-level metrics)

**Bookmark Toggles**:
- "Current Year" / "All Time" toggle switches the time frame
- "Revenue" / "Units" / "Profit" toggle switches the displayed metric
```

---

## Sync Slicers

### What It Is

Sync slicers appear on multiple pages and maintain the same selection as you navigate between pages.

### Business Description

**Pattern**:
"The [slicer name] is synchronized across [which pages] - your selection persists as you navigate between these pages"

**Examples**:
- "The Year slicer is synchronized across all pages - when you select '2024' on the Summary page, all other pages also filter to 2024"
- "Region and Product Category slicers are synced across Sales Analysis, Customer Insights, and Product Performance pages for consistent filtering"

### How to Document

```markdown
**Synchronized Slicers** (persist across pages):
- Year Slicer: Appears on all pages and maintains selection
- Region Filter: Synced across Sales Analysis and Regional Breakdown pages
- Product Category: Synced across Product Performance and Customer Insights pages
```

---

## Focus Mode / Full Screen

### What It Is

Users can expand a single visual to full screen for detailed examination.

### Business Description

**Pattern**:
"Click the 'Focus Mode' icon (⤢) in the top-right of any visual to expand it to full screen"

**Examples**:
- "Users can expand the sales trend chart to full screen using the Focus Mode button for detailed analysis"
- "Click the full-screen icon on any table to see all rows without scrolling"

---

## Conditional Formatting Visual Cues

### What It Is

Visuals use color, icons, or data bars to highlight important values.

### Business Description Patterns

**Color-Based**:
"[Visual name] uses color to indicate [what]: [color meaning]"

**Examples**:
- "The Sales table uses color-coded backgrounds: green for above target, yellow for on track, red for below target"
- "The performance matrix highlights high-performing regions in dark green and underperforming regions in red"

**Icon-Based**:
"[Visual name] displays icons to show [what]: [icon meanings]"

**Examples**:
- "The KPI cards show trend arrows: ↑ for growth, ↓ for decline, → for stable"
- "The customer list shows status icons: ✓ for active, ⚠ for at-risk, ✗ for churned"

**Data Bars**:
"[Visual name] includes data bars to visualize [what] magnitude"

**Examples**:
- "The product table includes data bars in the Revenue column to quickly compare relative performance"

### How to Document

```markdown
**Visual Indicators**:
- Sales Performance table:
  - Background color: Green (above target), Yellow (90-100% of target), Red (below 90%)
  - Trend arrows: ↑ (growth), ↓ (decline), → (flat)
- Customer Status column:
  - ✓ Active customer (purchased in last 90 days)
  - ⚠ At-risk (no purchase in 90-180 days)
  - ✗ Churned (no purchase in >180 days)
```

---

## Mobile Layout / Responsive Design

### What It Is

Reports may have different layouts for desktop vs. mobile viewing.

### Business Description

**Pattern**:
"This dashboard has a mobile-optimized layout that reorganizes visuals for smaller screens"

**Examples**:
- "On mobile devices, visuals stack vertically for easier scrolling rather than side-by-side layout"
- "The mobile layout shows only the key KPIs on the first screen, with detailed charts accessible via scrolling"

---

## General Interaction Documentation Template

When documenting a page, include:

```markdown
## Page: [Page Name]

### Purpose
[What this page is designed to show/answer]

### Visuals
[List and describe each visual - see visual_types.md]

### Filters
**Page-Level**: [List]
**Report-Level**: [List]
**Visual-Specific**: [List]

### Interactions
**Cross-Filtering**:
- [Describe how visuals filter each other]

**Drillthrough**:
- [Describe available drillthrough targets]

**Drill-Down**:
- [Describe hierarchies available]

**Tooltips**:
- [Describe custom tooltips or special hover behavior]

### Navigation
- [Describe buttons or links to other pages]
```

---

## Best Practices for Documenting Interactions

1. **Use action verbs**: "Click", "Hover over", "Right-click", "Select"
2. **Be specific about outcomes**: Don't just say "filters other visuals" - say what gets filtered
3. **Note exceptions**: "All visuals cross-filter except the KPI cards which show overall totals"
4. **Include navigation paths**: "Right-click → Drill through to → Customer Details"
5. **Describe user workflows**: "Users typically start on Executive Summary, then drill through to Regional Breakdown for specific areas of concern"
6. **Document hidden features**: "Advanced users can press Ctrl+Click to multi-select items in the slicer"
