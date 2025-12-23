# Visual Templates Library

Reusable PBIR visual templates with `{{PLACEHOLDER}}` syntax for creating new visuals.

## Available Templates

| Template | Visual Type | Description |
|----------|-------------|-------------|
| `card-single-measure.json` | Card | Single KPI display |
| `line-chart-category-y.json` | Line Chart | Trend over category |
| `line-chart-multi-y.json` | Line Chart | Multiple Y measures |
| `line-chart-with-series.json` | Line Chart | With legend series |
| `bar-chart-category-y.json` | Bar Chart | Horizontal bars |
| `bar-chart-with-series.json` | Bar Chart | Grouped/stacked |
| `clustered-column-multi-measure.json` | Column Chart | Side-by-side columns |
| `table-basic.json` | Table | Columnar data |
| `matrix-basic.json` | Matrix | Pivot table |
| `pie-chart.json` | Pie Chart | Part-to-whole |
| `scatter-bubble-chart.json` | Scatter/Bubble | X-Y relationship |
| `azure-map-gradient.json` | Azure Map | Filled regions |
| `azure-map-bubble.json` | Azure Map | Bubble markers |
| `slicer-between-date.json` | Slicer | Date range filter |
| `slicer-dropdown.json` | Slicer | Dropdown selection |
| `slicer-list-multiselect.json` | Slicer | Multi-select list |
| `image-static.json` | Image | Static logo/image |

## Placeholder Reference

### Position Placeholders (Always Required)

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{VISUAL_NAME}}` | Unique visual identifier | `TotalSalesCard` |
| `{{X}}` | X position in pixels | `24` |
| `{{Y}}` | Y position in pixels | `80` |
| `{{Z}}` | Z-order (layering) | `2000` |
| `{{WIDTH}}` | Width in pixels | `300` |
| `{{HEIGHT}}` | Height in pixels | `180` |
| `{{TAB_ORDER}}` | Keyboard navigation order | `0` |
| `{{TITLE}}` | Visual title text | `Total Sales` |
| `{{FILTER_GUID}}` | Filter identifier | Generate with `secrets.token_hex(10)` |

### Data Binding Placeholders

| Placeholder | Used For | Example |
|-------------|----------|---------|
| `{{TABLE_NAME}}` | Primary table | `Fact_Sales` |
| `{{MEASURE_NAME}}` | Primary measure | `Total Sales` |
| `{{CATEGORY_TABLE}}` | Category axis table | `dim_date` |
| `{{CATEGORY_COLUMN}}` | Category axis column | `month_name` |
| `{{SERIES_TABLE}}` | Legend/series table | `dim_region` |
| `{{SERIES_COLUMN}}` | Legend/series column | `region_name` |

### Multi-Measure Placeholders

For visuals with multiple measures:

| Placeholder | Description |
|-------------|-------------|
| `{{MEASURE_1_TABLE}}` | First measure table |
| `{{MEASURE_1_NAME}}` | First measure name |
| `{{MEASURE_2_TABLE}}` | Second measure table |
| `{{MEASURE_2_NAME}}` | Second measure name |

### Formatting Placeholders (Optional)

| Placeholder | Description | Default |
|-------------|-------------|---------|
| `{{FONT_SIZE}}` | Label font size | `32` (cards) |
| `{{DISPLAY_UNITS}}` | Display units (1=Auto) | `1` |

## Schema Version

All templates use PBIR schema version **2.4.0**:
```
https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json
```

## Adding New Templates

Use `/harvest-templates` to extract templates from existing reports, or manually:

1. Create visual in Power BI Desktop (PBIR format)
2. Copy the `visual.json` file
3. Replace specific values with placeholders
4. Save with descriptive name: `[visual-type]-[pattern].json`
5. Add entry to this README

## Source

Initial templates imported from [pbir-visuals](https://github.com/cn-dataworks/pbir-visuals).
