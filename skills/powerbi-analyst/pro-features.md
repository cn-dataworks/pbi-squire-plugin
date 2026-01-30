# Power BI Analyst - Pro Features

This document contains Pro-tier features for the Power BI Analyst skill.

---

## Pro Bootstrap Features

When running `bootstrap.ps1` on a Pro installation, these additional files are created:

### Design Standards (`powerbi-design-standards.md`)

A customizable design specification copied to `.claude/powerbi-design-standards.md` in your project. This file serves as:

1. **The "Constitution"**: Rules agents follow when generating dashboards
2. **The "Rubric"**: Checklist for the Visual Analysis Loop during QA

**What you can customize:**
- Organization color palette and brand colors
- Typography standards (fonts, sizes, weights)
- Logo placement and branding requirements
- Layout grid specifications
- Allowed/prohibited visual types
- Accessibility requirements
- Organization-specific compliance rules

**How agents use it:**
- Dashboard generation agents reference it for styling decisions
- QA Inspector uses it during the design critique phase
- UX Reviewer cross-references it with UX guidelines

**File locations:**
- Template: `tools/templates/powerbi-design-standards.md`
- Plugin default: `references/powerbi-design-standards.md`
- Your customized copy: `.claude/powerbi-design-standards.md` (created during bootstrap)

If your project has a customized version, agents will use that instead of the plugin default.

---

## Pro Trigger Actions

Add these to your workflow detection:

**Page Creation:**
- "Create a dashboard page" → CREATE_PAGE workflow
- "Build a visual" / "Create a card" → CREATE_PAGE workflow
- "Add a new report page" → CREATE_PAGE workflow

**Template Harvesting:**
- "Extract templates from this report" → HARVEST_TEMPLATES workflow
- "Harvest visual templates" → HARVEST_TEMPLATES workflow

**UX Review:**
- "Review the UX of this dashboard" → REVIEW_UX workflow

**QA Loop:**
- "Run the QA loop on this dashboard" → QA_LOOP workflow
- "Validate and deploy my changes" → QA_LOOP workflow

**Design Standards:**
- "How do I ensure consistent design?" → SETUP_DESIGN_STANDARDS
- "Set up design standards" → SETUP_DESIGN_STANDARDS
- "Review dashboard for consistency" → QA_LOOP with `--design-critique`
- "Check against design guidelines" → QA_LOOP with `--design-critique`
- "Configure brand guidelines" → SETUP_DESIGN_STANDARDS
- "Customize design templates" → SETUP_DESIGN_STANDARDS

---

## Pro Workflows

### SETUP_DESIGN_STANDARDS (Configure Design Guidelines)

**Use when:** User asks about consistent design, brand guidelines, or design templates for dashboards.

**Trigger phrases:**
- "How do I ensure consistent design?"
- "Set up design standards"
- "Configure brand guidelines"
- "Customize design templates"

**Process:**

1. **Check Bootstrap Status**
   - Verify project has been bootstrapped
   - Check if `.claude/powerbi-design-standards.md` already exists

2. **If Not Bootstrapped:**
   ```
   Your project needs to be bootstrapped first to get design standards.

   Run:
     & "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"

   This will create .claude/powerbi-design-standards.md in your project.
   ```

3. **If Already Exists - Guide Customization:**
   ```
   Design standards are already set up at:
     .claude/powerbi-design-standards.md

   You can customize this file to match your organization's guidelines:
   - Color palette and brand colors
   - Typography standards
   - Logo placement requirements
   - Allowed visual types
   - Accessibility rules

   Would you like help customizing any of these sections?
   ```

4. **If Needs Creation After Bootstrap:**
   - Copy from `tools/templates/powerbi-design-standards.md`
   - Guide user through customization

**Output:** Customized `.claude/powerbi-design-standards.md` file

**Next step:** "Run the QA loop with design critique" to validate dashboards against standards

---

### CREATE_PAGE (Full Dashboard Page Creation)

**Use when:** User wants to create a complete new report page with visuals, layout, and interactions.

**Why Pro?** This workflow involves sophisticated design capabilities:
- Visual type recommendation with data-driven analysis
- Research-based layout design (8px grid, F-pattern hierarchy)
- Cross-filtering and drill-through interaction design
- PBIR file generation for visuals and pages

**Trigger phrases:**
- "Create a dashboard page showing..."
- "Build a visual for..."
- "Add a sales KPI card"
- "Create a regional performance page"

**Commands:** `/create-pbi-page-specs`

**Process:**
1. **Question Analysis** - Understand the business question being answered
2. **Schema Extraction** - Analyze available tables, columns, measures
3. **Artifact Decomposition** - Identify required measures and visuals
4. **Measure Specification** - Delegates to CREATE_ARTIFACT (embedded mode) for each new measure
5. **Visual Type Recommendation** - Data-driven selection with pros/cons
6. **Layout Design** - Optimal positioning using research-based hierarchy
7. **Interaction Design** - Cross-filtering matrix, drill-through targets
8. **PBIR Generation** - Complete page.json and visual.json files
9. **Validation** - DAX and PBIR structure validation

**Output:** `findings.md` with:
- Section 2.A: Calculation Changes (measures with DAX code)
- Section 2.B: Visual Specifications (type, fields, formatting)
- Section 3: Page Layout Plan (coordinates, zones)
- Section 4: Interaction Design (cross-filtering, drill-through)
- Section 5: PBIR Page Files (complete JSON)

**Next step:** `/implement-deploy-test-pbi-project-file` to create the page

**Core Edition Alternative:**
Core users can create measures with `/create-pbi-artifact-spec`, then add visuals manually in Power BI Desktop.

See `workflows/create-pbi-page-specs.md` for full documentation.

---

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

### QA_LOOP (Automated QA Pipeline)

**Use when:** User wants to validate, deploy, and verify a Power BI report with automated error detection following a "Validate → Deploy → Inspect → Fix" cycle.

**Prerequisites:**
- PBIP project with `.Report` folder
- GitHub repository with Actions workflow for deployment
- Published report URL in Power BI Service
- Playwright MCP available
- GitHub CLI authenticated (`gh auth login`)

**New to CI/CD?** See `resources/qa-loop-prerequisites.md` for complete step-by-step setup from a desktop .pbix file.

**Commands:** `/qa-loop-pbi-dashboard`

**Process:**
1. User commits and pushes changes to GitHub
2. Monitor GitHub Actions deployment (`monitor_deployment_status.py`)
3. Inspect live report DOM for errors (`powerbi-qa-inspector` agent)
4. Report findings and offer retry or completion

**Note:** This workflow assumes code has already been validated through `/implement-deploy-test-pbi-project-file`. It focuses on runtime/deployment errors.

**Output:** `findings.md` with Section 5: QA Loop Results including:
- Deployment status and duration
- DOM inspection results with screenshots
- Issue list with recommendations

**Next step:** Fix issues and re-run QA loop, or mark complete

See `workflows/qa-loop-pbi-dashboard.md` for full documentation.

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

### QA Inspector (`powerbi-qa-inspector`)
**Handles:** DOM inspection, error detection, deployment verification

**Expertise:**
- Error container detection (grey boxes)
- Crash message identification
- Visual failure classification
- Screenshot evidence capture
- Actionable issue reporting

See `agents/powerbi-qa-inspector.md` for full documentation.

---

## Pro Quick Start

Additional examples for Pro users:

1. **Build template library?** → "Harvest visual templates from this report"
2. **Review dashboard UX?** → "Analyze the UX of my published dashboard"
3. **Test interactions?** → "Test the cross-filtering behavior"
4. **Validate and deploy?** → "Run the QA loop on my dashboard"
5. **Check for errors?** → "Inspect the deployed report for issues"

---

## Pro References

### Setup Guides (QA Loop)
- `resources/qa-loop-prerequisites.md` - Complete prerequisites checklist and setup walkthrough
- `resources/github-setup-for-powerbi.md` - Git and GitHub setup for Power BI projects
- `resources/fabric-deployment-setup.md` - Deployment pipeline configuration (Fabric Git, GitHub Actions)
- `resources/playwright-mcp-setup.md` - Playwright MCP installation for DOM inspection

### Workflows
- `workflows/create-pbi-page-specs.md` - Full page creation with visuals and layout
- `workflows/harvest-templates.md` - Template extraction workflow
- `workflows/review-ux-pbi-dashboard.md` - UX review workflow
- `workflows/qa-loop-pbi-dashboard.md` - Automated QA loop workflow

### Agents
- `agents/powerbi-playwright-tester.md` - Browser automation agent
- `agents/powerbi-ux-reviewer.md` - UX analysis agent
- `agents/powerbi-qa-inspector.md` - DOM inspection agent (with design critique)

### Design Standards & Guidelines
- `references/powerbi-design-standards.md` - Dashboard design constitution & AI critique rubric
- `references/ux-review-guidelines.md` - UX evaluation criteria
- `tools/templates/powerbi-design-standards.md` - Customizable template for projects

### Tools
- `tools/advanced/monitor_deployment_status.py` - GitHub Actions monitor
