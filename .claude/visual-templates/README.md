# PBIR Visual Templates

This folder contains JSON templates for Power BI Enhanced Report Format (PBIR) visuals. These templates use the correct `queryState/projections` structure required for PBIR visual.json files.

## Schema Version

All templates use schema version **2.4.0**:
```
https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json
```

## Available Templates

| Template | Visual Type | Description |
|----------|-------------|-------------|
| `card-single-measure.json` | Card | Single measure display with formatting |
| `line-chart-category-y.json` | Line Chart | Category on X-axis, single measure on Y-axis |
| `line-chart-multi-y.json` | Line Chart | Category on X-axis, multiple measures on Y-axis |
| `line-chart-with-series.json` | Line Chart | Category on X-axis, Series for legend grouping, single Y measure |
| `bar-chart-category-y.json` | Bar Chart | Horizontal bars with category and measure |
| `bar-chart-with-series.json` | Bar Chart | Grouped/stacked bars with category, series, and measure |
| `clustered-column-multi-measure.json` | Clustered Column | Multiple measures side-by-side |
| `table-basic.json` | Table | Basic table with columns and measures |
| `matrix-basic.json` | Matrix | Pivot table with rows, columns, and values |
| `pie-chart.json` | Pie Chart | Category slices with measure values |
| `scatter-bubble-chart.json` | Scatter/Bubble | X/Y measures with category and optional bubble size |
| `azure-map-gradient.json` | Azure Map | Filled map with gradient coloring |
| `azure-map-bubble.json` | Azure Map | Bubble map with clustering support |
| `image-static.json` | Image | Static image/logo from registered resources |
| `slicer-between-date.json` | Slicer | Date range slicer (Between mode) |
| `slicer-dropdown.json` | Slicer | Dropdown single-select slicer |
| `slicer-list-multiselect.json` | Slicer | List multi-select slicer |

## Template Placeholders

All templates use `{{PLACEHOLDER}}` syntax for values that need to be replaced:

### Common Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{VISUAL_NAME}}` | Unique visual identifier | `TotalSalesCard` |
| `{{X}}`, `{{Y}}` | Position coordinates | `16`, `80` |
| `{{Z}}` | Z-order (stacking) | `2000` |
| `{{WIDTH}}`, `{{HEIGHT}}` | Dimensions in pixels | `240`, `120` |
| `{{TAB_ORDER}}` | Keyboard navigation order | `0`, `1`, `2`... |
| `{{TITLE}}` | Visual title text | `Total Sales` |
| `{{FILTER_GUID}}` | Random 20-char hex string | `640f9cd40ada36475294` |

### Data Binding Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{TABLE_NAME}}` | Source table name | `Fact_Sales` |
| `{{MEASURE_NAME}}` | Measure name | `Total Revenue` |
| `{{MEASURE_TABLE}}` | Table containing measure | `Fact_Sales` |
| `{{MEASURE_1_TABLE}}`, `{{MEASURE_1_NAME}}` | First measure (multi-measure visuals) | `Fact_Sales`, `Units Sold` |
| `{{MEASURE_2_TABLE}}`, `{{MEASURE_2_NAME}}` | Second measure | `Fact_Sales`, `Revenue` |
| `{{MEASURE_3_TABLE}}`, `{{MEASURE_3_NAME}}` | Third measure | `Fact_Sales`, `Profit` |
| `{{CATEGORY_TABLE}}` | Dimension table (X-axis) | `dim_date` |
| `{{CATEGORY_COLUMN}}` | Dimension column | `month_name` |
| `{{SERIES_TABLE}}` | Series/Legend table (bar/column with series) | `Fact_Sales` |
| `{{SERIES_COLUMN}}` | Series/Legend column | `region` |
| `{{ROW_TABLE}}` | Matrix row dimension table | `dim_product` |
| `{{ROW_COLUMN}}` | Matrix row column | `product_name` |
| `{{COLUMN_TABLE}}` | Matrix column dimension table | `dim_date` |
| `{{COLUMN_COLUMN}}` | Matrix column column | `year` |
| `{{COLUMN_1_TABLE}}`, `{{COLUMN_1_NAME}}` | Table first column | `Fact_Sales`, `region` |
| `{{LOCATION_TABLE}}` | Geographic dimension table | `dim_customer` |
| `{{LOCATION_COLUMN}}` | Location column | `state` |
| `{{X_MEASURE_TABLE}}`, `{{X_MEASURE_NAME}}` | Scatter X-axis measure | `Fact_Sales`, `Units Sold` |
| `{{Y_MEASURE_TABLE}}`, `{{Y_MEASURE_NAME}}` | Scatter Y-axis measure | `Fact_Sales`, `Profit Margin` |
| `{{SIZE_MEASURE_TABLE}}`, `{{SIZE_MEASURE_NAME}}` | Bubble size measure | `Fact_Sales`, `Revenue` |
| `{{TOOLTIP_MEASURE_TABLE}}`, `{{TOOLTIP_MEASURE_NAME}}` | Tooltip measure | `Fact_Sales`, `Count` |
| `{{IMAGE_FILE_NAME}}` | Registered resource image file | `logo_abc123.png` |

### Formatting Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{FONT_SIZE}}` | Font size (append D) | `28` → `"28D"` |
| `{{DISPLAY_UNITS}}` | Display units (1=None) | `1` |
| `{{STROKE_WIDTH}}` | Line thickness | `2` |
| `{{SHOW_MARKERS}}` | Show data markers | `true` |
| `{{SHOW_DATA_LABELS}}` | Show data labels on chart | `true` |
| `{{LEGEND_POSITION}}` | Legend position | `Top`, `Bottom`, `Left`, `Right` |
| `{{SHOW_CATEGORY_AXIS_TITLE}}` | Show X-axis title | `true`, `false` |
| `{{SHOW_VALUE_AXIS_TITLE}}` | Show Y-axis title | `true`, `false` |
| `{{SHOW_GRID_VERTICAL}}` | Show vertical grid lines (table) | `true` |
| `{{SHOW_TOTALS}}` | Show totals row (table) | `true`, `false` |
| `{{SHOW_ROW_SUBTOTALS}}` | Show row subtotals (matrix) | `true` |
| `{{SHOW_COLUMN_SUBTOTALS}}` | Show column subtotals (matrix) | `true` |
| `{{MAP_TRANSPARENCY}}` | Map transparency (append L) | `40` → `"40L"` |
| `{{MEASURE_1_COLOR}}` | Hex color code | `#19F5E2` |
| `{{SHOW_LEGEND}}` | Show legend | `true`, `false` |
| `{{SHOW_LABELS}}` | Show data labels (pie chart) | `true`, `false` |
| `{{LABEL_STYLE}}` | Pie label style | `Category`, `Data value`, `Percent of total`, `All detail labels` |
| `{{BACKGROUND_TRANSPARENCY}}` | Background transparency (0-100) | `0` |
| `{{SHOW_X_AXIS_TITLE}}` | Show X-axis title (scatter) | `true`, `false` |
| `{{SHOW_Y_AXIS_TITLE}}` | Show Y-axis title (scatter) | `true`, `false` |
| `{{SHOW_CATEGORY_LABELS}}` | Show category labels | `true`, `false` |
| `{{MAP_STYLE}}` | Azure Map style | `road`, `aerial`, `grayscale_dark`, `grayscale_light` |
| `{{SHOW_STYLE_PICKER}}` | Show map style picker | `true`, `false` |
| `{{SHOW_NAV_CONTROLS}}` | Show map navigation controls | `true`, `false` |
| `{{SHOW_SELECTION_CONTROL}}` | Show map selection control | `true`, `false` |
| `{{ENABLE_CLUSTERING}}` | Enable bubble clustering | `true`, `false` |
| `{{CLUSTER_RADIUS}}` | Cluster bubble radius (append L) | `23` → `"23L"` |
| `{{MIN_BUBBLE_RADIUS}}` | Minimum bubble radius (append L) | `6` → `"6L"` |

## Query Structure Reference

### Role Names by Visual Type

```
Card:                { Values: [...] }
Line Chart:          { Category: [...], Y: [...] }
Line Chart (Series): { Category: [...], Series: [...], Y: [...] }
Bar Chart:           { Category: [...], Y: [...] }
Bar Chart (Series):  { Category: [...], Series: [...], Y: [...] }
Column Chart:        { Category: [...], Y: [...] }
Pie Chart:           { Category: [...], Y: [...] }
Scatter/Bubble:      { Category: [...], X: [...], Y: [...], Size: [...] }
Table:               { Values: [...] }  // columns and measures together
Matrix:              { Rows: [...], Columns: [...], Values: [...] }
Azure Map (Gradient):{ Category: [...], Tooltips: [...] }
Azure Map (Bubble):  { Category: [...], Size: [...], Tooltips: [...] }
Image:               // No query - uses ResourcePackageItem
Slicer:              { Values: [...] }
```

### Column vs Measure References

**Column (dimension):**
```json
{
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "TableName" } },
      "Property": "column_name"
    }
  },
  "queryRef": "TableName.column_name",
  "nativeQueryRef": "column_name",
  "active": true
}
```

**Measure:**
```json
{
  "field": {
    "Measure": {
      "Expression": { "SourceRef": { "Entity": "TableName" } },
      "Property": "Measure Name"
    }
  },
  "queryRef": "TableName.Measure Name",
  "nativeQueryRef": "Measure Name"
}
```

## Filter GUID Generation

Generate random 20-character hex strings for `filterConfig.filters[].name`:

```python
import secrets
filter_guid = secrets.token_hex(10)  # e.g., "640f9cd40ada36475294"
```

## Slicer Modes

| Mode | Value | Description |
|------|-------|-------------|
| Between | `'Between'` | Date range picker |
| Dropdown | `'Dropdown'` | Single-select dropdown |
| Basic | `'Basic'` | List with checkboxes |

## Usage Example

To create a new card visual:

1. Copy `card-single-measure.json`
2. Replace placeholders:
   ```json
   "{{VISUAL_NAME}}" → "TotalRevenueCard"
   "{{TABLE_NAME}}" → "Fact_Sales"
   "{{MEASURE_NAME}}" → "Total Revenue"
   "{{TITLE}}" → "Total Revenue"
   "{{X}}" → "16"
   "{{Y}}" → "80"
   ...
   ```
3. Save as `TotalRevenueCard/visual.json` in the page's visuals folder

## Adding New Templates

When you create a new visual type in Power BI Desktop:

1. Save the project (PBIR format)
2. Navigate to `.Report/definition/pages/[PageName]/visuals/[VisualName]/visual.json`
3. Copy the file
4. Replace specific values with `{{PLACEHOLDER}}` syntax
5. Add to this folder with descriptive name
6. Update this README

## Templates Needed

The following visual types don't have templates yet:

- [x] Table *(added: table-basic.json)*
- [x] Matrix *(added: matrix-basic.json)*
- [x] Pie Chart *(added: pie-chart.json)*
- [ ] Donut Chart
- [x] Scatter Chart *(added: scatter-bubble-chart.json)*
- [ ] Gauge
- [ ] KPI
- [ ] Treemap
- [x] Stacked Bar/Column *(covered by bar-chart-with-series.json)*
- [ ] Area Chart
- [ ] Waterfall Chart
- [ ] Funnel Chart
- [x] Image *(added: image-static.json)*
- [x] Azure Map Bubble *(added: azure-map-bubble.json)*
- [x] Line Chart with Series *(added: line-chart-with-series.json)*

## Source

Templates extracted from working PBIR visuals created in Power BI Desktop (November 2024).
