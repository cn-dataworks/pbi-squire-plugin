# Power BI Project Format Detection Guide

## Purpose

Detect project storage mode (Import vs Live Connection vs DirectQuery) and recommend appropriate format conversion to enable full analysis capabilities.

---

## Why Format Matters

| Format | What You Can Analyze |
|--------|---------------------|
| .pbix (binary) | Nothing without extraction - file is compressed binary |
| .pbix (extracted with pbi-tools) | DAX measures only - M code embedded in DataModel |
| .pbip (Import Mode) | **Everything**: DAX, M code, schemas, relationships, visuals |
| .pbip (DirectQuery) | DAX, M code, schemas - but data is remote |
| .pbip (Live Connection) | Report visuals only - data model is remote |

**Key Insight**: PBIP format unlocks M code visibility, which is critical for tracing data lineage and understanding ETL transformations.

---

## Storage Mode Detection Logic

### Step 1: Identify Project Format

| Detected Pattern | Project Type |
|-----------------|--------------|
| Single `.pbix` file | PBIX Binary - needs conversion |
| Folder with `*.pbip` + `.SemanticModel/` | PBIP - full analysis available |
| Folder with `.pbixproj.json` + `Model/` | pbi-tools extracted - DAX only |
| Folder with `DataModel` (binary) + `Report/` | Extracted PBIX - limited analysis |

### Step 2: Check Storage Mode (PBIP only)

For PBIP projects, check partition definitions in TMDL files:

**Location**: `.SemanticModel/definition/tables/*.tmdl`

```tmdl
partition 'TableName' = m
    mode: import  // or directQuery
    source =
        let
            Source = ...
        in
            Result
```

**Detection Rules**:
- `mode: import` or `mode: directQuery` = Has data model with M code
- No partition blocks (only measures) = Calculated table or Live Connection table

### Step 3: Check for Live Connection

**PBIP Live Connection Indicators**:

1. **Check for remote dataset reference** in `.SemanticModel/definition/model.tmdl`:
   ```tmdl
   model Model
       culture: en-US
       // Look for: No table definitions with partitions
   ```

2. **Check table TMDL files for thin structure**:
   - Tables with ONLY measures (no partitions) = measures-only table
   - No tables at all in `/tables/` = Report connects to remote dataset

3. **Check DataModel size** (if extracted format):
   | File | Size | Interpretation |
   |------|------|----------------|
   | `DataModel` | > 1 MB | **Import Mode** - data embedded |
   | `DataModel` | < 100 KB or missing | **Live Connection** - thin report |

### Step 4: Check Connections File (Extracted PBIX)

If working with extracted PBIX (not PBIP), check the Connections file:

**File**: `Connections` (JSON)

```json
{
  "RemoteArtifacts": [{
    "DatasetId": "guid-here"
  }]
}
```

**IMPORTANT**: `RemoteArtifacts` indicates where the report was PUBLISHED TO, NOT that it's a Live Connection. Always cross-reference with DataModel size.

---

## Format Capabilities Matrix

| Capability | .pbix (binary) | .pbix (extracted) | .pbip (Import) | .pbip (DirectQuery) | .pbip (Live Connection) |
|-----------|----------------|-------------------|----------------|---------------------|------------------------|
| Read DAX measures | No | Yes | Yes | Yes | No (remote) |
| Read M code / Power Query | No | No* | Yes | Yes | No (remote) |
| Read table schemas | No | Partial | Yes | Yes | No (remote) |
| Read relationships | No | Yes | Yes | Yes | No (remote) |
| Edit visuals (PBIR) | No | No | Yes (with .Report) | Yes (with .Report) | Yes (with .Report) |
| Live validation (MCP) | No | No | Yes | Yes | Limited |

*M code is embedded in DataModel binary, not readable as text

---

## User-Facing Messages

### Scenario: PBIX File Detected (Import Mode)

```
+---------------------------------------------------------------------------+
|  PBIX FILE DETECTED - Limited Analysis Mode                               |
+---------------------------------------------------------------------------+

You've provided a .pbix file. This binary format limits what can be analyzed:

  Current capabilities:
    [OK] DAX measures (after extraction)
    [--] M code / Power Query - NOT READABLE
    [--] Table schemas - NOT READABLE
    [--] Data lineage - NOT TRACEABLE

To analyze the full data lineage including M code:

  OPTION 1: Convert to PBIP (Recommended)
  -----------------------------------------
  1. Open this file in Power BI Desktop
  2. File -> Save As -> Power BI Project (.pbip)
  3. Re-run this command with the .pbip folder path

  OPTION 2: Continue with Limited Analysis
  -----------------------------------------
  I can still analyze DAX measures after extraction, but M code
  and data transformations will not be visible.

Would you like to:
  [A] I'll convert to PBIP and come back
  [B] Continue with DAX-only analysis (extract with pbi-tools)
  [C] Show me manual extraction instructions
```

### Scenario: Live Connection Report Detected

```
+---------------------------------------------------------------------------+
|  LIVE CONNECTION REPORT DETECTED                                          |
+---------------------------------------------------------------------------+

This report connects to a remote dataset and does not contain its own data model.

  Dataset ID: {dataset-id}
  Workspace ID: {workspace-id} (if available)

  What this means:
    [OK] Report visuals - CAN analyze
    [--] DAX measures - Remote (not in this file)
    [--] M code - Remote (not in this file)
    [--] Data model - Remote (not in this file)

To analyze the data model and M code, you need the SOURCE DATASET:

  1. Go to Power BI Service
  2. Find the dataset in the workspace
  3. Download as .pbip (Power BI Project)
  4. Re-run this command with the dataset's .pbip folder

Would you like to:
  [A] Continue analyzing report visuals only
  [B] Help me locate the source dataset
```

### Scenario: pbi-tools Extracted Format

```
+---------------------------------------------------------------------------+
|  pbi-tools FORMAT DETECTED - Partial Analysis Mode                        |
+---------------------------------------------------------------------------+

This project was extracted using pbi-tools, which provides:

  Current capabilities:
    [OK] DAX measures - Full access
    [OK] Relationships - Full access
    [OK] Table schemas - Full access
    [--] M code / Power Query - Embedded in binary, not readable
    [--] PBIR visuals - Not available (different structure)

  For full M code visibility:
  1. Re-open the original .pbix in Power BI Desktop
  2. File -> Save As -> Power BI Project (.pbip)
  3. This creates human-readable TMDL files with M code

Would you like to:
  [A] Continue with available analysis
  [B] Show conversion instructions
```

---

## Detection Output Format

When the detection runs, return a structured result:

```yaml
format_detection:
  project_type: pbip | pbix_extracted | pbix_binary | pbitools
  storage_mode: import | direct_query | live_connection | unknown
  m_code_accessible: true | false
  recommendation: none | convert_to_pbip | get_source_dataset
  capabilities:
    dax_measures: true | false
    m_code: true | false
    table_schemas: true | false
    relationships: true | false
    pbir_visuals: true | false
  message_key: full_analysis | limited_dax_only | live_connection | conversion_recommended
```

---

## Integration Points

### In evaluate-pbi-project-file.md Phase 1

Add after Step 2 (Project Validation):

**Step 2.5: Storage Mode Detection**

1. Run storage mode detection using logic from this reference
2. If Import Mode PBIX detected:
   - Display conversion recommendation prominently
   - If user declines, note limitation in findings file Prerequisites
3. If Live Connection detected:
   - Display source dataset instructions
   - Option to continue with visual-only analysis
4. If pbi-tools format detected:
   - Note M code limitation
   - Option to continue with DAX-only analysis

### In getting-started.md

Add new section after "Before You Start":

**Understanding Project Formats** section that explains:
- Why PBIP format matters
- The capability matrix for each format
- How to convert PBIX to PBIP

### In SKILL.md Pre-Workflow Checks

Reference this document for format detection logic when validating projects.

---

## Quick Reference: Conversion Path

```
.pbix (binary)
    |
    +---> [pbi-tools extract] ---> Extracted folder (DAX only)
    |
    +---> [PBI Desktop: Save As PBIP] ---> .pbip folder (Full access)

.pbip (Live Connection)
    |
    +---> [Download source dataset] ---> .pbip folder (Full access)
```

**Always prefer the PBIP path for full analysis capability.**

---

## Windows Path Length Considerations

### The Problem

Windows has a default maximum path length of **260 characters** (MAX_PATH). PBIP projects have deeply nested folder structures that can easily exceed this limit:

```
C:\Users\LongUserName\Documents\PowerBI\CustomerProjectFolder\
  └── MyVeryDescriptiveProjectName/
      └── MyVeryDescriptiveProjectName.Report/
          └── definition/
              └── pages/
                  └── Sales Dashboard Overview/
                      └── visuals/
                          └── 12345678-1234-1234-1234-123456789012/
                              └── visual.json  ← Can exceed 260 chars!
```

The deepest paths in PBIP projects are typically in the Report folder, especially:
- `{Project}.Report/definition/pages/{PageName}/visuals/{VisualGUID}/visual.json`
- Visual GUIDs are 36 characters
- Page names can vary significantly

### Path Budget Calculation

| Component | Typical Length |
|-----------|----------------|
| Report folder suffix | `.Report/definition/pages/` = 25 chars |
| Page name | Variable (can be 30+ chars) |
| Visual path | `/visuals/{GUID}/visual.json` = 57 chars |
| **Reserved for nested structure** | **~120 characters** |

**Safe budget for base path + project name:** ~140 characters

### Detection Rules

When recommending PBIP conversion, check path length:

```python
# Calculate expected maximum path length
base_path_length = len(user_provided_path)
project_name_length = len(proposed_project_name)
reserved_structure = 120  # For deepest nested paths

total_expected = base_path_length + project_name_length + reserved_structure

if total_expected > 250:  # Leave 10-char buffer
    # WARN: Path length issue likely
```

### User-Facing Path Length Warnings

#### Warning Level 1: Caution (Total > 200 chars)

```
⚠️  PATH LENGTH ADVISORY

Your project path may approach Windows limits for deeply nested files.

  Base path: C:\Users\{username}\Documents\PowerBI\Projects\
  Base path length: {X} characters

  Recommended maximum project name: {Y} characters

  This ensures all nested files (especially report visuals) stay under
  the Windows 260-character path limit.

Recommendation: Use shorter project names (15-25 characters) or a shorter
base path like C:\PBI\ or D:\Projects\
```

#### Warning Level 2: At Risk (Total > 230 chars)

```
⚠️  PATH LENGTH WARNING

Your setup path is long and may cause issues with PBIP projects.

  Base path: {path}
  Length: {X} characters

  With typical project names, nested files will likely exceed the
  Windows 260-character limit, causing:
  - Save failures in Power BI Desktop
  - Files that cannot be opened or deleted
  - Git operations that fail silently

STRONGLY RECOMMENDED:
  1. Use a shorter base path:
     - C:\PBI\
     - D:\Projects\
     - C:\Dev\

  2. Keep project names under 15 characters:
     - "SalesQ4" instead of "Q4_2024_Sales_Analysis_Dashboard_v2"
     - "HR_Metrics" instead of "Human_Resources_Metrics_Dashboard_Monthly"
```

#### Warning Level 3: Critical (Total > 250 chars)

```
❌  PATH LENGTH CRITICAL

Your current path will almost certainly cause failures with PBIP format.

  Current path: {path}
  Length: {X} characters
  Remaining budget for files: {Y} characters
  Minimum needed for PBIP structure: ~120 characters

You MUST either:
  1. Move to a shorter path: C:\PBI\ (recommended)
  2. Use PBIX format (binary) instead of PBIP

If you proceed with PBIP at this location, expect:
  - Power BI Desktop errors when saving
  - Corrupted or inaccessible files
  - Unable to edit certain visuals
```

### Project Naming Recommendations

| Base Path Length | Recommended Max Project Name |
|------------------|------------------------------|
| < 50 chars | 40 characters |
| 50-100 chars | 30 characters |
| 100-130 chars | 20 characters |
| 130-150 chars | 15 characters |
| > 150 chars | **Use shorter base path** |

### Best Practices for PBIP Paths

1. **Use short base paths:**
   - `C:\PBI\`
   - `D:\Projects\`
   - `C:\Dev\PBI\`

2. **Keep project names concise:**
   - Good: `SalesQ4`, `HRMetrics`, `FinReport`
   - Avoid: `Q4_2024_Quarterly_Sales_Analysis_Dashboard_Final_v2`

3. **Avoid deep customer folder structures:**
   - Instead of: `C:\Customers\Acme Corp\Projects\Analytics\PowerBI\Reports\`
   - Use: `C:\PBI\AcmeCorp\` with customer name in project metadata

4. **Shorten page names in reports:**
   - Good: `Sales Overview`, `Monthly KPIs`
   - Avoid: `Quarterly Sales Analysis by Region and Product Category`

### Integration with Format Recommendation

When presenting PBIP conversion options, ALWAYS check path length first:

```
Step 1: User provides base path for PBI projects
Step 2: Calculate available character budget
Step 3: If budget < 30 chars for project name:
        - Show path length warning
        - Suggest shorter path
        - Offer to proceed with caution
Step 4: Recommend project name character limit based on budget
Step 5: Proceed with format recommendation
```
