---
name: setup-data-anonymization
description: Set up M code-based data anonymization for a Power BI project. Auto-detects sensitive columns, generates conditional masking M code, and configures a DataMode parameter for toggling between real and anonymized data. Use this before working with MCP on sensitive client data.
pattern: ^/setup-data-anonymization\s+(.+)$
---

# Setup Data Anonymization

This workflow enables you to work with Power BI MCP on sensitive data by:
0. **Checking for cached data** that may expose unmasked values (security risk)
1. Auto-detecting columns that likely contain PII/sensitive data
2. Generating M code with conditional masking logic
3. Creating a DataMode parameter for toggling between Real and Anonymized modes

> **Security Note**: Power BI PBIP format caches refreshed data in `.pbi/cache.abf`. This workflow checks for and optionally removes cached data that could bypass anonymization.

## Tracing Output (Required)

**On workflow start, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 WORKFLOW: setup-data-anonymization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Before each phase, output:**
```
📋 PHASE [N]: [Phase Name]
   └─ [What this phase does]
```

**On workflow complete, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: setup-data-anonymization
   └─ Config: .anonymization/config.json
   └─ Next: Open in Power BI Desktop and add DataMode parameter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Usage

```bash
/setup-data-anonymization --project <path-to-pbip-folder>
```

### Parameters

- `--project` (required): Path to the Power BI Project folder (containing .SemanticModel)

### Examples

```bash
# Basic usage
/setup-data-anonymization --project "C:\Projects\SalesReport"

# Relative path
/setup-data-anonymization --project "./ClientDashboard"
```

## Workflow Phases

### Phase 0: Cache Security Check

**Goal**: Detect and handle cached data that may contain unmasked sensitive information.

**Why this matters**: Power BI PBIP format stores the last refreshed data in `.pbi/cache.abf`. If this cache was created with `DataMode = "Real"`, it contains unmasked data that MCP tools or file access could expose — even after you switch to Anonymized mode.

**Steps**:
1. Search for `.pbi/cache.abf` files in the project
2. If found, check file size and modification date
3. Warn user and prompt for action

**Cache detection locations**:
```
YourProject.SemanticModel/.pbi/cache.abf
YourProject.Report/.pbi/cache.abf
```

**Output if cache found**:
```
📋 PHASE 0: Cache Security Check
   └─ Scanning for cached data files...

   ⚠️  WARNING: Data cache detected!
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Found: YourProject.SemanticModel/.pbi/cache.abf
   Size: 12.4 MB
   Modified: 2025-01-02 14:30:22

   This cache may contain UNMASKED sensitive data from a previous
   refresh. MCP tools or direct file access could expose this data
   even after anonymization is configured.

   Options:
     [D] Delete cache now (recommended)
         Cache will rebuild with anonymized data on next refresh

     [K] Keep cache and continue
         ⚠️  Risk: Cache may contain real data

     [I] Inspect cache metadata
         Show what tables/columns are cached (not the data itself)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If user chooses [D] Delete**:
```powershell
# Delete cache files
Remove-Item -Path "{{PROJECT}}/.pbi/cache.abf" -Force -ErrorAction SilentlyContinue
```

```
   └─ ✅ Cache deleted: YourProject.SemanticModel/.pbi/cache.abf
   └─ ℹ️  Cache will rebuild on next Power BI refresh
```

**If user chooses [K] Keep**:
```
   └─ ⚠️ Continuing with existing cache
   └─ ℹ️  IMPORTANT: Refresh with DataMode="Anonymized" before using MCP
```

**Output if no cache found**:
```
📋 PHASE 0: Cache Security Check
   └─ Scanning for cached data files...
   └─ ✅ No data cache found (safe to proceed)
```

**Add to .gitignore** (automatic):
If `.gitignore` exists and doesn't already exclude cache files, append:
```gitignore
# Power BI data cache - may contain sensitive data
**/.pbi/cache.abf
**/.pbi/localSettings.json
```

```
   └─ ✅ Added cache exclusion to .gitignore
```

---

### Phase 1: Project Validation

**Goal**: Verify project structure and check for existing anonymization config.

**Steps**:
1. Verify project path exists and contains TMDL files
2. Check for `.anonymization/config.json` - if exists, ask user if they want to reconfigure
3. Create `.anonymization/` directory if it doesn't exist

**Output**:
```
📋 PHASE 1: Project Validation
   └─ Verifying project structure...
   └─ ✅ Found: 8 TMDL files in semantic model
   └─ ⚠️ No existing anonymization config (first-time setup)
```

### Phase 2: Sensitive Column Detection

**Goal**: Scan TMDL files to identify columns likely containing sensitive data.

**Steps**:
1. Run `sensitive_column_detector.py` against project
2. Parse detection results
3. Group findings by confidence level (HIGH, MEDIUM, LOW)

**Output**:
```
📋 PHASE 2: Sensitive Column Detection
   └─ Scanning TMDL files for sensitive columns...
   └─ Found 12 potentially sensitive columns:

      HIGH CONFIDENCE (likely sensitive):
        - Customers.CustomerName (names)
        - Customers.Email (emails)
        - Customers.SSN (identifiers)
        - Customers.Phone (phones)
        - Employees.Salary (amounts)

      MEDIUM CONFIDENCE (possibly sensitive):
        - Sales.Amount (amounts)
        - Orders.Price (amounts)

      LOW CONFIDENCE (review recommended):
        - Support.Notes (freetext)
```

### Phase 3: User Confirmation

**Goal**: Allow user to review and customize column selection.

**Prompt user with options**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PHASE 3: Confirm Columns to Anonymize
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The following columns were detected as potentially sensitive:

| Table     | Column       | Category    | Confidence | Masking Strategy     |
|-----------|--------------|-------------|------------|----------------------|
| Customers | CustomerName | names       | HIGH       | sequential_numbering |
| Customers | Email        | emails      | HIGH       | fake_domain          |
| Customers | SSN          | identifiers | HIGH       | partial_mask         |
| Customers | Phone        | phones      | HIGH       | fake_prefix          |
| Sales     | Amount       | amounts     | MEDIUM     | scale_factor         |

Options:
  [Y] Accept all and continue
  [C] Customize selection (add/remove columns)
  [P] Preview masking patterns
  [?] Help - explain masking strategies

Your choice:
```

**If user chooses [C] Customize**:
- Show list of detected columns with checkboxes
- Allow adding columns by name (table.column format)
- Allow removing columns from list
- Show available masking strategies

**If user chooses [P] Preview**:
- Show sample of what each masking strategy produces
- Example: "John Smith" → "Customer 1"
- Example: "john@company.com" → "user1@example.com"

### Phase 3b: Numerical Column Configuration

**Goal**: For each numerical column detected, ask targeted questions to select the optimal anonymization strategy.

For each column in the `amounts` category, prompt:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CONFIGURE NUMERICAL COLUMN: {{Table}}.{{Column}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please answer these questions to select the best anonymization strategy:

1. What is the typical value range for this column?
   [A] Small integers (0-20) — counts, units, ratings
   [B] Medium integers (20-100) — quantities, scores
   [C] Large values (100+) — financial amounts, revenue
   [D] Mixed/varies widely

2. Must values stay non-negative (no negative results)?
   [Y] Yes - floor at zero
   [N] No - negative values are acceptable

3. Do totals across related columns need to add up?
   (e.g., Total = Unit1 + Unit2 + Unit3)
   [Y] Yes - apply consistent factor per row
   [N] No - independent randomization is fine

4. How important is preserving the distribution shape?
   [H] High - relative differences matter for analysis
   [M] Medium - general patterns should hold
   [L] Low - just need plausible values
```

**Strategy Selection Logic**:

| Q1 Answer | Q4 Answer | Recommended Strategy |
|-----------|-----------|---------------------|
| A (0-20) | Any | **Hybrid** with floor=2 |
| B (20-100) | Any | **Hybrid** with floor=3 |
| C (100+) | H (High) | **Scale Factor** (0.8-1.2x) |
| C (100+) | M/L | **Hybrid** with floor=5% of median |
| D (Mixed) | Any | **Hybrid** with floor=2 |

**If Q3 = Yes (totals must add up)**:
- Generate row-level random factor instead of column-level
- Apply same factor to all related columns in the row
- Recalculate Total column after anonymizing components

**Output after configuration**:
```
📋 NUMERICAL STRATEGY SELECTED: {{Table}}.{{Column}}
   └─ Strategy: Hybrid (Percentage + Floor)
   └─ Percentage: 25%
   └─ Minimum Floor: 2
   └─ Non-negative: Yes
   └─ Sample: 5 → range [3-7], 100 → range [75-125]
```

### Phase 4: Generate M Code

**Goal**: Generate conditional masking M code for selected columns using configured strategies.

**Steps**:
1. Run `anonymization_generator.py` with confirmed columns and their strategies
2. Generate M code transformations for each table
3. For numerical columns, apply the strategy selected in Phase 3b:
   - **Hybrid**: Use percentage + floor pattern from `anonymization_patterns.md`
   - **Scale Factor**: Use 0.8-1.2x multiplier pattern
   - **Random Replacement**: Use random range pattern
   - **Bucketing**: Use range label pattern
4. Generate DataMode parameter definition

**Output**:
```
📋 PHASE 4: Generate M Code
   └─ Generating masking transformations...
   └─ Created M code for 3 tables:
      - Customers: 4 columns masked
      - Sales: 1 column masked (Hybrid: 25%/floor=2)
      - Employees: 1 column masked (Scale Factor: 0.8-1.2x)
   └─ DataMode parameter definition generated
```

### Phase 5: Preview & Confirm

**Goal**: Show generated M code and get user approval before proceeding.

**Display for each table**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TABLE: Customers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Columns to mask:
  - CustomerName → sequential_numbering
  - Email → fake_domain
  - SSN → partial_mask
  - Phone → fake_prefix

Generated M Code:
```m
let
    Source = {PREVIOUS_STEP},

    // Add index for sequential numbering
    IndexedData = Table.AddIndexColumn(Source, "_MaskIndex", 1, 1, Int64.Type),

    // Apply conditional masking based on DataMode parameter
    MaskedData = Table.TransformColumns(IndexedData, {
        {"CustomerName", each
            if #"DataMode" = "Anonymized" then
                "Customer " & Text.From([_MaskIndex])
            else
                [CustomerName],
            type text
        },
        {"Email", each
            if #"DataMode" = "Anonymized" then
                "user" & Text.From([_MaskIndex]) & "@example.com"
            else
                [Email],
            type text
        },
        ...
    }),

    Result = Table.RemoveColumns(MaskedData, {"_MaskIndex"})
in
    Result
```

[A] Apply this code
[S] Skip this table
[E] Edit manually
```

**For tables with numerical columns** (showing Hybrid strategy):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TABLE: Sales
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Columns to mask:
  - Units → hybrid (25%, floor=2)
  - Amount → scale_factor (0.8-1.2x)

Generated M Code:
```m
let
    Source = {PREVIOUS_STEP},

    // Apply conditional masking based on DataMode parameter
    MaskedData = if #"DataMode" = "Anonymized" then
        Table.TransformColumns(Source, {
            // Units: Hybrid strategy (25% + floor 2)
            // Small values get ±2, large values get ±25%
            {"Units", each
                let
                    PercentNoise = Number.Abs(_) * 0.25,
                    MinFloor = 2,
                    NoiseRange = Number.Max(MinFloor, PercentNoise),
                    RandomNoise = (Number.Random() * 2 - 1) * NoiseRange,
                    Result = Number.Max(0, Number.RoundDown(_ + RandomNoise))
                in
                    Result,
                Int64.Type
            },
            // Amount: Scale factor (0.8x to 1.2x)
            {"Amount", each
                Number.Round(_ * (0.8 + Number.Random() * 0.4), 2),
                type number
            }
        })
    else
        Source
in
    MaskedData
```

Expected behavior:
  - Units=5 → range [3-7]
  - Units=100 → range [75-125]
  - Amount=$50.00 → range [$40.00-$60.00]

[A] Apply this code
[S] Skip this table
[E] Edit manually
```

### Phase 6: Save Configuration

**Goal**: Save anonymization config and generated code for reference.

**Steps**:
1. Create backup of current TMDL files (`.anonymization/backups/`)
2. Save generated M code files (`.anonymization/generated/`)
3. Save configuration (`.anonymization/config.json`)

**Output**:
```
📋 PHASE 6: Save Configuration
   └─ Creating backup of TMDL files...
   └─ Saved to: .anonymization/backups/20250102_143022/
   └─ Generated M code saved to: .anonymization/generated/
   └─ Config saved to: .anonymization/config.json
```

### Phase 7: Integration Instructions

**Goal**: Provide clear instructions for integrating the generated code.

**Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PHASE 7: Integration Instructions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To complete the anonymization setup:

1. ADD DATAMODE PARAMETER
   Open Power BI Desktop → Home → Transform Data → Manage Parameters → New Parameter

   Name: DataMode
   Type: Text
   Current Value: Real
   Allowed Values: Real, Anonymized

2. MODIFY PARTITION M CODE
   For each table listed below, add the generated masking code:

   - Customers partition: Insert code from .anonymization/generated/Customers_anonymization.m
   - Sales partition: Insert code from .anonymization/generated/Sales_anonymization.m

   Insert the masking steps AFTER your source data retrieval and BEFORE final type casting.

3. TEST BOTH MODES
   - Set DataMode = "Real" → Refresh → Verify real data loads
   - Set DataMode = "Anonymized" → Refresh → Verify masked data loads

4. USE WITH MCP
   - Set DataMode = "Anonymized"
   - Click Close & Apply
   - Now MCP queries will return masked values
   - Switch back to "Real" when done developing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: setup-data-anonymization
   └─ Config: .anonymization/config.json
   └─ Backups: .anonymization/backups/
   └─ Generated code: .anonymization/generated/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Files Created

After running this workflow, the following files are created:

```
YourProject/
├── .anonymization/
│   ├── config.json           ← Anonymization settings
│   ├── backups/
│   │   └── 20250102_143022/  ← Backup of original TMDL files
│   └── generated/
│       ├── Customers_anonymization.m
│       ├── Sales_anonymization.m
│       └── DataMode_parameter.m
└── ...
```

## Toggling Between Modes

After integration, to switch modes:

1. **To use anonymized data (for MCP/development)**:
   - Open Power BI Desktop
   - Transform Data → Parameters → DataMode = "Anonymized"
   - Close & Apply
   - Data refreshes with masked values
   - ✅ Safe to use with MCP tools

2. **To use real data (for production/deployment)**:
   - Transform Data → Parameters → DataMode = "Real"

> ⚠️ **Cache Warning**: After refreshing with `DataMode = "Real"`, the `.pbi/cache.abf` file will contain unmasked data. Before using MCP tools again:
> 1. Switch back to `DataMode = "Anonymized"`
> 2. Refresh to rebuild cache with masked data
>
> Or delete the cache file manually:
> ```powershell
> Remove-Item -Path "YourProject.SemanticModel/.pbi/cache.abf" -Force
> ```
   - Close & Apply
   - Data refreshes with actual values

## Query Folding Note

All masking operations break query folding. This is expected and acceptable for:
- Development/testing scenarios
- Small-medium datasets
- Security requirements

For large datasets, consider applying filters BEFORE the masking steps to reduce data loaded.

## Restoring Original State

To restore original TMDL files:
```bash
# Copy backup files back
cp -r .anonymization/backups/<timestamp>/* .

# Or delete the masking steps manually from Power Query
```

## Related Resources

- `references/anonymization_patterns.md` - Complete masking template library
- `scripts/sensitive_column_detector.py` - Column detection script
- `scripts/anonymization_generator.py` - M code generation script
