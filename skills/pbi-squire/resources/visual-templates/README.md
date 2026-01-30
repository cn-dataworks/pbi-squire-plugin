# Visual Templates

17 PBIR visual templates bundled with the skill. These templates use schema v2.4.0 and the `queryState/projections` structure.

## Available Templates

| Template | Visual Type | Description |
|----------|-------------|-------------|
| `azure-map-bubble.json` | Azure Map | Bubble map with size by measure |
| `azure-map-gradient.json` | Azure Map | Filled/choropleth map with gradient |
| `bar-chart-category-y.json` | Bar Chart | Category axis with single measure |
| `bar-chart-with-series.json` | Bar Chart | Category axis with series/legend |
| `card-single-measure.json` | Card | Single KPI measure display |
| `clustered-column-multi-measure.json` | Column Chart | Multiple measures side-by-side |
| `image-static.json` | Image | Static image visual |
| `line-chart-category-y.json` | Line Chart | Category axis with single measure |
| `line-chart-multi-y.json` | Line Chart | Multiple Y-axis measures |
| `line-chart-with-series.json` | Line Chart | Category with series/legend |
| `matrix-basic.json` | Matrix | Rows, columns, and values |
| `pie-chart.json` | Pie Chart | Category with single measure |
| `scatter-bubble-chart.json` | Scatter | X, Y measures with optional size |
| `slicer-between-date.json` | Slicer | Date range (between) slicer |
| `slicer-dropdown.json` | Slicer | Dropdown single-select |
| `slicer-list-multiselect.json` | Slicer | List with multi-select |
| `table-basic.json` | Table | Basic table with columns |

## How Templates Work

1. **Agents use templates** when generating new visuals (e.g., `/create-pbi-artifact-spec`)
2. **Templates are bundled** with the skill - no network fetch required
3. **Placeholders** like `{{MEASURE_NAME}}` are replaced with actual values

## Contributing New Templates

1. **Harvest** templates from your reports: `/harvest-templates`
2. **Review** and mark for promotion: `/review-templates`
3. **Submit PR** to public repo: `/promote-templates`
4. **Maintainer** merges PR to `cn-dataworks/pbir-visuals`
5. **Maintainer** copies into skill and releases update
6. **Users** get new templates via `/plugin update`

## Public Repository

Community contributions go to: https://github.com/cn-dataworks/pbir-visuals

This is the staging ground for new templates before they're bundled into the skill.

## Template Updates

Templates are updated when:
- You run `/plugin update pbi-squire@cn-dataworks-pbi-squire-plugin`
- This pulls the latest skill version which includes updated templates

Templates are versioned with the skill to ensure compatibility.
