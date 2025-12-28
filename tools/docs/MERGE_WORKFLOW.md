# Power BI Project Merge - Quick Start Guide

## What is this?

A workflow to compare two Power BI projects and selectively merge changes from one into the other.

## When to use it?

- You have two versions of a Power BI report
- You want to pick and choose which changes to keep
- You need to understand the business impact of differences before merging

## Quick Start

### 1. Run the command

```
/merge-powerbi-projects --main "path/to/main.pbip" --comparison "path/to/other.pbip"
```

**What each parameter means:**
- `--main`: Your baseline project (the one you want to modify)
- `--comparison`: The project containing changes you might want to merge in

### 2. Wait for analysis

The system will:
1. Find all technical differences (measures, tables, visuals, etc.)
2. Explain what each difference means in business terms
3. Present you with a choice list

### 3. Make your decisions

You'll see something like:

```
Diff diff_001: Measure - "Total Revenue"

Technical Details:
- Main Version: SUM(Sales[Amount])
- Comparison Version: SUMX(Sales, Sales[Quantity] * Sales[Price])

Business Impact:
This changes how Total Revenue is calculated. The MAIN version uses a
pre-calculated column, while COMPARISON calculates it dynamically...

Your Choice: [Respond with: "diff_001: Main" or "diff_001: Comparison"]
```

### 4. Respond with your choices

**Option A: Individual decisions**
```
diff_001: Comparison
diff_002: Main
diff_003: Comparison
```

**Option B: Choose one version for everything**
```
all Main
```
or
```
all Comparison
```

### 5. Get your merged project

The system will:
1. Create a new timestamped folder (e.g., `merged_20250128_143022.pbip`)
2. Copy your main project as the base
3. Apply your chosen changes from the comparison project
4. Give you a detailed log of what was changed

## Example Session

```
You: /merge-powerbi-projects --main "C:/reports/sales_v1.pbip" --comparison "C:/reports/sales_v2.pbip"

System: [Analyzing projects... Found 12 differences]

System: [Presenting differences with business impact...]

Diff diff_001: Measure - "YoY Growth"
Status: Modified
Main: DIVIDE([This Year], [Last Year]) - 1
Comparison: Uses SAMEPERIODLASTYEAR for time intelligence...
Business Impact: The comparison version is more accurate for fiscal year reporting...

You: diff_001: Comparison
     diff_002: Main
     ...

System: [Executing merge... Done!]
Your merged project is at: C:/reports/merged_20250128_143022.pbip
12 decisions processed, 7 changes applied, 0 errors
```

## Important Notes

### Non-Destructive
- Your original projects are NEVER modified
- The merge creates a NEW folder
- You can always go back to the originals

### What gets compared?
- **Data Model**: Tables, measures, calculated columns, relationships
- **Report**: Pages, visuals, filters
- **Files**: Any added or deleted files

### What doesn't get compared?
- Data source credentials
- Refresh schedules
- Power BI Service settings

## After the merge

1. **Open in Power BI Desktop**
   - Navigate to the merged folder
   - Open the `.pbip` file
   - Verify visuals load correctly

2. **Test thoroughly**
   - Check all measures calculate correctly
   - Verify visuals display expected data
   - Test filters and slicers

3. **Deploy if satisfied**
   - Use normal deployment process
   - Or run further comparisons if needed

## Tips for choosing

### Choose MAIN when:
- You're unsure about the comparison change
- The main version is the production version
- The comparison change might break dependencies

### Choose COMPARISON when:
- The change is a clear improvement
- It fixes a known bug
- You're intentionally adopting new features

### When in doubt:
- Choose MAIN (safer)
- Run the merge again later with different choices
- You can always re-merge!

## Common Scenarios

### Scenario 1: Merge a bug fix
```
Your main project has a broken measure. Your colleague fixed it.

Action: Choose "Comparison" for just that measure, "Main" for everything else
Result: You get the fix without adopting other changes
```

### Scenario 2: Adopt all new features
```
A new version has multiple improvements.

Action: Review each difference, choose "Comparison" for improvements
Result: Selective adoption of new features
```

### Scenario 3: Keep everything but one change
```
The comparison version is mostly good but has one bad change.

Action: Choose "Comparison" for that one diff, "Main" for all others
Result: You adopt everything except the problematic change
```

## Troubleshooting

### "Invalid project path"
- Check that paths are correct and exist
- Ensure they point to `.pbip` folders, not `.pbix` files
- Use absolute paths for clarity

### "No differences found"
- The projects are identical
- You may have compared a project to itself

### "Merge completed with warnings"
- Check the error log in the results
- Common: missing files, parse errors
- The merge still succeeded for other changes

### "Visual broken after merge"
- May indicate dependencies between changes
- Re-run merge and choose "Comparison" for related diffs
- Or manually fix in Power BI Desktop

## Getting Help

If you encounter issues:
1. Check the detailed merge log
2. Review the business impact analysis
3. Try merging in smaller batches
4. Ask for clarification on specific diffs

## Advanced Usage

### Merging multiple times
You can run the merge workflow multiple times:
```
/merge-powerbi-projects --main "merged_v1.pbip" --comparison "another_version.pbip"
```

This lets you incrementally merge changes from multiple sources.

### Comparing specific versions
Use version control to compare different commits:
```
# Check out version 1
git checkout v1

# Copy project
cp -r project.pbip /tmp/v1.pbip

# Check out version 2
git checkout v2

# Now merge
/merge-powerbi-projects --main "/tmp/v1.pbip" --comparison "project.pbip"
```

## Summary

1. **Run**: `/merge-powerbi-projects --main "path1" --comparison "path2"`
2. **Review**: Read business impact for each difference
3. **Decide**: Choose Main or Comparison for each diff
4. **Test**: Open merged project in Power BI Desktop
5. **Deploy**: Use your normal deployment process

The workflow is designed to be safe, non-destructive, and to give you full control over what changes get merged.
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
# Power BI Project Merge Workflow - Visual Diagrams

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                  /merge-powerbi-projects                        │
│                   (Main Orchestrator)                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Coordinates
             │
    ┌────────┴────────┬──────────────────┬───────────────────┐
    │                 │                  │                   │
    v                 v                  v                   v
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌───────────┐
│ Agent 1 │    │ Agent 2  │    │    HITL      │    │ Agent 3   │
│Technical│───>│Business  │───>│  (Human      │───>│Merge      │
│Auditor  │    │Analyst   │    │  Decision)   │    │Surgeon    │
└─────────┘    └──────────┘    └──────────────┘    └───────────┘
```

## Detailed Workflow Sequence

```
START: User runs command
│
├─> /merge-powerbi-projects --main "A" --comparison "B"
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: INPUT VALIDATION                                    │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ • Verify paths exist                                     │ │
│ │ • Check for .SemanticModel/ folder                       │ │
│ │ • Check for .Report/ folder                              │ │
│ │ • Detect TMDL vs BIM format                              │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
│ IF VALID
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: TECHNICAL COMPARISON                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-compare-project-code                      │ │
│ │                                                          │ │
│ │ Scans:                                                   │ │
│ │  ├─> File structure (additions/deletions)                │ │
│ │  ├─> Semantic Model                                      │ │
│ │  │    ├─> Tables (.tmdl files or model.bim)             │ │
│ │  │    ├─> Measures (DAX expressions)                    │ │
│ │  │    ├─> Columns (data types, calc columns)           │ │
│ │  │    └─> Relationships (cardinality, filters)         │ │
│ │  └─> Report                                              │ │
│ │       ├─> Pages (report.json)                           │ │
│ │       ├─> Visuals (types, data fields)                  │ │
│ │       └─> Filters (page & visual level)                 │ │
│ │                                                          │ │
│ │ Outputs: DiffReport.json                                 │ │
│ │ ┌──────────────────────────────────────────────────────┐ │ │
│ │ │ {                                                    │ │ │
│ │ │   "diffs": [                                         │ │ │
│ │ │     {                                                │ │ │
│ │ │       "diff_id": "diff_001",                         │ │ │
│ │ │       "component_type": "Measure",                   │ │ │
│ │ │       "component_name": "Total Revenue",             │ │ │
│ │ │       "status": "Modified",                          │ │ │
│ │ │       "main_version_code": "...",                    │ │ │
│ │ │       "comparison_version_code": "..."               │ │ │
│ │ │     }                                                │ │ │
│ │ │   ],                                                 │ │ │
│ │ │   "summary": {...}                                   │ │ │
│ │ │ }                                                    │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: BUSINESS IMPACT ANALYSIS                            │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-code-understander                         │ │
│ │                                                          │ │
│ │ For each diff:                                           │ │
│ │  ├─> Analyze calculation logic (DAX)                     │ │
│ │  ├─> Assess performance impact                           │ │
│ │  ├─> Identify business consequences                      │ │
│ │  ├─> Flag breaking changes                               │ │
│ │  └─> Provide decision guidance                           │ │
│ │                                                          │ │
│ │ Enriches: DiffReport with "business_impact" field        │ │
│ │ ┌──────────────────────────────────────────────────────┐ │ │
│ │ │ {                                                    │ │ │
│ │ │   "diff_id": "diff_001",                             │ │ │
│ │ │   ...                                                │ │ │
│ │ │   "business_impact": "This changes how Total         │ │ │
│ │ │   Revenue is calculated. MAIN uses pre-calculated    │ │ │
│ │ │   column, COMPARISON calculates dynamically..."      │ │ │
│ │ │ }                                                    │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: HUMAN DECISION (HITL)                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Orchestrator presents combined report to user:          │ │
│ │                                                          │ │
│ │ ╔════════════════════════════════════════════════════╗  │ │
│ │ ║ Diff diff_001: Measure - "Total Revenue"           ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Technical Details:                                 ║  │ │
│ │ ║   Main: SUM(Sales[Amount])                         ║  │ │
│ │ ║   Comparison: SUMX(Sales, Qty * Price)             ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Business Impact:                                   ║  │ │
│ │ ║   [Explanation of what changed and why it matters] ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Your Choice: diff_001: [Main or Comparison]        ║  │ │
│ │ ╚════════════════════════════════════════════════════╝  │ │
│ │                                                          │ │
│ │ User responds:                                           │ │
│ │   diff_001: Comparison                                   │ │
│ │   diff_002: Main                                         │ │
│ │   diff_003: Comparison                                   │ │
│ │   ...                                                    │ │
│ │                                                          │ │
│ │ Orchestrator parses → MergeManifest.json                 │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5: MERGE EXECUTION                                     │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-code-merger                               │ │
│ │                                                          │ │
│ │ Step 1: Create output folder                             │ │
│ │   └─> merged_20250128_143022.pbip/                       │ │
│ │                                                          │ │
│ │ Step 2: Copy main project                                │ │
│ │   └─> cp -r main.pbip/* output/                          │ │
│ │                                                          │ │
│ │ Step 3: Apply "Comparison" decisions                     │ │
│ │   For each diff where choice = "Comparison":             │ │
│ │     ├─> If Modified:                                     │ │
│ │     │    └─> Replace component in output                 │ │
│ │     ├─> If Added:                                        │ │
│ │     │    └─> Copy component to output                    │ │
│ │     └─> If Deleted:                                      │ │
│ │          └─> Remove component from output                │ │
│ │                                                          │ │
│ │ Step 4: Generate log                                     │ │
│ │   ├─> Timestamp each operation                           │ │
│ │   ├─> Record successes                                   │ │
│ │   ├─> Collect errors                                     │ │
│ │   └─> Calculate statistics                               │ │
│ │                                                          │ │
│ │ Outputs: MergeResult.json + merged project               │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5.5: TMDL FORMAT VALIDATION (Quality Gate)            │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-tmdl-syntax-validator                     │ │
│ │                                                          │ │
│ │ For each modified TMDL file:                             │ │
│ │   ├─> Check indentation consistency                      │ │
│ │   ├─> Validate property placement                        │ │
│ │   ├─> Verify tab usage                                   │ │
│ │   └─> Check measure/column structure                     │ │
│ │                                                          │ │
│ │ Output: Validation report (PASS/WARNINGS/FAIL)           │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5.6: DAX SYNTAX VALIDATION (Quality Gate)             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-dax-review-agent                          │ │
│ │                                                          │ │
│ │ For each modified DAX object:                            │ │
│ │   ├─> Validate DAX syntax                                │ │
│ │   ├─> Check function signatures                          │ │
│ │   ├─> Verify references                                  │ │
│ │   ├─> Assess runtime risks                               │ │
│ │   └─> Check context usage                                │ │
│ │                                                          │ │
│ │ Output: Validation report (PASS/WARNINGS/FAIL)           │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 6: FINAL REPORT                                        │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Orchestrator presents:                                   │ │
│ │                                                          │ │
│ │ ╔════════════════════════════════════════════════════╗  │ │
│ │ ║ Power BI Project Merge Complete                   ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Output: merged_20250128_143022.pbip                ║  │ │
│ │ ║ Decisions Applied: 25                              ║  │ │
│ │ ║ Changes Applied: 12 (7 Main, 5 Comparison)         ║  │ │
│ │ ║ Errors: 0                                          ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Section 1: Technical Diffs [summary table]         ║  │ │
│ │ ║ Section 2: Business Impact [highlights]            ║  │ │
│ │ ║ Section 3: Merge Log [detailed operations]         ║  │ │
│ │ ╚════════════════════════════════════════════════════╝  │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
END: User has merged project ready for testing/deployment
```

## Data Flow Diagram

```
┌────────────┐                    ┌────────────┐
│ Main       │                    │ Comparison │
│ Project    │                    │ Project    │
│ (path A)   │                    │ (path B)   │
└──────┬─────┘                    └──────┬─────┘
       │                                 │
       └────────────┬────────────────────┘
                    │
                    v
          ┌─────────────────┐
          │  Agent 1 Scan   │
          │  (Comparer)     │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │ DiffReport.json │
          │                 │
          │ [diff_001]      │
          │ [diff_002]      │
          │ [diff_003]      │
          │ ...             │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │  Agent 2 LLM    │
          │  (Understander) │
          └────────┬────────┘
                   │
                   v
          ┌──────────────────────┐
          │ BusinessImpact.json  │
          │                      │
          │ [diff_001 + impact]  │
          │ [diff_002 + impact]  │
          │ ...                  │
          └────────┬─────────────┘
                   │
                   v
          ┌─────────────────┐
          │  User Reviews   │
          │  & Decides      │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │MergeManifest.json│
          │                 │
          │ decisions: [    │
          │   {diff_001: C} │
          │   {diff_002: M} │
          │ ]               │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │  Agent 3 Exec   │
          │  (Merger)       │
          └────────┬────────┘
                   │
                   v
          ┌──────────────────────┐
          │ TMDL Format Validator│
          │ (Quality Gate)       │
          └────────┬─────────────┘
                   │
                   v
          ┌──────────────────────┐
          │ DAX Syntax Validator │
          │ (Quality Gate)       │
          └────────┬─────────────┘
                   │
                   v
          ┌─────────────────┐
          │ Merged Project  │
          │ + MergeLog      │
          │ + Validation    │
          └─────────────────┘
```

## Component Interaction Model

```
┌─────────────────────────────────────────────────────────┐
│              Main Orchestrator                          │
│           (merge-powerbi-projects.md)                   │
│                                                         │
│  State Management:                                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │ • main_path: string                               │ │
│  │ • comparison_path: string                         │ │
│  │ • diff_report: DiffReport                         │ │
│  │ • business_impact_report: BusinessImpactReport    │ │
│  │ • merge_manifest: MergeManifest                   │ │
│  │ • merge_result: MergeResult                       │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Control Flow:                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 1. validate_input()                               │ │
│  │ 2. invoke_agent_1() → diff_report                 │ │
│  │ 3. invoke_agent_2(diff_report) → business_report  │ │
│  │ 4. present_to_user(business_report)               │ │
│  │ 5. wait_for_user_response()                       │ │
│  │ 6. parse_decisions() → merge_manifest             │ │
│  │ 7. invoke_agent_3(merge_manifest) → merge_result  │ │
│  │ 8. generate_final_report()                        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
        │                    │                    │
        │ Task               │ Task               │ Task
        │ Invocation         │ Invocation         │ Invocation
        v                    v                    v
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│   Agent 1     │   │   Agent 2    │   │   Agent 3    │
│               │   │              │   │              │
│ Uses:         │   │ Uses:        │   │ Uses:        │
│ • Glob        │   │ • LLM        │   │ • Read       │
│ • Read        │   │ • Read       │   │ • Write      │
│ • Python util │   │ • JSON parse │   │ • Edit       │
│               │   │              │   │ • Bash       │
│ Returns:      │   │ Returns:     │   │ Returns:     │
│ DiffReport    │   │ BusinessRpt  │   │ MergeResult  │
└───────────────┘   └──────────────┘   └──────────────┘
```

## File System Operations

```
BEFORE MERGE:
─────────────

main.pbip/
├── Project.SemanticModel/
│   └── definition/
│       └── tables/
│           └── Sales.tmdl    [measure: SUM(Amount)]
└── Project.Report/
    └── report.json

comparison.pbip/
├── Project.SemanticModel/
│   └── definition/
│       └── tables/
│           └── Sales.tmdl    [measure: SUMX(Qty*Price)]
└── Project.Report/
    └── report.json


AFTER MERGE (if user chose "Comparison" for that measure):
────────────────────────────────────────────────────────────

merged_20250128_143022.pbip/
├── Project.SemanticModel/
│   └── definition/
│       └── tables/
│           └── Sales.tmdl    [measure: SUMX(Qty*Price)]  ← UPDATED
└── Project.Report/
    └── report.json

[Original main.pbip and comparison.pbip remain unchanged]
```

## Error Handling Flow

```
┌─────────────┐
│ Operation   │
└──────┬──────┘
       │
       v
   ┌───────┐
   │Try    │
   └───┬───┘
       │
       ├─> Success ──> Log & Continue
       │
       ├─> FileNotFound
       │   └─> Add to errors[], Log, Skip, Continue
       │
       ├─> ParseError
       │   └─> Add to errors[], Log, Skip, Continue
       │
       └─> CriticalError
           └─> Add to errors[], Log, ABORT
```

## Success Path Summary

```
User Command
    ↓
Validation ✓
    ↓
Technical Scan → 25 diffs found
    ↓
Business Analysis → Impact explained
    ↓
User Reviews → Makes 25 decisions
    ↓
Merge Execution → 12 changes applied
    ↓
Validation ✓
    ↓
Final Report + Merged Project
    ↓
User Tests in Power BI Desktop
    ↓
Deployment to Production
```

## Agent Autonomy Levels

```
Agent 1: FULLY AUTONOMOUS
├─ Scans files without user input
├─ Parses TMDL/BIM autonomously
└─ Returns complete report

Agent 2: FULLY AUTONOMOUS
├─ Analyzes each diff independently
├─ Generates business explanations
└─ No user interaction required

HITL: HUMAN REQUIRED
├─ Reviews all information
├─ Makes final decisions
└─ Cannot be skipped

Agent 3: FULLY AUTONOMOUS
├─ Executes decisions faithfully
├─ Handles errors gracefully
└─ Returns complete result
```

This visual representation shows how the three autonomous agents work together under orchestration, with human judgment at the critical decision point.
