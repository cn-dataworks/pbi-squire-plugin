# Power BI Analyst - Pro Features

This document contains Pro-tier features for the Power BI Analyst skill.

---

## Pro Trigger Actions

Add these to your workflow detection:

- "Extract templates from this report" → HARVEST_TEMPLATES workflow
- "Review the UX of this dashboard" → REVIEW_UX workflow
- "Harvest visual templates" → HARVEST_TEMPLATES workflow

---

## Pro Workflows

### HARVEST_TEMPLATES (Extract Visual Templates)

**Use when:** User wants to extract reusable visual templates from existing dashboards.

**Commands:** `/harvest-templates`, `/review-templates`, `/promote-templates`

**Process:**
1. Connect to the source report
2. Enumerate all visuals across pages
3. Extract visual configurations with placeholder syntax
4. Categorize by visual type
5. Generate template files with metadata

**Output:** Template files in `assets/visual-templates/` with:
- Visual JSON with `{{PLACEHOLDER}}` tokens
- Metadata (source report, original measures, layout info)
- Usage documentation

See `workflows/harvest-templates.md` for full documentation.

---

### REVIEW_UX (Dashboard UX Analysis)

**Use when:** User wants expert UX review of a published dashboard to identify improvements.

**Prerequisites:**
- Playwright MCP available
- User confirms DataMode = "Anonymized" with fresh refresh

**Commands:** `/review-ux-pbi-dashboard`

**Process:**
1. Check Playwright MCP availability
2. Warn user to verify data is anonymized
3. Navigate to published dashboard (or auto-publish local project)
4. Capture screenshots of all pages
5. Analyze for UX issues (chart types, layout, accessibility, labeling)
6. Analyze visual interactions (cross-filtering, drill-through coordination)
7. Generate implementation-ready recommendations

**Output:** `findings.md` with screenshot evidence and implementation plan sections:
- Section 1.4: UX Review (visual analysis)
- Section 1.5: Interaction Review (coordination analysis)
- Section 2.B: Visual Changes (VISUAL_CHANGE, SETTINGS_CHANGE)
- Section 2.C: Interaction Changes (INTERACTION_CHANGE)

**Next step:** "implement the changes" to apply UX improvements

See `workflows/review-ux-pbi-dashboard.md` for full documentation.

---

## Pro Specialist Agents

### Playwright Tester (`powerbi-playwright-tester`)
**Handles:** Browser automation, visual testing, screenshot capture

**Expertise:**
- Navigating Power BI Service
- Capturing dashboard screenshots
- Interacting with slicers and filters
- Visual regression testing

See `agents/powerbi-playwright-tester.md` for full documentation.

### UX Reviewer (`powerbi-ux-reviewer`)
**Handles:** Dashboard UX analysis, interaction design review

**Expertise:**
- Visual hierarchy analysis
- Chart type recommendations
- Accessibility evaluation
- Cross-filter coordination review
- Layout optimization

See `agents/powerbi-ux-reviewer.md` for full documentation.

---

## Pro Quick Start

Additional examples for Pro users:

1. **Build template library?** → "Harvest visual templates from this report"
2. **Review dashboard UX?** → "Analyze the UX of my published dashboard"
3. **Test interactions?** → "Test the cross-filtering behavior"

---

## Pro References

- `workflows/harvest-templates.md` - Template extraction workflow
- `workflows/review-ux-pbi-dashboard.md` - UX review workflow
- `agents/powerbi-playwright-tester.md` - Browser automation agent
- `agents/powerbi-ux-reviewer.md` - UX analysis agent
- `references/ux-review-guidelines.md` - UX evaluation criteria
