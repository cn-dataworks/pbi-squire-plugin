# Power BI Project Merge Workflow

## Overview

This workflow provides a semi-automated, human-in-the-loop system for comparing and merging two Power BI project folders (.pbip). It analyzes technical differences, provides business impact analysis, and executes selective merging based on user decisions.

## Architecture

The workflow consists of:
1. **Main Orchestrator**: `/merge-powerbi-projects` slash command
2. **Three Specialized Agents**:
   - `powerbi-compare-project-code`: Technical Auditor
   - `powerbi-code-understander`: Business Analyst
   - `powerbi-code-merger`: Merge Surgeon

## Workflow Phases

### Phase 1: Input Validation
The main command validates that both project paths exist and contain valid .pbip structures.

### Phase 2: Technical Comparison
The `powerbi-compare-project-code` agent:
- Scans both project folders
- Identifies all technical differences in:
  - Tables, measures, columns, relationships (from TMDL or model.bim)
  - Report pages, visuals, filters (from report.json)
  - File additions/deletions
- Outputs: `DiffReport` JSON

### Phase 3: Business Impact Analysis
The `powerbi-code-understander` agent:
- Receives the technical diff report
- Adds business-level explanations for each difference
- Explains consequences of choosing each version
- Outputs: `BusinessImpactReport` JSON

### Phase 4: User Decision (HITL)
The main command:
- Presents both technical and business information
- Asks user to choose between Main or Comparison for each diff
- Accepts natural language responses

### Phase 5: Merge Execution
The `powerbi-code-merger` agent:
- Creates a new timestamped output folder
- Copies main project as base
- Selectively applies comparison changes based on user choices
- Generates detailed merge log
- Outputs: `MergeResult` JSON

## Usage

### Basic Invocation

```
/merge-powerbi-projects --main "C:/path/to/main.pbip" --comparison "C:/path/to/comparison.pbip"
```

### User Response Format

When presented with differences, respond with:

**Individual decisions:**
```
diff_001: Comparison
diff_002: Main
diff_003: Comparison
```

**Bulk decisions:**
```
all Main
```
or
```
all Comparison
```

## Data Flow

```
User Input (2 paths)
  ↓
DiffReport.json
  ↓
BusinessImpactReport.json
  ↓
User Decisions (natural language)
  ↓
MergeManifest.json
  ↓
MergeResult.json + Merged .pbip folder
```

## File Structure

```
.claude/
├── commands/
│   └── merge-powerbi-projects.md       # Main orchestrator
├── agents/
│   ├── powerbi-compare-project-code.md  # Technical Auditor
│   ├── powerbi-code-understander.md     # Business Analyst
│   └── powerbi-code-merger.md           # Merge Surgeon
└── tools/
    ├── pbi_merger_utils.py              # Python utilities
    ├── pbi_merger_schemas.json          # JSON schemas
    └── README_MERGE_WORKFLOW.md         # This file
```

## JSON Schemas

### DiffReport Schema

```json
{
  "diffs": [
    {
      "diff_id": "diff_001",
      "component_type": "Measure",
      "component_name": "Total Revenue",
      "file_path": "Project.SemanticModel/definition/tables/Sales.tmdl",
      "status": "Modified",
      "main_version_code": "SUM(Sales[Amount])",
      "comparison_version_code": "SUMX(Sales, Sales[Quantity] * Sales[Price])",
      "metadata": {
        "parent_table": "Sales"
      }
    }
  ],
  "summary": {
    "total_diffs": 1,
    "added": 0,
    "modified": 1,
    "deleted": 0,
    "breakdown": {
      "Measure": 1
    }
  }
}
```

### BusinessImpactReport Schema

Same as DiffReport, but each diff entry includes:
```json
{
  "business_impact": "This changes how Total Revenue is calculated..."
}
```

### MergeManifest Schema

```json
{
  "merge_decisions": [
    {"diff_id": "diff_001", "choice": "Comparison"}
  ],
  "main_project_path": "C:/path/to/main.pbip",
  "comparison_project_path": "C:/path/to/comparison.pbip",
  "output_project_path": "C:/path/to/merged_20250128_143022.pbip",
  "diff_report": { /* DiffReport object */ }
}
```

### MergeResult Schema

```json
{
  "status": "success",
  "output_path": "C:/path/to/merged_20250128_143022.pbip",
  "merge_log": "...",
  "statistics": {
    "total_decisions": 25,
    "main_chosen": 13,
    "comparison_chosen": 12,
    "files_modified": 8,
    "components_added": 2,
    "components_modified": 9,
    "components_deleted": 1,
    "errors": 0
  },
  "errors": []
}
```

## Component Types

The workflow recognizes these Power BI component types:
- **Measure**: DAX measure
- **CalculatedColumn**: DAX calculated column
- **CalculatedTable**: DAX calculated table
- **Table**: Data source table
- **Column**: Table column
- **Relationship**: Model relationship
- **Visual**: Report visual/chart
- **Page**: Report page
- **Filter**: Report or page-level filter
- **Parameter**: What-if or field parameter
- **Role**: RLS role
- **Expression**: M expression or shared DAX
- **File**: Generic file add/delete
- **Error**: Parse error

## Implementation Details

### TMDL Parsing

The workflow can parse TMDL format projects:
- Extracts measures, columns, tables from `.tmdl` files
- Uses regex patterns to identify components
- Handles both simple and complex DAX expressions

### BIM Parsing

The workflow can parse model.bim JSON:
- Loads and navigates JSON structure
- Compares measures, tables, relationships
- Preserves JSON formatting (2-space indent)

### Report JSON Parsing

- Parses `report.json` for pages and visuals
- Compares visual configurations
- Handles page-level and visual-level filters

## Error Handling

The workflow handles these error scenarios:
- **FileNotFound**: Missing files are logged and skipped
- **ParseError**: Invalid JSON/TMDL is flagged but doesn't stop the merge
- **ComponentNotFound**: Missing components are logged as warnings
- **CopyError**: Critical error that stops the merge
- **ApplyError**: Logged but allows merge to continue

All errors are collected in the `errors` array of the final result.

## Non-Destructive Workflow

The merge process NEVER modifies the original projects:
1. Main project is copied to a new timestamped folder
2. Changes are applied to the copy
3. Original main and comparison projects remain untouched

## Best Practices

### For Users

1. **Review thoroughly**: The business impact analysis helps, but always review critical changes
2. **Test merged project**: Open in Power BI Desktop and validate before deployment
3. **Backup originals**: Although the workflow is non-destructive, always have backups
4. **Incremental merges**: For large projects, consider merging in phases

### For Developers

1. **Extend component types**: Add new component types to the enum as needed
2. **Enhance parsers**: The TMDL/BIM parsers can be extended for more sophisticated comparisons
3. **Add validation**: Consider adding semantic validation (e.g., DAX syntax checking)
4. **Improve business analysis**: Enhance the business impact prompts with domain-specific knowledge

## Limitations

Current limitations:
- Does not validate DAX syntax
- Visual comparisons are basic (doesn't deep-compare all properties)
- M query comparisons are file-level only
- No automatic conflict resolution
- Requires manual testing after merge

## Future Enhancements

Potential improvements:
- DAX syntax validation
- Automated testing of merged project
- Intelligent conflict resolution suggestions
- Version control integration (git diff-like view)
- Rollback capability
- Batch merge support (merging multiple projects)

## Troubleshooting

### "Agent failed to parse project"
- Verify both paths are valid .pbip folders
- Check that semantic model folder exists
- Ensure either TMDL or model.bim is present

### "Merge completed with errors"
- Review the errors array in the result
- Common issues: missing files, parse errors
- Check the merge log for details

### "Visual not found in merged project"
- May indicate structural differences between projects
- Manually inspect the report.json in both projects
- Consider using "Main" for that diff if critical

## Support Files

- `pbi_merger_utils.py`: Python library with parsers and merge logic
- `pbi_merger_schemas.json`: JSON schema definitions for validation
- Agent markdown files: Detailed instructions for each specialized agent

## Version History

- **v1.0** (2025-01-28): Initial implementation with TMDL and BIM support
