# Project Comparison Guide

Complete guide for comparing and merging Power BI projects. Supports both Developer Edition (Python utility) and Analyst Edition (Claude-native comparison).

---

## Quick Reference

| Edition | Comparison Method |
|---------|-------------------|
| **Pro** | Run `pbi_merger_utils.py` → structured diff report |
| **Core** | Use Read/Grep tools → apply comparison rules below |

---

## Part 1: Project Comparison (Claude-Native)

When Python utility is not available, use these instructions to compare projects directly.

### Step 1: Enumerate Objects

**Find semantic model folders:**

```
Main Project:
  Glob: <main_path>/*.SemanticModel/definition/

Comparison Project:
  Glob: <comparison_path>/*.SemanticModel/definition/
```

**Find all TMDL table files:**

```
Glob: <semantic_model>/tables/*.tmdl
```

### Step 2: Extract Measures from TMDL

**Pattern to match measure definitions:**

```regex
measure\s+['"]?([^\s'"]+)['"]?\s*=\s*(.*?)(?=\n\s*(?:measure|column|partition|annotation-group|\Z))
```

**Extraction procedure:**

1. Read the TMDL file
2. Find all `measure` blocks
3. Extract:
   - **Measure name:** Text after `measure` (may be quoted)
   - **DAX expression:** Content after `=` until next object or properties

**Example TMDL:**
```tmdl
measure 'Total Sales' =
    SUMX(Sales, [Amount] * [Quantity])
    formatString: "$#,##0"
    lineageTag: abc-123

measure 'YoY Growth' =
    DIVIDE([Total Sales] - [Prior Year Sales], [Prior Year Sales])
```

**Extracted measures:**
```
{
  "Total Sales": "SUMX(Sales, [Amount] * [Quantity])",
  "YoY Growth": "DIVIDE([Total Sales] - [Prior Year Sales], [Prior Year Sales])"
}
```

### Step 3: Extract Columns from TMDL

**Pattern to match column definitions:**

```regex
column\s+['"]?([^\s'"]+)['"]?(?:\s*:\s*([^\n]+))?\s*\n((?:\s+.*\n)*)
```

**Extraction procedure:**

1. Find all `column` blocks
2. Extract:
   - **Column name:** Text after `column`
   - **Data type:** Text after `:` (if present)
   - **Is calculated:** Check if `expression` property exists

**Example TMDL:**
```tmdl
column CustomerID : String
    sourceColumn: CustomerID
    lineageTag: def-456

column FullName
    expression: [FirstName] & " " & [LastName]
    lineageTag: ghi-789
```

**Extracted columns:**
```
{
  "CustomerID": { "dataType": "String", "isCalculated": false },
  "FullName": { "dataType": null, "isCalculated": true }
}
```

### Step 4: Extract Table Names

**Pattern to match table declarations:**

```regex
^table\s+['"]?([^\s'"]+)['"]?
```

**Read first line of TMDL file to get table name.**

### Step 5: Compare Objects

**For each table file in both projects:**

1. Extract measures from main version
2. Extract measures from comparison version
3. Classify each measure:

| Condition | Status |
|-----------|--------|
| In comparison only | **Added** |
| In main only | **Deleted** |
| In both, DAX identical | **Unchanged** |
| In both, DAX different | **Modified** |

**Comparison algorithm:**

```
main_measures = extract_measures(main_file)
comp_measures = extract_measures(comparison_file)

for name in comp_measures:
    if name not in main_measures:
        status = "Added"
    elif main_measures[name] != comp_measures[name]:
        status = "Modified"
    else:
        status = "Unchanged"

for name in main_measures:
    if name not in comp_measures:
        status = "Deleted"
```

### Step 6: Compare File Structure

**Check for added/deleted files:**

```
main_files = glob(<main_path>/**/*) - relative paths
comp_files = glob(<comparison_path>/**/*) - relative paths

added_files = comp_files - main_files
deleted_files = main_files - comp_files
```

### Step 7: Generate Diff Report

**Diff entry format:**

```json
{
  "diff_id": "diff_001",
  "component_type": "Measure",
  "component_name": "Total Sales",
  "file_path": "tables/Sales.tmdl",
  "status": "Modified",
  "main_version_code": "SUM(Sales[Amount])",
  "comparison_version_code": "SUMX(Sales, [Amount] * [Quantity])",
  "metadata": {
    "parent_table": "Sales"
  }
}
```

**Report format:**

```
================================================================================
PROJECT COMPARISON REPORT
================================================================================
Main Project: <main_path>
Comparison Project: <comparison_path>

SUMMARY:
  Total Differences: N
  Added: A
  Modified: M
  Deleted: D

BREAKDOWN BY TYPE:
  Measures: X
  Columns: Y
  Tables: Z
  Files: W

================================================================================
DIFFERENCES
================================================================================

[diff_001] MEASURE: Total Sales (Modified)
  Table: Sales
  File: tables/Sales.tmdl

  MAIN VERSION:
    SUM(Sales[Amount])

  COMPARISON VERSION:
    SUMX(Sales, [Amount] * [Quantity])

--------------------------------------------------------------------------------

[diff_002] MEASURE: New Metric (Added)
  Table: Sales
  File: tables/Sales.tmdl

  COMPARISON VERSION:
    CALCULATE([Total Sales], FILTER(Dates, [IsCurrentYear] = TRUE))

--------------------------------------------------------------------------------

[diff_003] TABLE: NewTable (Added)
  File: tables/NewTable.tmdl

================================================================================
```

---

## Part 2: Merge Decision Framework

After comparison, user selects which version to keep for each difference.

### Merge Manifest Structure

```json
{
  "main_project_path": "<path>",
  "comparison_project_path": "<path>",
  "output_project_path": "<path>",
  "diff_report": { ... },
  "merge_decisions": [
    { "diff_id": "diff_001", "choice": "Comparison" },
    { "diff_id": "diff_002", "choice": "Main" },
    { "diff_id": "diff_003", "choice": "Comparison" }
  ]
}
```

### Decision Options

| Choice | Meaning |
|--------|---------|
| **Main** | Keep main project version (no change) |
| **Comparison** | Apply comparison version to output |

### Merge Execution

**For "Main" choices:** No action (output starts as copy of main)

**For "Comparison" choices:**

1. If status = "Added":
   - Copy new content from comparison to output

2. If status = "Modified":
   - Replace main version with comparison version in output

3. If status = "Deleted":
   - Remove the item from output (if user confirms)

### Applying Measure Changes

**To replace a measure in TMDL:**

```
Pattern: measure\s+{escaped_name}\s*=\s*.*?(?=\n\s*(?:measure|column|partition|annotation-group|\Z))

Replacement: new_measure_definition
```

**Use Edit tool to perform the replacement.**

---

## Part 3: Comparison Report Format

### Full Report Template

```
================================================================================
POWER BI PROJECT COMPARISON
================================================================================

PROJECTS:
  Main:       <main_project>
  Comparison: <comparison_project>
  Generated:  <timestamp>

================================================================================
EXECUTIVE SUMMARY
================================================================================

  Total Differences Found: N

  | Type    | Added | Modified | Deleted |
  |---------|-------|----------|---------|
  | Measures|   A   |    M     |    D    |
  | Columns |   A   |    M     |    D    |
  | Tables  |   A   |    M     |    D    |
  | Files   |   A   |    M     |    D    |

================================================================================
DETAILED DIFFERENCES
================================================================================

--- MEASURES ---

[diff_001] Total Sales (Modified)
  Location: Sales table (tables/Sales.tmdl)

  Main Version:
  ```dax
  SUM(Sales[Amount])
  ```

  Comparison Version:
  ```dax
  SUMX(Sales, [Amount] * [Quantity])
  ```

  Decision: [ ] Main  [ ] Comparison

---

[diff_002] New KPI (Added)
  Location: KPIs table (tables/KPIs.tmdl)

  Comparison Version:
  ```dax
  DIVIDE([Actual], [Target])
  ```

  Decision: [ ] Skip  [ ] Add

================================================================================
MERGE RECOMMENDATIONS
================================================================================

1. Review all Modified measures carefully
2. Test Added measures before merging
3. Confirm Deleted items are intentional
4. After merge, validate in Power BI Desktop

================================================================================
```

---

## Part 4: Checklist

Before comparing projects:

- [ ] Both projects are valid (run project_structure_validation first)
- [ ] Both projects are same format (PBIP or pbi-tools)
- [ ] Semantic model paths identified

During comparison:

- [ ] All tables enumerated
- [ ] All measures extracted
- [ ] All columns extracted (if applicable)
- [ ] File structure compared

After comparison:

- [ ] Diff report generated
- [ ] User reviewed all differences
- [ ] Merge decisions recorded
- [ ] Merge executed (if requested)
- [ ] Output validated in Power BI Desktop

---

## See Also

- `project_structure_validation.md` - Validate project format before comparison
- `tmdl_partition_structure.md` - TMDL format rules
- `tool-fallback-pattern.md` - Pro vs Core tool usage
