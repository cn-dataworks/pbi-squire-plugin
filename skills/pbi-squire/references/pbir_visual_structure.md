# PBIR Visual Structure

Complete guide for understanding and extracting visual layout information from Power BI Report (PBIR) files. Supports both Developer Edition (Python utility) and Analyst Edition (Claude-native extraction).

---

## Quick Reference

| Edition | Extraction Method |
|---------|-------------------|
| **Pro** | Run `extract_visual_layout.py` → formatted layout report |
| **Core** | Use Glob/Read tools → apply extraction rules below |

---

## Part 1: Visual Layout Extraction (Claude-Native)

When Python utility is not available, use these instructions to extract visual layout information.

### Step 1: Locate Report Structure

**Find the Report folder:**

```
Glob: <project>/*.Report/definition/
```

**Report structure:**

```
*.Report/
└── definition/
    ├── report.json           # Report-level config
    └── pages/
        ├── <page_id_1>/      # GUID-like folder name
        │   ├── page.json     # Page properties
        │   └── visuals/
        │       ├── <visual_id_1>/
        │       │   └── visual.json
        │       ├── <visual_id_2>/
        │       │   └── visual.json
        │       └── ...
        ├── <page_id_2>/
        │   └── ...
        └── ...
```

### Step 2: List Available Pages

**Find all page folders:**

```
Glob: <project>/*.Report/definition/pages/*/page.json
```

**Extract page display name from page.json:**

```json
{
  "displayName": "Sales Overview",
  "name": "ReportSection1234"
}
```

**Output format:**
```
Available Pages:
  ID: feaad185bc0ca0d442fb
  Name: Sales Overview
  ----------------
  ID: abc123def456
  Name: Customer Details
```

### Step 3: Extract Visual Layout

**For a specific page, find all visuals:**

```
Glob: <project>/*.Report/definition/pages/<page_id>/visuals/*/visual.json
```

**Read each visual.json file.**

### Step 4: Parse visual.json Structure

**Key properties in visual.json:**

```json
{
  "name": "abc123-visual-id",
  "position": {
    "x": 100,
    "y": 50,
    "width": 400,
    "height": 300,
    "z": 1000,
    "tabOrder": 5
  },
  "parentGroupName": "GroupName",
  "visual": {
    "visualType": "clusteredBarChart",
    "query": { ... },
    "visualContainerObjects": {
      "title": [ ... ]
    }
  }
}
```

**Extraction mapping:**

| Property | Path | Description |
|----------|------|-------------|
| Container ID | `name` | Unique visual identifier |
| X Position | `position.x` | Left edge (pixels from left) |
| Y Position | `position.y` | Top edge (pixels from top) |
| Width | `position.width` | Visual width (pixels) |
| Height | `position.height` | Visual height (pixels) |
| Z-Index | `position.z` | Stacking order (higher = on top) |
| Tab Order | `position.tabOrder` | Accessibility order |
| Visual Type | `visual.visualType` | Chart/visual type code |
| Parent Group | `parentGroupName` | Group container (if any) |

### Step 5: Extract Visual Title

**Title is nested in visualContainerObjects:**

```json
{
  "visual": {
    "visualContainerObjects": {
      "title": [
        {
          "properties": {
            "text": {
              "expr": {
                "Literal": {
                  "Value": "'Sales by Region'"
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

**Extraction path:**
```
visual.visualContainerObjects.title[0].properties.text.expr.Literal.Value
```

**Strip surrounding quotes:** `'Sales by Region'` → `Sales by Region`

### Step 6: Extract Data Fields

**Data fields are in the query structure:**

```json
{
  "visual": {
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Property": "Total Sales"
                }
              },
              "displayName": "Revenue"
            }
          ]
        },
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": {
                      "Entity": "Geography"
                    }
                  },
                  "Property": "Region"
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

**Field types:**

| Type | Detection | Format |
|------|-----------|--------|
| Measure | `field.Measure` exists | `[Measure] PropertyName` |
| Column | `field.Column` exists | `[Column] Entity.Property` |

**Extraction procedure:**

1. Iterate through `queryState` (Values, Category, Series, etc.)
2. For each role, iterate through `projections`
3. Extract field type and name

### Step 7: Canvas Dimensions

**Standard Power BI canvas:**

| Aspect | Value |
|--------|-------|
| Width | 1280 pixels |
| Height | 720 pixels |
| Aspect Ratio | 16:9 |

**Position coordinate system:**
- Origin (0,0) is top-left corner
- X increases to the right
- Y increases downward

### Step 8: Generate Layout Report

**Report format:**

```
================================================================================
Visual Layout Report - Page ID: <page_id>
Total Visuals: N
================================================================================

CANVAS DIMENSIONS: 1280px (width) x 720px (height)

EXISTING SLICERS (N):
  - Slicer Title at (X, Y) - WxH

================================================================================
VISUAL INVENTORY (sorted top-to-bottom, left-to-right)
================================================================================

1. CLUSTEREDBARCHART - Sales by Region
   Container ID: abc123
   Position: (100.0, 50.0)
   Size: 400.0px × 300.0px
   Z-index: 1000 | Tab Order: 5
   Data Fields (3):
      - [Measure] Total Sales
      - [Column] Geography.Region
      - [Column] Products.Category

2. SLICER - Date Filter
   Container ID: def456
   Position: (10.0, 10.0)
   Size: 300.0px × 60.0px
   Z-index: 2000 | Tab Order: 1
   Data Fields (1):
      - [Column] Dates.Date

================================================================================
AVAILABLE SPACE ANALYSIS FOR NEW SLICER
================================================================================

Top content starts at Y = 80.0px
Available space at top: 0 to 80.0px (Height: 80.0px)

RECOMMENDATION:
  Place new slicer at: X=10, Y=10
  Suggested size: 300px (width) × 60px (height)
================================================================================
```

---

## Part 2: Visual Type Reference

**Common visual type codes:**

| Code | Visual Type |
|------|-------------|
| `clusteredBarChart` | Clustered Bar Chart |
| `clusteredColumnChart` | Clustered Column Chart |
| `lineChart` | Line Chart |
| `areaChart` | Area Chart |
| `pieChart` | Pie Chart |
| `donutChart` | Donut Chart |
| `tableEx` | Table |
| `pivotTable` | Matrix |
| `card` | Card |
| `multiRowCard` | Multi-row Card |
| `slicer` | Slicer |
| `textbox` | Textbox |
| `shape` | Shape (rectangle, oval, etc.) |
| `image` | Image |
| `map` | Map |
| `filledMap` | Filled Map |
| `treemap` | Treemap |
| `waterfallChart` | Waterfall Chart |
| `scatterChart` | Scatter Chart |
| `gauge` | Gauge |
| `kpi` | KPI |
| `funnel` | Funnel Chart |

---

## Part 3: Page Structure

### page.json Properties

```json
{
  "name": "ReportSection",
  "displayName": "Sales Overview",
  "displayOption": 1,
  "width": 1280,
  "height": 720,
  "filters": [ ... ],
  "ordinal": 0
}
```

| Property | Description |
|----------|-------------|
| `name` | Internal page identifier |
| `displayName` | User-visible page name |
| `displayOption` | View mode (1=Fit to Page) |
| `width` | Canvas width |
| `height` | Canvas height |
| `ordinal` | Page order (0-indexed) |

### Visual Grouping

**Visuals can be grouped for formatting:**

```json
{
  "name": "GroupContainer123",
  "parentGroupName": null,
  "isGroup": true,
  "position": { ... }
}
```

**Child visuals reference parent:**

```json
{
  "name": "VisualInGroup",
  "parentGroupName": "GroupContainer123"
}
```

---

## Part 4: Checklist

Before extracting visual layout:

- [ ] Project has `.Report` folder (PBIP format)
- [ ] Report definition folder exists
- [ ] Pages folder contains page subfolders

During extraction:

- [ ] All pages enumerated
- [ ] For target page, all visuals found
- [ ] Position data extracted (x, y, width, height)
- [ ] Visual types identified
- [ ] Titles extracted
- [ ] Data fields extracted
- [ ] Slicers identified

After extraction:

- [ ] Layout report generated
- [ ] Available space calculated (for new visuals)
- [ ] Recommendations provided

---

## See Also

- `project_structure_validation.md` - Validate PBIP format first
- `visual_types.md` - Visual type reference
- `tool-fallback-pattern.md` - Pro vs Core tool usage
