# Translation Guidelines: Technical to Business Language

Guidelines for translating Power BI technical content into business-friendly language.

## Core Principles

### 1. Focus on "What" and "Why", Not "How"

**Good:**
- "Total Sales excluding returns and discounts"
- "Year-over-year comparison of revenue"
- "Percentage of target achieved"

**Avoid:**
- "SUMX function iterating over filtered table context"
- "SAMEPERIODLASTYEAR time intelligence function"
- "CALCULATE with ALL modifier removing filter context"

### 2. Explain Dependencies Without Overwhelming Detail

**Good:**
- "Depends on: Total Sales, Prior Year Sales"
- "Uses: Product Category, Region filters"
- "Calculated from: Invoice Amount, Discount Amount"

**Avoid:**
- Full nested DAX code blocks
- Complete dependency trees
- Internal variable names

### 3. Use Business Terminology

| Technical Term | Business Translation |
|----------------|---------------------|
| SAMEPERIODLASTYEAR | Same period last year |
| CALCULATE | Filtered calculation |
| SUMX | Sum of (individual) |
| AVERAGEX | Average of (individual) |
| DIVIDE | Division (safe from errors) |
| BLANK() | No value / empty |
| ALL | Ignoring filters |
| FILTER | Only including |

### 4. Describe Visual Purpose, Not Just Type

**Good:**
- "Line chart tracking monthly revenue trends over time"
- "Bar chart comparing sales performance across regions"
- "Card showing current month's total revenue"

**Avoid:**
- "Line chart with Date on X-axis and Revenue on Y-axis"
- "Clustered bar chart visual"
- "Card visual bound to [Total Sales]"

### 5. Include Just Enough Technical Detail

For credibility, include:
- Simplified code snippets when helpful
- Specific table/column names when relevant
- Important business logic (filters, conditions)

**Example:**
```
**Profit Margin %**
- Definition: Profit as a percentage of revenue
- Calculation: (Revenue - Cost) / Revenue
- Note: Returns 0% when revenue is zero (prevents errors)
```

## Measure Explanation Format

```markdown
**[Measure Name]**
- **Definition:** [One-sentence business explanation]
- **Dependencies:** [List of measures/columns it uses]
- **Business Logic:** [Any important conditions or filters]
- **Example:** [Optional: sample value with context]
```

### Example Measure Explanations

**Total Sales**
- **Definition:** Sum of all invoice amounts excluding returns and cancelled orders
- **Dependencies:** Sales Amount (column from Invoices table)
- **Business Logic:** Filters out records where Status = "Cancelled" or Return = TRUE

**Year-over-Year Growth %**
- **Definition:** Percentage increase or decrease compared to the same period last year
- **Dependencies:** Total Sales, Prior Year Sales
- **Business Logic:** Returns 0% if there were no sales in the prior period
- **Example:** If current month is $120K and last year was $100K, shows +20%

**Profit Margin %**
- **Definition:** Profit expressed as a percentage of revenue
- **Dependencies:** Total Revenue, Total Cost
- **Business Logic:** Safe division that returns 0% if revenue is zero

## Visual Description Format

```markdown
**[Visual Title or Purpose]**
- **Type:** [Visual type in plain language]
- **Purpose:** [What business question it answers]
- **Shows:** [Key data points displayed]
- **Interactivity:** [How users can interact with it]
```

### Example Visual Descriptions

**Sales by Region Chart**
- **Type:** Horizontal bar chart
- **Purpose:** Compare total sales performance across geographic regions
- **Shows:** Region names on left, sales amounts as bars
- **Interactivity:** Clicking a region filters other visuals on the page

**Monthly Revenue Trend**
- **Type:** Line chart with markers
- **Purpose:** Track revenue performance over time, identify trends
- **Shows:** Months on horizontal axis, revenue on vertical axis
- **Interactivity:** Hover for exact values, brush to zoom

**YTD Performance Card**
- **Type:** Single number card
- **Purpose:** Show year-to-date total at a glance
- **Shows:** Current YTD revenue with comparison to prior year
- **Interactivity:** None (static display)

## Page Summary Format

```markdown
### [Page Name]

**Purpose:** [One sentence describing what business question this page answers]

**Key Metrics:**
- [Metric 1]: [Brief description]
- [Metric 2]: [Brief description]

**Filters Available:**
- [Filter 1]: [What it controls]
- [Filter 2]: [What it controls]

**Visuals:**
[List of visual descriptions]
```

## Common DAX Pattern Translations

| DAX Pattern | Business Description |
|-------------|---------------------|
| `CALCULATE(SUM(...), ALL(...))` | Total ignoring current filters |
| `DIVIDE(A, B, 0)` | A divided by B (zero if B is empty) |
| `CALCULATE(..., SAMEPERIODLASTYEAR(...))` | Same calculation for last year's period |
| `CALCULATE(..., DATEADD(..., -1, MONTH))` | Same calculation for previous month |
| `IF(ISBLANK(...), 0, ...)` | Returns 0 when no data exists |
| `SUMX(table, expression)` | Sum calculated row by row |
| `RANKX(ALL(...), ...)` | Ranking across all items |

## Interaction Pattern Translations

| Technical Behavior | Business Description |
|-------------------|---------------------|
| Cross-filter | Clicking this visual filters other visuals on the page |
| Cross-highlight | Clicking this visual highlights related data elsewhere |
| Drillthrough | Right-click to navigate to a detail page |
| Tooltip | Hover to see additional information |
| Sync slicers | This filter applies to multiple pages |

## Tips for Effective Translation

1. **Start with the business question** - What decision does this help make?
2. **Avoid jargon** - If a business user wouldn't say it, rephrase it
3. **Use examples** - Concrete numbers help understanding
4. **Note limitations** - When does the metric not apply?
5. **Group related metrics** - Help users see the bigger picture
