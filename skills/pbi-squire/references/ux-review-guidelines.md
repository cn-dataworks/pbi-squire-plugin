# Power BI Dashboard UX Review Guidelines

This reference provides best practice guidelines for evaluating Power BI dashboard UX across five dimensions: chart type appropriateness, visual hierarchy, color/accessibility, labeling, and interactions.

---

## 1. Chart Type Appropriateness

### Decision Matrix

| Data Characteristics | Recommended Visual | Anti-Patterns |
|---------------------|-------------------|---------------|
| Single value (KPI) | Card, KPI visual, Gauge | Table for single value |
| 2-7 categories | Bar Chart, Column Chart | Pie chart with >5 slices |
| 8-20 categories | Bar Chart with Top N, Table | Pie chart, cluttered bar |
| 20+ categories | Table, Matrix | Any chart type |
| Time series | Line Chart, Area Chart | Bar chart for trends |
| Part-to-whole (<=5 parts) | Donut, Treemap | Pie chart with many slices |
| Geographic | Filled Map, Map | Table with coordinates |
| Two variables relationship | Scatter Plot | Dual-axis line chart |

### Common Anti-Patterns

**Pie Chart Overuse**
- Issue: Pie charts with more than 5-7 slices
- Impact: Human perception of angles/areas is inaccurate for comparison
- Solution: Convert to horizontal bar chart

**Bar Chart for Time Series**
- Issue: Using bar/column charts for temporal trends
- Impact: Breaks the visual expectation of continuous time flow
- Solution: Convert to line chart (shows trend) or area chart (shows accumulation)

**Table for Summary**
- Issue: Using tables to show single values or executive-level KPIs
- Impact: Requires reading effort, no visual encoding for quick scanning
- Solution: Use Card or KPI visual for single values

**3D Effects**
- Issue: Any 3D visual distortion
- Impact: Distorts perception of values
- Solution: Use flat 2D visuals

---

## 2. Visual Hierarchy & Layout

### F-Pattern Reading Flow

Users naturally scan dashboards in an F-pattern:
1. **Top zone (horizontal scan)**: First attention point - place primary KPIs here
2. **Left column (vertical scan)**: Secondary attention - navigation, secondary metrics
3. **Center content**: Primary analytical visuals
4. **Bottom zone**: Filters, supporting detail

### Zone Assignment Guidelines

| Zone | Content Type | Visual Size |
|------|-------------|-------------|
| Top-left | Primary KPI (most important) | Large card |
| Top-center | Secondary KPIs | Medium cards |
| Top-right | Date/filter context | Slicers |
| Middle-left | Supporting metrics | Medium charts |
| Middle-center | Primary analytical visual | Large chart |
| Middle-right | Detail comparison | Medium chart/table |
| Bottom | Filters, detailed tables | Full-width slicers |

### Common Anti-Patterns

**KPIs Below the Fold**
- Issue: Key metrics placed at bottom of page
- Impact: Users must scroll to see most important information
- Solution: Move KPI cards to top-left zone

**Detail Before Summary**
- Issue: Detailed tables above summary charts
- Impact: Violates overview-then-detail principle
- Solution: Restructure: summary visuals at top, detail tables at bottom

**No Visual Grouping**
- Issue: Related visuals scattered across page
- Impact: Users struggle to connect related information
- Solution: Group semantically related visuals together

**Inconsistent Spacing**
- Issue: Uneven gaps between visuals
- Impact: Creates visual chaos, unprofessional appearance
- Solution: Use 8px grid system, consistent margins (24px recommended)

---

## 3. Color & Accessibility

### WCAG Contrast Requirements

| Element Type | Minimum Contrast Ratio |
|-------------|----------------------|
| Normal text | 4.5:1 |
| Large text (18pt+) | 3:1 |
| Graphics/icons | 3:1 |
| Non-text UI | 3:1 |

### Colorblind-Safe Palettes

**Avoid These Combinations:**
- Red + Green (deuteranopia, 8% of males)
- Blue + Purple (tritanopia)
- Green + Brown

**Recommended Alternatives:**

| Instead Of | Use |
|-----------|-----|
| Red/Green traffic light | Blue/Gray/Orange |
| Red for negative | Blue for negative |
| Green for positive | Orange for positive |

**Safe Categorical Palette:**
- Blue, Orange, Gray, Yellow, Teal, Purple (avoid relying on red/green distinction)

### Color Semantics

**Consistency Rules:**
- Same color = same meaning across entire dashboard
- If red means "bad" on one visual, it must mean "bad" everywhere
- Avoid using color for decoration only

**Conditional Formatting Best Practices:**
- Use diverging scales (good → neutral → bad)
- Include pattern/icon redundancy for colorblind users
- Document color meaning in dashboard or title

### Common Anti-Patterns

**Red/Green Only**
- Issue: Traffic light colors without patterns or icons
- Impact: Colorblind users cannot distinguish status
- Solution: Add icons (checkmark, warning, X) or use blue/orange

**Low Contrast Axis Labels**
- Issue: Light gray text on white background
- Impact: Difficult to read, especially for low vision users
- Solution: Increase font weight or use darker color

**Rainbow Palette**
- Issue: Many unrelated colors in single chart
- Impact: Creates visual noise, no meaningful encoding
- Solution: Use sequential or diverging palette based on data meaning

---

## 4. Labeling & Context

### Completeness Checklist

Every visual should have:
- [ ] **Descriptive title** (not "Chart 1" or field name)
- [ ] **Axis labels** with units (if applicable)
- [ ] **Legend** (if multi-series)
- [ ] **Data source/date context** (when data was refreshed)

### Title Guidelines

| Visual Type | Title Pattern | Example |
|-------------|--------------|---------|
| KPI Card | Metric Name | "Total Revenue (YTD)" |
| Comparison Chart | Metric by Dimension | "Sales by Region - Q4 2025" |
| Trend Chart | Metric over Time | "Monthly Revenue Trend" |
| Detail Table | Entity List | "Customer Order Details" |

### Axis Label Guidelines

| Axis Type | Include |
|-----------|---------|
| Currency | Symbol and scale (e.g., "$ (thousands)") |
| Percentage | % symbol in label or format |
| Date | Period granularity (e.g., "Month-Year") |
| Count | "Count of" or "# of" prefix |

### Common Anti-Patterns

**Generic Titles**
- Issue: "Sales1", "Chart", "New Visual", or field name only
- Impact: User must decode what the visual shows
- Solution: Write action-oriented titles (e.g., "Compare Regional Performance")

**Missing Units**
- Issue: Axis shows numbers without context (is it thousands? millions?)
- Impact: Risk of misinterpretation
- Solution: Add unit label to axis title or format string

**Unexplained Acronyms**
- Issue: "COGS", "YTD", "MoM" without definition
- Impact: New users confused
- Solution: Add subtitle with definition or tooltip

**No Date Context**
- Issue: "Total Sales" without time period
- Impact: Users don't know if data is current
- Solution: Add "as of [date]" or include period in title

---

## 5. Interaction Patterns

### Cross-Filtering Guidelines

**Recommended Patterns:**
- KPI cards should NOT filter other visuals (always show totals)
- Charts should cross-filter related charts on same topic
- Tables should filter charts but not other tables
- Slicers should affect all visuals (or clearly marked subset)

**Anti-Patterns:**
- All visuals filtering all visuals (chaos)
- No cross-filtering at all (missed insights)
- KPIs that change when other visuals selected (confusing)

### Drill-Through Best Practices

| Source Visual | Target Page | Data Passed |
|--------------|-------------|-------------|
| Customer in table | Customer Details | Customer ID |
| Product in chart | Product Performance | Product ID |
| Region on map | Regional Breakdown | Region |

**Anti-Patterns:**
- Drill-through to page with different time context
- Drill-through that loses user's filter selections
- No visual indication that drill-through is available

### Slicer Coordination

**Sync Slicer Rules:**
- Slicers that appear on multiple pages MUST sync
- Global filters (date range, business unit) should sync across all pages
- Page-specific filters should NOT sync

**Slicer Placement:**
- Date slicers: Top-right or dedicated filter pane
- Category slicers: Left sidebar or top bar
- Search boxes: Near related table/list

### Visual Coordination Principles

**Complementary Visuals:**
- Summary chart + detail table = good pair
- Same data, different views = reinforcing
- Clicking summary should filter detail

**Conflicting Visuals:**
- Two pie charts side by side (confusing comparison)
- Overlapping data in multiple visuals (redundant)
- Visuals showing same metric with different time periods without clear labels

---

## Severity Levels

| Severity | Criteria | User Impact |
|----------|----------|-------------|
| **CRITICAL** | Fundamentally impairs comprehension | Users may misunderstand data or make wrong decisions |
| **MAJOR** | Significantly reduces usability | Users experience friction or accessibility barriers |
| **MINOR** | Improvement opportunity | Users would benefit but can work without |

### Examples by Severity

**CRITICAL:**
- Pie chart with 15+ slices
- Red/green color scheme with no alternative encoding
- KPIs that show different values based on hidden filters
- Misleading chart scales (truncated axis without indication)

**MAJOR:**
- Missing chart titles
- KPIs at bottom of page
- Low contrast text
- No date context on key metrics
- Slicers that don't sync across pages

**MINOR:**
- Inconsistent spacing
- Generic slicer labels
- Missing axis labels on obvious metrics
- Suboptimal visual type (works but not ideal)

---

## Quick Reference: Red Flags

When reviewing a dashboard, immediately flag:

1. **Pie charts**: Check slice count (should be <=5)
2. **Red/Green**: Check for colorblind alternatives
3. **KPI placement**: Should be top-left, above fold
4. **Chart titles**: Should be descriptive, not field names
5. **Axis labels**: Should include units
6. **Date context**: Every page should show data freshness
7. **Cross-filtering**: KPIs should show totals, not filter

---

## Implementation Notes

When generating findings for `/implement-deploy-test`:

**VISUAL_CHANGE findings** (require visual.json edits):
- Visual type changes
- Position/size changes
- Data binding changes

**SETTINGS_CHANGE findings** (require config property edits):
- Title text
- Axis labels
- Color/formatting
- Legend visibility

**INTERACTION_CHANGE findings** (require interactions.json edits):
- Cross-filter behavior
- Drill-through definitions
- Slicer sync settings

Each finding should include:
1. Visual identifier (name or position)
2. Current state
3. Recommended change
4. Rationale (tied to guideline)
5. Severity level
