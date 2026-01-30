# Project Structure Validation

Complete guide for validating Power BI project folder structures. Supports both Developer Edition (Python validator) and Analyst Edition (Claude-native validation).

---

## Quick Reference

| Edition | Validation Method |
|---------|-------------------|
| **Pro** | Run `pbi_project_validator.py` → structured JSON result |
| **Core** | Use Glob/Read tools → apply detection rules below |

---

## Part 1: Format Detection (Claude-Native)

When Python validator is not available, use these instructions to detect and validate project format.

### Step 1: Detect Project Format

**Check for these indicators in order:**

| Format | Detection Method | Glob Pattern |
|--------|------------------|--------------|
| **PBIX file** | Path ends with `.pbix` | `*.pbix` |
| **PBIP (Power BI Project)** | Has `.pbip` file AND `.SemanticModel` folder | `*.pbip` + `*.SemanticModel` |
| **pbi-tools** | Has `.pbixproj.json` AND `Model/` folder | `.pbixproj.json` + `Model/` |
| **Invalid** | None of the above | - |

**Detection procedure:**

```
1. If path is a file AND ends with .pbix:
   → Format: PBIX (requires extraction)

2. If path is a directory:
   a. Glob for "*.pbip" files
   b. Glob for "*.SemanticModel" folders
   c. If both found → Format: PBIP

   d. If PBIP not found:
      - Check for ".pbixproj.json" file
      - Check for "Model/" folder
      - If both found → Format: pbi-tools

   e. Otherwise → Format: Invalid
```

### Step 2: Validate Required Files

**For PBIP format:**

```
Required:
  <project>/
    ├── *.pbip                           # Project file
    └── *.SemanticModel/
        └── definition/
            ├── model.tmdl               # Required
            └── tables/                  # Required folder
                └── *.tmdl               # At least one table

Optional (for visual changes):
  <project>/
    └── *.Report/
        └── definition/
            ├── report.json              # Report config
            └── pages/                   # Page definitions
```

**Validation procedure:**

```
Glob: <project>/*.pbip
→ Must find at least 1 file

Glob: <project>/*.SemanticModel/definition/model.tmdl
→ Must find exactly 1 file

Glob: <project>/*.SemanticModel/definition/tables/*.tmdl
→ Must find at least 1 file

If visual changes expected:
  Glob: <project>/*.Report/definition/report.json
  → Must find exactly 1 file
```

**For pbi-tools format:**

```
Required:
  <project>/
    ├── .pbixproj.json (or pbixproj.json)
    └── Model/
        ├── model.tmdl                   # Required
        └── tables/                      # Table definitions
            └── *.tmdl

Note: pbi-tools does NOT support visual changes
```

**Validation procedure:**

```
Read: <project>/.pbixproj.json OR <project>/pbixproj.json
→ Must exist

Glob: <project>/Model/model.tmdl
→ Must exist

If visual changes expected:
  → ERROR: pbi-tools format does not support visual changes
```

### Step 3: Path Length Validation

**Windows has a 260-character MAX_PATH limit.**

PBIP projects have deeply nested structures:
```
{base}/{project}/{project}.Report/definition/pages/{page}/visuals/{guid}/visual.json
```

**Path budget calculation:**

| Component | Typical Length |
|-----------|----------------|
| Reserved for nested structure | ~120 characters |
| Base path | Variable |
| Project name (appears twice) | Variable × 2 |

**Warning levels:**

| Total Estimated Max | Level | Action |
|---------------------|-------|--------|
| > 250 characters | CRITICAL | Must move to shorter path |
| 231-250 characters | WARNING | Recommend shorter path |
| 201-230 characters | CAUTION | Keep project names short |
| ≤ 200 characters | OK | Safe for PBIP |

**Calculation formula:**

```
Total = len(base_path) + 1 + len(project_name) + 1 + len(project_name) + 120

Recommended max project name = (260 - len(base_path) - 1 - 120 - 1) / 2
```

**Example:**
```
Base path: C:\Users\JohnDoe\Documents\PowerBI\Projects (45 chars)
Project name: CustomerAnalyticsDashboard (26 chars)

Total = 45 + 1 + 26 + 1 + 26 + 120 = 219 characters ✅ OK

Recommended max = (260 - 45 - 1 - 120 - 1) / 2 = 46 characters
```

### Step 4: Generate Validation Report

**Report format:**

```
======================================================================
POWER BI PROJECT VALIDATION
======================================================================
Project Path: <path>
Timestamp: <timestamp>
Visual Changes Expected: Yes/No
======================================================================

[SUCCESS/ERROR/ACTION REQUIRED]

Format: PBIP / pbi-tools / PBIX / Invalid
Semantic Model: <path>
Report Path: <path> (if applicable)
Requires Compilation: Yes/No

TMDL Files Found:
  - model.tmdl
  - tables/
  - tables/Sales.tmdl
  - tables/Customers.tmdl
  - ... and N more

Report Files Found:
  - report.json
  - pages/
  - pages/Page1/
  - ... and N more pages

----------------------------------------------------------------------
PATH LENGTH ANALYSIS
----------------------------------------------------------------------
Base path length: X characters
Project name length: Y characters
Estimated max path: Z characters
Warning level: OK / CAUTION / WARNING / CRITICAL

[If WARNING or CRITICAL:]
RECOMMENDATION:
  1. Move to a shorter path (e.g., C:\PBI\)
  2. Or use shorter project name (max: N characters)
======================================================================
```

### Step 5: Handle Special Cases

**PBIX file detected:**

```
Status: ACTION_REQUIRED
Action: pbix_extraction

Message: "The PBIX file needs to be extracted to a folder format for analysis."

Options:
  1. Convert to PBIP format (recommended)
  2. Use pbi-tools to extract
  3. Continue with PBIX (limited analysis)
```

**Visual changes requested but no .Report folder:**

```
Status: ERROR
Action: report_folder_missing

Message: "Visual changes requested but .Report folder not found"

Suggested Fix:
  1. Open and re-save in Power BI Desktop to create .Report folder
  2. Handle visual changes manually in Power BI Desktop UI
  3. Re-run focusing only on calculation changes
```

**pbi-tools with visual changes:**

```
Status: ERROR
Action: format_incompatible_with_visual_changes

Message: "Visual changes requested but project format does not support visual modifications"

Suggested Fix:
  1. Use Power BI Project (.pbip) format instead
  2. Handle visual changes manually in Power BI Desktop UI
  3. Split request - run for calculation changes only
```

---

## Part 2: Validation Checklist

Before proceeding with project modifications:

- [ ] Project format detected and valid
- [ ] Required files exist (model.tmdl, at least one table)
- [ ] Path length is within safe limits
- [ ] If visual changes needed: .Report folder exists
- [ ] Semantic model path identified
- [ ] No compilation required (or compilation available)

---

## Part 3: Format Comparison

| Aspect | PBIP | pbi-tools | PBIX |
|--------|------|-----------|------|
| File Extension | `.pbip` | `.pbixproj.json` | `.pbix` |
| Semantic Model | `*.SemanticModel/` | `Model/` | Embedded |
| Report Support | `*.Report/` | No | Embedded |
| Visual Changes | ✅ Yes | ❌ No | ❌ No |
| Requires Compilation | No | Yes | N/A |
| Git-Friendly | ✅ Yes | ✅ Yes | ❌ No |
| Power BI Desktop | Native | Via pbi-tools | Native |

---

## See Also

- `tmdl_partition_structure.md` - TMDL format validation
- `tool-fallback-pattern.md` - Pro vs Core tool usage
- `SKILL.md` - Main skill documentation
