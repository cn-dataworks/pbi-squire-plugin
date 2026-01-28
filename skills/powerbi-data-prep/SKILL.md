---
name: powerbi-data-prep
description: "[DEPRECATED] This skill has been merged into powerbi-analyst. Use powerbi-analyst instead with the DATA_PREP workflow."
---

# Power BI Data Prep

> **⚠️ DEPRECATED:** This skill has been consolidated into `powerbi-analyst`.
>
> The `powerbi-analyst` skill now includes the **DATA_PREP workflow** which provides:
> - M code / Power Query transformations
> - Query folding validation
> - Pattern analysis and best practices
> - Safe TMDL partition editing
>
> **Trigger the DATA_PREP workflow by saying:**
> - "Filter this table in Power Query"
> - "Add a calculated column in M code"
> - "Merge these two tables"
> - "Edit the M code for..."
>
> **Please use `powerbi-analyst` instead.**

---

## Legacy Documentation (for reference)

Write and edit M code (Power Query) transformations in Power BI projects with intelligent pattern analysis, query folding validation, and safe TMDL editing.

## Core Workflow

1. **Analyze existing patterns** - Discover naming conventions and transformation styles
2. **Design transformation** - Prefer simplest approach, present pros/cons for complex alternatives
3. **Validate query folding** - Warn about performance impacts before applying
4. **Apply M code changes** - Safely edit TMDL partition files
5. **Validate TMDL syntax** - Run syntax checker to ensure file integrity

## M Code Transformation Capabilities

### Editing Existing Tables
- Filter rows based on conditions
- Remove or select specific columns
- Rename columns
- Add custom columns (conditional logic, concatenation, calculations)
- Change data types
- Merge/join tables
- Append tables
- Pivot/unpivot operations
- Group and aggregate data
- Replace values
- Modify existing transformation steps

### Creating New Tables
- Generate calculated tables with M code
- Create date/calendar tables
- Reference existing tables with transformations
- Build dimension tables from fact tables

### Partition Operations (Rare - User Confirmation Required)
- Add new partitions to tables (incremental refresh scenarios)
- Modify partition expressions
- **Note**: Partition creation should be thoroughly discussed and only done when specifically requested

## Step-by-Step Process

### Step 1: Understand the Request

Ask clarifying questions:
- What transformation is needed? (filter, merge, new column, etc.)
- Which table(s) are affected?
- What is the desired outcome?
- Are there performance concerns?

### Step 2: Analyze Project Patterns

Run the pattern analyzer to discover:
- Naming conventions (PascalCase, snake_case, etc.)
- Common transformation patterns
- Code organization style
- Table naming standards

```bash
python scripts/m_pattern_analyzer.py "<project-path>"
```

See `references/m_pattern_discovery.md` for interpretation guidance.

### Step 3: Design the Transformation

**Simplicity First**: Always present the simplest transformation that accomplishes the goal.

**Present Alternatives**: If more complex approaches offer advantages (better performance, maintainability, flexibility), present them with clear pros/cons:

```
Option 1 (Recommended): Filter in M code
  ✓ Simple and straightforward
  ✓ Maintains query folding
  ✓ Easy to modify later
  ✗ Loads all data then filters

Option 2: Filter at source (SQL WHERE clause)
  ✓ Better performance for large datasets
  ✓ Reduces data transfer
  ✗ More complex M code
  ✗ Requires SQL knowledge to maintain
  ✗ May break if source schema changes
```

See `references/common_transformations.md` for M code patterns.

### Step 4: Validate Query Folding

Before applying changes, validate query folding impact:

```bash
python scripts/query_folding_validator.py "<tmdl-file>" --proposed-code "<m-code>"
```

**Always warn users if proposed changes break query folding**, explaining:
- What query folding is (pushing transformations to the data source)
- Performance impact (loading more data into Power BI)
- When it's acceptable (small datasets, complex transformations unavoidable)

See `references/query_folding_guide.md` for detailed rules.

### Step 5: Apply M Code Changes

Use the safe TMDL partition editor to modify M code:

**For editing existing partitions:**
```bash
python scripts/m_partition_editor.py "<tmdl-file>" --table "<TableName>" --partition "<PartitionName>" --m-code "<m-code-file>"
```

**For creating new tables:**
```bash
python scripts/m_partition_editor.py "<tmdl-file>" --create-table "<TableName>" --m-code "<m-code-file>"
```

The editor:
- Handles tabs and indentation correctly
- Preserves TMDL structure
- Creates automatic backups
- Validates syntax before saving

See `references/tmdl_partition_structure.md` for TMDL partition formatting rules.

### Step 6: Validate TMDL Syntax

After applying changes, **always** run the TMDL syntax validator:

```bash
python .claude/tools/tmdl_format_validator.py "<tmdl-file>" --context "Modified <TableName> partition"
```

If validation fails, review errors and fix before proceeding.

For authoritative validation before deployment:
```bash
python .claude/tools/tmdl_format_validator.py "<tmdl-file>" --authoritative
```

## M Code Best Practices

Load detailed best practices from `references/m_best_practices.md` when:
- Writing complex transformations
- Optimizing performance
- Ensuring maintainability
- Following naming conventions

Key principles:
- **Descriptive step names**: Use clear names like "Remove Inactive Customers" not "Filtered Rows"
- **Comments for complex logic**: Explain non-obvious transformations
- **Consistent naming**: Follow project patterns discovered in Step 2
- **Error handling**: Use `try...otherwise` for operations that might fail
- **Parameter usage**: Use parameters for values that might change

## Query Folding Validation

**Always check query folding** before applying transformations that might break it.

**Preserves query folding:**
- Filtering rows (`Table.SelectRows`)
- Selecting columns (`Table.SelectColumns`)
- Renaming columns (`Table.RenameColumns`)
- Sorting (`Table.Sort`)
- Grouping/aggregating (`Table.Group`)
- Joins on indexed columns

**Breaks query folding:**
- Adding custom columns with M functions
- Text operations (concatenation, substring, etc.)
- Complex conditional logic
- Merging with non-database sources
- Pivot/unpivot operations
- Any operation using `#"Added Custom"`

See `references/query_folding_guide.md` for comprehensive rules and workarounds.

## Common Transformation Patterns

For frequently-used transformations, load from `references/common_transformations.md`:

- **Filter rows**: Based on single/multiple conditions
- **Add calculated column**: Concatenation, conditional logic, date calculations
- **Merge tables**: Inner, left outer, full outer joins
- **Append tables**: Union multiple tables
- **Remove duplicates**: Based on one or more columns
- **Pivot/unpivot**: Reshape data
- **Group and aggregate**: Sum, count, average, etc.
- **Replace values**: Null handling, value mapping

Each pattern includes:
- M code snippet
- Query folding impact
- Common pitfalls
- When to use vs alternatives

## TMDL Partition Structure

M code in TMDL files follows this structure:

```tmdl
table Sales
	partition 'Sales-Part1' = m
		mode: Import
		source =
			let
				Source = Sql.Database("server", "db"),
				Navigation = Source{[Schema="dbo",Item="Sales"]}[Data],
				FilteredRows = Table.SelectRows(Navigation, each [Amount] > 0)
			in
				FilteredRows
```

**Critical formatting rules:**
- Use tabs for indentation
- `source =` followed by M expression
- `let` statement starts M code block
- Each step on new line with comma separator
- Final step referenced in `in` statement
- No trailing commas

See `references/tmdl_partition_structure.md` for complete specification.

## Error Handling

If M code changes fail:

1. **Check TMDL syntax validation** - Most common issue
2. **Verify M code syntax** - Check for typos, missing commas, unmatched brackets
3. **Restore from backup** - Editor creates `.backup` files automatically
4. **Review query folding warnings** - May indicate unsupported operations
5. **Test in Power Query Editor** - Copy M code and test in Power BI Desktop

## Integration with Power BI Workflows

This skill integrates with existing Power BI workflows:

**Typical usage:**
1. User requests data transformation
2. **This skill** designs and applies M code changes
3. Validate TMDL syntax (automatic via this skill)
4. Use `/implement-deploy-test-pbi-project-file` for deployment and testing

**When to use this skill vs other workflows:**
- Use this skill for M code / Power Query transformations
- Use `/create-pbi-artifact` for DAX measures, calculated columns (DAX, not M)
- Use `/evaluate-pbi-project-file` for debugging existing issues

## Data Anonymization

For working with sensitive client data while using MCP, use the anonymization workflow:

```bash
/setup-data-anonymization --project "<path-to-pbip>"
```

This workflow:
1. **Detects sensitive columns** - Scans for PII patterns (names, emails, SSN, phones, etc.)
2. **Generates masking M code** - Creates conditional transformations with DataMode parameter
3. **Enables mode toggling** - Switch between Real and Anonymized data

### Scripts for Anonymization

- `scripts/sensitive_column_detector.py` - Scan for PII column patterns
- `scripts/anonymization_generator.py` - Generate conditional masking M code

### Toggling Data Mode

After setup, toggle between modes in Power BI Desktop:
1. Transform Data → Parameters → DataMode
2. Set to "Real" (actual data) or "Anonymized" (masked data)
3. Close & Apply to refresh

See `workflows/setup-data-anonymization.md` for complete workflow details.
See `references/anonymization_patterns.md` for masking template library.

## Scripts Reference

### `m_partition_editor.py`
Safely edit M code in TMDL partition files with proper tab handling, indentation, and backups.

### `m_pattern_analyzer.py`
Scan project to discover naming conventions, transformation patterns, and code organization styles.

### `query_folding_validator.py`
Analyze M code to detect operations that break query folding and estimate performance impact.

### `sensitive_column_detector.py`
Scan TMDL files to identify columns likely containing sensitive/PII data based on naming patterns.

### `anonymization_generator.py`
Generate conditional masking M code for detected sensitive columns with DataMode parameter.

## References

Load these as needed for detailed guidance:

- `references/m_best_practices.md` - M code style guide and optimization techniques
- `references/query_folding_guide.md` - Complete rules for what preserves/breaks query folding
- `references/common_transformations.md` - Library of M code patterns with examples
- `references/tmdl_partition_structure.md` - TMDL partition formatting specification
- `references/m_pattern_discovery.md` - How to interpret pattern analysis output
- `references/anonymization_patterns.md` - M code templates for data masking

## Success Criteria

M code transformation is successful when:
1. ✅ Transformation accomplishes the stated goal
2. ✅ M code follows project patterns and naming conventions
3. ✅ Query folding impact is validated and user-acknowledged
4. ✅ TMDL syntax validation passes
5. ✅ Code is simple, maintainable, and well-documented
6. ✅ Backup files are created for rollback capability
