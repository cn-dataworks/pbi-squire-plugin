# Power BI Template Harvester Agent

Extract reusable PBIR visual templates from existing Power BI reports.

## Purpose

Scan PBIR visual.json files, extract unique visual patterns, sanitize them into reusable templates with placeholders, and save to local staging for review and promotion.

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

## Workflow

### Phase 1: Scan

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

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Template files | `.templates/harvested/*.json` | Sanitized visual templates |
| Manifest | `.templates/harvested/manifest.json` | Harvest metadata |
| Summary report | Console | Results summary |

## Error Handling

| Error | Handling |
|-------|----------|
| No .Report folder | Abort with "Project must have PBIR .Report folder" |
| No visuals found | Warn and exit gracefully |
| Invalid visual.json | Skip with warning, continue |
| Write permission denied | Abort with path guidance |

## Constraints

- Read-only access to source visuals (never modify originals)
- Only process PBIR format (.Report folder structure)
- Schema version 2.4.0 compatibility
- UTF-8 encoding for all output files
