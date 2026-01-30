# Power BI Design Standards & AI Critique Rubric

This document serves two purposes for the PBI Squire skill:

1. **The "Constitution"**: Rules agents follow when generating dashboards and visuals
2. **The "Rubric"**: Checklist agents use during the Visual Analysis Loop (post-screenshot) to objectively grade their own work

**For Customization**: During Pro bootstrap, a copy of this document is placed in your project's `.claude/` folder. You can customize it to match your organization's brand guidelines, color palettes, and design standards.

---

## 1. Visual Style Guidelines (The "Look")

### A. Color Palette & Usage

**Primary Palette:**
- Use a maximum of **3 distinct hues** for data categories
- Do not use random colors - use the defined Theme JSON colors
- Maintain color consistency across all pages of the report

**Semantic Colors:**
| Purpose | Color Family | Hex Examples |
|---------|-------------|--------------|
| Positive/On-target | Green/Blue | `#107C10`, `#0078D4` |
| Negative/Off-target | Red/Orange | `#D83B01`, `#A4262C` |
| Neutral/Context | Greys | `#605E5C`, `#8A8886` |

**Backgrounds:**
| Element | Recommended | Avoid |
|---------|-------------|-------|
| Canvas | Light Grey (`#F0F0F0`) or White | Dark backgrounds |
| Visual Containers | White (`#FFFFFF`) with subtle border/shadow | Colored backgrounds |
| Cards | Solid white or very light accent | Gradients, patterns |

**Agent Check:** "Does the dashboard look like a 'fruit salad' (too many colors)? If yes, FAIL."

### B. Typography & Hierarchy

| Element | Size | Weight | Alignment |
|---------|------|--------|-----------|
| Dashboard Title | 20-24pt | Bold | Top Left |
| Section Headers | 14-16pt | Semi-Bold | Left |
| Visual Titles | 12-14pt | Regular/Semi-Bold | Left within container |
| Data Labels | 9-11pt | Regular | Depends on visual |
| Axis Labels | 9-11pt | Regular | Default position |

**Font Recommendations:**
- Primary: Segoe UI (Power BI default)
- Fallback: Arial, Helvetica
- Avoid: Decorative fonts, multiple font families

**Agent Check:** "Is the text hierarchy clear? Can I distinguish the Dashboard Title from a Chart Title?"

### C. Spacing & Alignment (The Grid)

**Grid System:**
```
+--[20px margin]--+--[content]--+--[20px margin]--+
|                 |             |                 |
| [20px] Visual   | [10px gap]  | Visual [20px]  |
|                 |             |                 |
+--------[10-15px gutter between rows]------------+
```

**Rules:**
- **Margins**: Uniform 20px outer margin around entire canvas
- **Gutter**: 10-15px consistent spacing between visual containers
- **Alignment**:
  - Top edges: Align horizontally
  - Left/Right edges: Align vertically
  - Use Power BI's snap-to-grid feature

**Agent Check:** "Do the edges of the visuals align perfectly, or is there 'stair-casing'? Stair-casing is a FAIL."

---

## 2. Best Practices (The "Feel")

### A. Layout Strategy (Z-Pattern / F-Pattern)

Users scan dashboards following predictable patterns. Optimize layout accordingly:

```
+------------------------------------------+
|  ZONE 1 (Top-Left)    | ZONE 2 (Top-Right)|
|  Most Important KPIs  | Global Slicers    |
|  (Single Value Cards) | (Date, Region)    |
+------------------------------------------+
|           ZONE 3 (Center)                 |
|           Trend Analysis                  |
|           (Line, Column Charts)           |
+------------------------------------------+
|           ZONE 4 (Bottom)                 |
|           Detailed Data                   |
|           (Tables, Matrices)              |
+------------------------------------------+
```

**Zone Assignments:**
| Zone | Purpose | Visual Types | Size |
|------|---------|-------------|------|
| 1 (Top-Left) | Primary KPI | Card, KPI | Large |
| 2 (Top-Right) | Context/Filters | Slicers, Date Range | Medium |
| 3 (Center) | Trend/Comparison | Line, Column, Bar | Large |
| 4 (Bottom) | Detail | Table, Matrix | Full-width |

### B. Data-Ink Ratio

Maximize data, minimize chart junk:

**Remove Clutter:**
- No unnecessary gridlines
- No decorative borders or backgrounds
- No 3D effects (NEVER)
- No shadow effects on data elements

**Label Guidelines:**
| Scenario | Action |
|----------|--------|
| Labels fit without overlap | Show data labels |
| Labels overlap | Rely on tooltips and axis |
| Single KPI | Always show value prominently |

**Scrollbars - STRICT PROHIBITION:**
- Scrollbars indicate poor design
- Exception: Intentionally scrollable detail tables at bottom of page
- **Agent Check:** "Are there any scrollbars visible? If yes (except intentional detail tables), FAIL."

### C. Visual Selection Guide

| Data Question | Recommended Visual | Avoid |
|--------------|-------------------|-------|
| Single value (KPI) | Card, KPI Visual, Gauge | Table for single value |
| Time trends | Line Chart, Area Chart | Bar chart for time series |
| Category comparison (2-7 items) | Bar Chart, Column Chart | Pie with >5 slices |
| Category comparison (8-20 items) | Horizontal Bar with Top N | Any pie chart |
| Category comparison (20+ items) | Table, Matrix | Any chart |
| Part-to-whole (<=5 parts) | Donut, Treemap | Pie with many slices |
| Geographic data | Map, Filled Map | Table with coordinates |
| Two variable relationship | Scatter Plot | Dual-axis line chart |

**Pie Chart Policy:**
- Maximum 4-5 slices
- Must have "Other" category if more
- Prefer Donut over Pie (shows total in center)
- Better alternative: Horizontal Bar Chart (always)

---

## 3. The "Loop" Critique Protocol

*When the agent receives a screenshot from Playwright MCP, execute this analysis routine.*

### Phase 1: The "Glitch" Scan (Pass/Fail)

**Check for technical failures before analyzing design:**

| Check | Pattern | Result |
|-------|---------|--------|
| Error Messages | "Can't display visual", "X", "Something went wrong" | **CRITICAL FAIL** |
| Broken Images | Placeholder image icons | **FAIL** |
| Truncated Text | Titles cut off with `...` inappropriately | **FAIL** |
| Grey Boxes | Visual containers with no content | **FAIL** |
| Loading Spinners | Persistent spinners after 10+ seconds | **WARN** |

**Immediate Actions on Fail:**
- Document the exact error
- Capture screenshot evidence
- Identify likely cause (data binding, measure error, etc.)
- Propose fix in findings

### Phase 2: The "Design" Critique (Scored 1-5)

*Analyze the screenshot against the standards above.*

**Question 1: Layout & Alignment**
- "Draw imaginary lines between the edges of visuals. Are they straight?"
- "Is the whitespace consistent?"
- *Action if messy:* "Snap visuals to grid. Align Top of Visual A with Top of Visual B."

**Question 2: Data Density & Readability**
- "Is the screen too crowded?"
- "Is the text too small to read?"
- "Are there any overlapping elements?"
- *Action if crowded:* "Reduce number of visuals or increase canvas height."

**Question 3: Visual Type Appropriateness**
- "Is the right chart type used for this data?"
- "Does the time series use a line chart?"
- "Does the pie chart have more than 5 slices?"
- *Action if wrong:* "Change visual type from [current] to [recommended]."

**Question 4: Context & Labeling**
- "Does every visual have a descriptive title?"
- "Are axis labels present with units?"
- "Is there date context for time-sensitive data?"
- *Action if missing:* "Add title: '[Descriptive Title]'"

**Question 5: Answering the Question**
- "Does the dashboard answer the specific User Question from the prompt?"
- "Are the required metrics present?"
- *Action if wrong context:* Mark as **WRONG CONTEXT** - requirements mismatch.

### Phase 3: Scoring

**Overall Score Calculation:**

| Score | Criteria | Action |
|-------|----------|--------|
| 5 | All checks pass, exemplary design | Complete |
| 4 | Minor issues only (spacing, labels) | Document, optionally fix |
| 3 | Moderate issues affecting usability | Iterate - fix required |
| 2 | Major issues blocking comprehension | Iterate - significant rework |
| 1 | Critical failures (errors, wrong data) | Iterate - start over |

---

## 4. Agent Output Format (The "Critique")

*When analyzing a screenshot, produce this structured output:*

```markdown
### Visual Analysis Report
**Status:** [COMPLETE | NEEDS ITERATION]
**Score:** [1-5]/5

**1. Technical Check:**
* [x] No Error Messages
* [x] No Grey Boxes / Broken Visuals
* [x] No Scrollbars (except intentional tables)
* [ ] No Truncated Text -> *Fail: [description]*

**2. Design Critique:**
* **Alignment:** [Assessment - specific issues if any]
* **Whitespace:** [Assessment - specific fixes if needed]
* **Color:** [Assessment - fruit salad check]
* **Visual Types:** [Assessment - wrong chart types]
* **Typography:** [Assessment - hierarchy issues]

**3. Content Verification:**
* **Requirement:** "[Original user request]"
* **Observation:** [What the dashboard actually shows]
* **Verdict:** [Match | Mismatch - details]

**4. Specific Issues:**
| # | Visual | Issue | Fix |
|---|--------|-------|-----|
| 1 | [Name] | [Problem] | [Solution] |

**Next Steps:**
1. [Specific action with visual ID/name]
2. [Specific action]
3. Restart QA Loop
```

---

## 5. Quick Reference Checklists

### Pre-Generation Checklist

Before generating a dashboard, confirm:
- [ ] User requirements are clear
- [ ] Data model is understood (tables, measures available)
- [ ] Target audience is identified
- [ ] Theme JSON is available (or use defaults)

### Post-Generation Checklist

Before submitting for review:
- [ ] All visuals have descriptive titles
- [ ] Layout follows Z/F-pattern
- [ ] Maximum 3 color hues for data
- [ ] No scrollbars
- [ ] All edges aligned
- [ ] Consistent spacing

### Visual Type Decision Tree

```
Is it a single number?
  YES -> Card or KPI Visual
  NO -> Continue

Is it over time?
  YES -> Line Chart or Area Chart
  NO -> Continue

Is it comparing categories?
  YES -> How many?
    2-7 -> Column or Bar Chart
    8-20 -> Horizontal Bar with Top N
    20+ -> Table or Matrix
  NO -> Continue

Is it part-of-whole?
  YES -> How many parts?
    <=5 -> Donut or Treemap
    >5 -> Horizontal Bar (never pie!)
  NO -> Continue

Is it geographic?
  YES -> Map or Filled Map
  NO -> Continue

Is it showing relationships?
  YES -> Scatter Plot
  NO -> Consult user for requirements
```

---

## 6. Customization Guide

This document is copied to your project during Pro bootstrap at:
```
.claude/powerbi-design-standards.md
```

### Customizing for Your Organization

**Color Palette:**
Replace the semantic colors section with your brand colors:
```markdown
| Purpose | Color | Hex |
|---------|-------|-----|
| Primary | [Your Brand Blue] | #XXXXXX |
| Secondary | [Your Brand Accent] | #XXXXXX |
| Positive | [Your Success Color] | #XXXXXX |
| Negative | [Your Alert Color] | #XXXXXX |
```

**Typography:**
If your organization uses specific fonts:
```markdown
| Element | Font | Size | Weight |
|---------|------|------|--------|
| Dashboard Title | [Your Font] | 24pt | Bold |
...
```

**Logo Placement:**
Add a section for required branding:
```markdown
### Brand Requirements
- Company logo: Top-right corner, 100x30px
- Footer text: "Confidential - [Company Name]"
- Report classification badge required
```

**Additional Standards:**
Add organization-specific rules:
```markdown
### [Company] Specific Standards
- All reports must include data refresh timestamp
- Financial data requires disclaimer
- Customer data pages require access warning
```

---

## 7. Integration with QA Loop

This document is referenced during:

1. **Dashboard Generation** (`powerbi-page-layout-designer`, `powerbi-visual-implementer-apply`)
   - Agents follow Section 1-2 as design rules

2. **QA Inspection** (`powerbi-qa-inspector`, `/qa-loop-pbi-dashboard`)
   - Agents use Section 3-4 as critique protocol

3. **UX Review** (`powerbi-ux-reviewer`, `/review-ux-pbi-dashboard`)
   - Complements `ux-review-guidelines.md` with style specifics

### Loading Custom Standards

Agents check for custom standards in this order:
1. `.claude/powerbi-design-standards.md` (user customized)
2. `references/powerbi-design-standards.md` (plugin default)

If custom standards exist, they override the defaults.

---

## See Also

- `ux-review-guidelines.md` - Detailed UX evaluation criteria
- `workflows/qa-loop-pbi-dashboard.md` - QA loop workflow
- `agents/powerbi-qa-inspector.md` - DOM inspection agent
- `agents/powerbi-ux-reviewer.md` - UX analysis agent
