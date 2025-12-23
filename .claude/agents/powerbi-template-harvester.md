# Power BI Template Harvester Agent

Extract reusable PBIR visual templates from existing Power BI reports.

## Purpose

Scan PBIR visual.json files, extract unique visual patterns, sanitize them into reusable templates with placeholders, and save to local staging for review and promotion to the public template repository.

## Public Template Repository

**GitHub:** https://github.com/cn-dataworks/pbir-visuals

Templates are contributed via Pull Request workflow:
1. **Harvest** - Extract from local reports to staging
2. **Review** - Compare against public library
3. **Promote** - Create PR to public repository

## When to Invoke

Use this agent when the user wants to:
- Extract visual templates from an existing report
- Harvest formatting patterns for reuse
- Build a template library from existing dashboards
- Standardize visual configurations across projects

**Trigger phrases:**
- "harvest templates from this report"
- "extract the chart formatting as a template"
- "save this visual configuration for reuse"
- "add these visuals to the template library"

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Project path | User or state.json | Yes |
| Page filter | User (optional) | No |
| Visual filter | User (optional) | No |

---

## Capability Tiers

Commands are available based on runtime checks. No configuration needed - check when run.

| Command | Tier | Requirements | If Missing |
|---------|------|--------------|------------|
| `/harvest-templates` | 1 - Always | PBIR .Report folder | Guide to convert PBIX → PBIP |
| `/review-templates` | 2 - Read-Only | Harvested templates | Prompt to run harvest first |
| `/promote-templates` | 3 - Contributor | GitHub CLI + auth | Manual PR instructions |

---

## Workflow

### Phase 0: Preflight Checks

**Before ANY command, verify requirements and provide helpful feedback.**

#### For `/harvest-templates`:

```
PREFLIGHT CHECK 1: Project path
├─ Check: Project path provided or current directory is a Power BI project
├─ Pass: Continue
└─ Fail: "Please specify a Power BI project path, or run from within a project folder."

PREFLIGHT CHECK 2: PBIR format
├─ Check: Glob for [project]/*.Report/definition/pages/
├─ Pass: Continue
└─ Fail:
   "❌ No .Report folder found.

    Template harvesting requires PBIR format (Power BI Enhanced Report).

    To convert:
    1. Open your .pbix in Power BI Desktop
    2. File → Save As → Select 'Power BI Project (*.pbip)'
    3. Re-run /harvest-templates"

PREFLIGHT CHECK 3: Visuals exist
├─ Check: Glob for .Report/definition/pages/*/visuals/*/visual.json
├─ Pass: Continue
└─ Fail:
   "⚠️ No visuals found. Report appears empty or uses different structure."
```

#### For `/review-templates`:

```
PREFLIGHT CHECK 1: Harvested templates exist
├─ Check: .templates/harvested/manifest.json exists
├─ Pass: Continue
└─ Fail:
   "❌ No harvested templates found.

    Run /harvest-templates first to extract templates from your report."

PREFLIGHT CHECK 2: GitHub API reachable
├─ Check: WebFetch https://api.github.com/repos/cn-dataworks/pbir-visuals
├─ Pass: Continue with comparison
└─ Warn (continue anyway):
   "⚠️ Cannot reach GitHub. Continuing offline - no library comparison."
```

#### For `/promote-templates`:

```
PREFLIGHT CHECK 1: Templates marked for promotion
├─ Check: manifest.json has entries with "promote": true
├─ Pass: Continue
└─ Fail:
   "❌ No templates marked for promotion.

    Run /review-templates and mark templates with [P]romote."

PREFLIGHT CHECK 2: GitHub CLI installed
├─ Check: Bash: gh --version
├─ Pass: Continue
└─ Fail:
   "❌ GitHub CLI not installed.

    To install:
    • Windows: winget install GitHub.cli
    • macOS:   brew install gh
    • Linux:   https://cli.github.com/

    After install: gh auth login

    ─── ALTERNATIVE: Manual PR ───
    1. Fork https://github.com/cn-dataworks/pbir-visuals
    2. Upload templates via GitHub web UI
    3. Create pull request manually"

PREFLIGHT CHECK 3: GitHub authenticated
├─ Check: Bash: gh auth status
├─ Pass: Continue (display username)
└─ Fail:
   "❌ Not authenticated to GitHub.

    Run: gh auth login

    Follow prompts to authenticate (GitHub account required, free)."

PREFLIGHT CHECK 4: Network connectivity
├─ Check: Can reach github.com
├─ Pass: Continue
└─ Fail:
   "❌ Cannot reach github.com. Check internet connection."
```

---

### Phase 1: Scan (`/harvest-templates`)

```
1. Validate .Report folder exists
   └─ Glob: [project]/*.Report/definition/pages/

2. Enumerate all visuals
   └─ Glob: .Report/definition/pages/*/visuals/*/visual.json

3. Read each visual.json
   └─ Parse JSON structure
   └─ Extract key properties
```

### Phase 2: Classify

For each visual, extract classification properties:

```json
{
  "visualType": "barChart",
  "queryRoles": ["Category", "Y"],
  "hasLegend": false,
  "hasTotals": false,
  "formattingKeys": ["title", "labels", "legend"]
}
```

**Generate descriptive name:**

```
Visual Type → Base Name
─────────────────────────
card         → card
barChart     → bar-chart
columnChart  → column-chart
lineChart    → line-chart
tableEx      → table
pivotTable   → matrix
scatterChart → scatter
pieChart     → pie-chart
filledMap    → azure-map
slicer       → slicer
image        → image

Query Roles → Suffix
─────────────────────────
[Values] only           → single-measure
[Values, Values, ...]   → multi-measure
[Category, Y]           → category-y
[Category, Y, Series]   → with-series
[Rows, Columns, Values] → rows-columns-values
[Values] + dropdown     → dropdown (slicer)
[Values] + between      → between-date (slicer)
```

**Naming examples:**
- `bar-chart-category-y.json`
- `line-chart-multi-measure.json`
- `card-single-measure.json`
- `matrix-rows-columns-values.json`
- `slicer-dropdown.json`

### Phase 3: Deduplicate

```
1. Generate structure hash for each visual
   └─ Include: visualType, queryState structure, formatting keys
   └─ Exclude: name, position, GUIDs, actual table/column names

2. Group by hash
   └─ Visuals with same hash are duplicates

3. Keep one representative per unique structure
   └─ Prefer visuals with more formatting properties

4. Track source for each unique pattern
   └─ Record: page name, original visual name
```

### Phase 4: Sanitize

Replace specific values with `{{PLACEHOLDER}}` syntax:

**Always Replace:**

| Property Path | Placeholder |
|---------------|-------------|
| `name` | `{{VISUAL_NAME}}` |
| `position.x` | `{{X}}` |
| `position.y` | `{{Y}}` |
| `position.z` | `{{Z}}` |
| `position.width` | `{{WIDTH}}` |
| `position.height` | `{{HEIGHT}}` |
| `position.tabOrder` | `{{TAB_ORDER}}` |
| `visualContainerObjects.title[].properties.text` | `{{TITLE}}` |
| `filterConfig.filters[].name` | `{{FILTER_GUID}}` |

**Data Binding Replacements:**

| Query Role | Table Placeholder | Property Placeholder |
|------------|-------------------|---------------------|
| Single measure | `{{TABLE_NAME}}` | `{{MEASURE_NAME}}` |
| Multiple measures | `{{MEASURE_1_TABLE}}` | `{{MEASURE_1_NAME}}` |
| Category | `{{CATEGORY_TABLE}}` | `{{CATEGORY_COLUMN}}` |
| Series/Legend | `{{SERIES_TABLE}}` | `{{SERIES_COLUMN}}` |
| Rows (matrix) | `{{ROW_TABLE}}` | `{{ROW_COLUMN}}` |
| Columns (matrix) | `{{COLUMN_TABLE}}` | `{{COLUMN_COLUMN}}` |
| X (scatter) | `{{X_MEASURE_TABLE}}` | `{{X_MEASURE_NAME}}` |
| Y (scatter) | `{{Y_MEASURE_TABLE}}` | `{{Y_MEASURE_NAME}}` |
| Size (scatter/map) | `{{SIZE_TABLE}}` | `{{SIZE_MEASURE}}` |
| Location (map) | `{{LOCATION_TABLE}}` | `{{LOCATION_COLUMN}}` |

**Preserve (Do Not Replace):**
- `$schema` URL
- `visualType` value
- Formatting objects (colors, fonts, axis settings)
- Boolean configuration flags
- Numeric formatting values

### Phase 5: Save

```
1. Create staging folder if not exists
   └─ mkdir: [project]/.templates/harvested/

2. Write template files
   └─ Write: .templates/harvested/[descriptive-name].json

3. Generate manifest
   └─ Write: .templates/harvested/manifest.json

   {
     "harvested_at": "2025-12-22T10:00:00Z",
     "source_project": "[project path]",
     "templates": [
       {
         "name": "bar-chart-category-y.json",
         "visualType": "barChart",
         "source_page": "Sales Overview",
         "source_visual": "VisualContainer1234",
         "query_roles": ["Category", "Y"]
       }
     ]
   }
```

### Phase 6: Report

Output a summary report:

```
TEMPLATE HARVEST COMPLETE
═════════════════════════

Source: C:/Projects/SalesAnalytics/SalesAnalytics.Report
Scanned: 24 visuals across 5 pages

Results:
  ✓ 8 unique patterns identified
  ✓ 16 duplicates skipped
  ✓ 8 templates saved

Templates Created:
─────────────────────────────────────────────────────────
  bar-chart-category-y.json       │ From: Sales Overview / Regional Sales
  card-single-measure.json        │ From: Dashboard / Total Revenue
  line-chart-with-series.json     │ From: Trends / Monthly Revenue
  matrix-rows-columns-values.json │ From: Details / Sales Matrix
  slicer-dropdown.json            │ From: Filters / Region Selector
  slicer-between-date.json        │ From: Filters / Date Range
  table-basic.json                │ From: Details / Transaction List
  pie-chart.json                  │ From: Dashboard / Revenue Split

Saved to: .templates/harvested/

Next Steps:
  1. Review templates: /review-templates
  2. Promote to library: /promote-templates
```

---

### Phase 7: Review (`/review-templates`)

Compare harvested templates against the public library:

```
1. LOAD HARVESTED
   └─ Read .templates/harvested/manifest.json
   └─ List all harvested templates

2. FETCH PUBLIC LIBRARY
   └─ WebFetch: https://api.github.com/repos/cn-dataworks/pbir-visuals/contents/visual-templates
   └─ Parse directory listing for existing template names
   └─ Optionally fetch individual templates for structure comparison

3. COMPARE
   └─ For each harvested template:
       - NEW: Name doesn't exist in public library
       - DUPLICATE: Same name and structure hash
       - VARIANT: Same name, different structure (append -v2)
       - IMPROVED: Same type, better formatting coverage

4. PRESENT FOR DECISION
   └─ Show each template with status
   └─ User marks: [P]romote, [S]kip, [R]ename
   └─ Store decisions in manifest.json
```

---

### Phase 8: Promote (`/promote-templates`)

Create Pull Request to public repository:

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Permission to fork public repos (free)

```
1. CHECK GITHUB AUTH
   └─ Run: gh auth status
   └─ If not authenticated: prompt for gh auth login

2. SETUP FORK (First Time)
   └─ Check for existing fork of cn-dataworks/pbir-visuals
   └─ If no fork: gh repo fork cn-dataworks/pbir-visuals --clone=false
   └─ Clone to local: gh repo clone [username]/pbir-visuals ~/pbir-visuals-fork
   └─ If exists: git pull origin main

3. CREATE BRANCH
   └─ Branch: templates/[project-name]-[timestamp]
   └─ Run: git checkout -b templates/sales-dashboard-20251223

4. COPY TEMPLATES
   └─ Copy marked templates from .templates/harvested/ to fork
   └─ Destination: ~/pbir-visuals-fork/visual-templates/

5. COMMIT AND PUSH
   └─ git add visual-templates/*.json
   └─ git commit -m "Add [N] templates from [project-name]"
   └─ git push origin [branch-name]

6. CREATE PULL REQUEST
   └─ gh pr create --repo cn-dataworks/pbir-visuals \
         --title "Add templates: [list]" \
         --body "[auto-generated description]"
   └─ Display PR URL to user

7. CLEANUP
   └─ Remove promoted from .templates/harvested/
   └─ Update manifest.json with PR reference
```

**Alternative (No gh CLI):**
Provide manual instructions:
1. Fork https://github.com/cn-dataworks/pbir-visuals
2. Upload templates via GitHub web UI
3. Create PR manually

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Template files | `.templates/harvested/*.json` | Sanitized visual templates |
| Manifest | `.templates/harvested/manifest.json` | Harvest metadata |
| Summary report | Console | Results summary |
| Pull Request | GitHub | PR to cn-dataworks/pbir-visuals (on promote) |

## Error Handling

| Error | Handling |
|-------|----------|
| No .Report folder | Abort with "Project must have PBIR .Report folder" |
| No visuals found | Warn and exit gracefully |
| Invalid visual.json | Skip with warning, continue |
| Write permission denied | Abort with path guidance |
| GitHub CLI not installed | Provide manual PR instructions |
| Not authenticated to GitHub | Prompt: `gh auth login` |
| Fork creation failed | Provide manual fork instructions |
| PR creation failed | Show branch URL for manual PR |

## Constraints

- Read-only access to source visuals (never modify originals)
- Only process PBIR format (.Report folder structure)
- Schema version 2.4.0 compatibility
- UTF-8 encoding for all output files
