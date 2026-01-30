# Power BI Design Standards

**Project-Specific Design Configuration**

This file was created during PBI Squire Pro bootstrap. Customize it to match your organization's design standards. The agent will use these rules when generating dashboards and critiquing visual designs.

---

## Organization Branding

### Color Palette

*Replace these with your organization's brand colors:*

| Purpose | Color Name | Hex Code |
|---------|-----------|----------|
| Primary Data | Brand Blue | `#0078D4` |
| Secondary Data | Brand Accent | `#00BCF2` |
| Tertiary Data | Brand Neutral | `#605E5C` |
| Positive/Success | Success Green | `#107C10` |
| Negative/Alert | Alert Red | `#D83B01` |
| Background | Canvas | `#F0F0F0` |
| Visual Container | White | `#FFFFFF` |

### Typography

| Element | Font Family | Size | Weight |
|---------|------------|------|--------|
| Dashboard Title | Segoe UI | 22pt | Bold |
| Section Header | Segoe UI | 14pt | Semi-Bold |
| Visual Title | Segoe UI | 12pt | Regular |
| Data Labels | Segoe UI | 10pt | Regular |
| Axis Labels | Segoe UI | 10pt | Regular |

### Logo & Branding

```
Logo Placement: [Top-Right / Top-Left / None]
Logo Size: [Width]x[Height] px
Footer Text: [Your disclaimer or branding text]
Classification: [Internal / Confidential / Public]
```

---

## Layout Standards

### Grid System

| Setting | Value |
|---------|-------|
| Outer Margin | 20px |
| Gutter (between visuals) | 10px |
| Min Visual Width | 200px |
| Min Visual Height | 150px |

### Zone Layout

```
+------------------------------------------+
| ZONE 1: KPIs          | ZONE 2: Filters  |
| [Primary metrics]     | [Date, Category] |
+------------------------------------------+
| ZONE 3: Main Analysis                    |
| [Trend charts, comparisons]              |
+------------------------------------------+
| ZONE 4: Detail                           |
| [Tables, drill-through]                  |
+------------------------------------------+
```

---

## Visual Standards

### Allowed Visual Types

*Check the visuals your organization approves:*

- [x] Card
- [x] KPI
- [x] Line Chart
- [x] Column Chart
- [x] Bar Chart
- [x] Table
- [x] Matrix
- [x] Donut Chart
- [ ] Pie Chart (discouraged)
- [x] Map
- [x] Filled Map
- [x] Scatter Chart
- [ ] Gauge
- [ ] Treemap
- [x] Slicer

### Prohibited Elements

- [ ] 3D effects
- [ ] Scrollbars on charts
- [ ] Pie charts with >5 slices
- [ ] Decorative images
- [ ] Animation effects
- [ ] Custom visuals (unless approved)

### Data Labels

| Scenario | Show Labels |
|----------|-------------|
| Card/KPI | Always |
| Bar Chart (<10 bars) | Yes |
| Bar Chart (>10 bars) | No (use tooltip) |
| Line Chart | No (use tooltip) |
| Table | N/A |

---

## Content Standards

### Required Elements

Every dashboard page must include:

- [ ] Descriptive page title
- [ ] Data refresh timestamp
- [ ] Date range context (if time-based)
- [ ] Source attribution (if required)

### Title Patterns

| Visual Type | Title Pattern | Example |
|-------------|--------------|---------|
| KPI Card | `[Metric Name]` | "Total Revenue" |
| Trend Chart | `[Metric] Over Time` | "Monthly Sales Trend" |
| Comparison | `[Metric] by [Dimension]` | "Revenue by Region" |
| Detail Table | `[Entity] Details` | "Order Details" |

### Naming Conventions

- Measures: PascalCase with spaces (`Total Revenue`, `YoY Growth %`)
- Columns: Match source or PascalCase
- Pages: Descriptive, max 30 characters

---

## Accessibility Requirements

### Contrast Minimums

| Element | Minimum Contrast Ratio |
|---------|----------------------|
| Normal Text | 4.5:1 |
| Large Text (18pt+) | 3:1 |
| Chart Elements | 3:1 |

### Colorblind Considerations

- [ ] Avoid red/green only encoding
- [ ] Use patterns or icons as secondary encoding
- [ ] Test with colorblind simulation tools

---

## Organization-Specific Rules

*Add your company's specific requirements below:*

### Financial Reports
```
- Must include fiscal period context
- Currency must be explicit (USD, EUR, etc.)
- Variance formatting: () for negative, not color alone
```

### Customer Data
```
- PII columns must be masked in development
- Access warning required on customer detail pages
- Data retention notice in footer
```

### Compliance
```
- Audit trail: Include "Last Modified" field
- Approval status badge for published reports
- Version number in report footer
```

---

## QA Checklist

*Agent uses this during the Visual Analysis Loop:*

### Technical (Must Pass)
- [ ] No error messages visible
- [ ] No grey boxes / broken visuals
- [ ] No scrollbars (except intentional tables)
- [ ] No truncated titles
- [ ] All visuals render within 10 seconds

### Design (Scored 1-5)
- [ ] Layout follows zone pattern
- [ ] All edges aligned to grid
- [ ] Consistent spacing between visuals
- [ ] Color palette matches standards
- [ ] Typography hierarchy is clear

### Content (Must Pass)
- [ ] All required elements present
- [ ] Titles are descriptive (not "Chart 1")
- [ ] Date context is clear
- [ ] Metrics answer the user's question

---

## Notes

*Document any project-specific decisions or exceptions:*

```
[Your notes here]
```

---

*This file is checked by the PBI Squire agent during dashboard generation and QA loops. Keep it updated as your standards evolve.*
