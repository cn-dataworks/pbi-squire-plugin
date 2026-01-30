# TMDL Partition Structure

Complete specification for M code partition formatting in TMDL files. Supports both Developer Edition (Python validator) and Analyst Edition (Claude-native validation).

---

## Quick Reference

| Edition | Validation Method |
|---------|-------------------|
| **Pro** | Run `tmdl_format_validator.py` → structured errors with codes |
| **Core** | Use Read tool → apply validation rules below |

---

## Part 1: Format Validation (Claude-Native)

When Python validator is not available, use these instructions to validate TMDL files directly.

### Step 1: Check Indentation Type

**Determine if file uses tabs or spaces:**

1. Read the TMDL file
2. Count lines starting with `\t` (tab) vs lines starting with spaces
3. Majority determines file's indentation type

**Rule:** Power BI requires tabs (`\t`), NOT spaces.

### Step 2: Validate Against TMDL Error Codes

**Check each line for these error conditions:**

| Code | Severity | Condition | Detection Pattern |
|------|----------|-----------|-------------------|
| **TMDL001** | ERROR | Inconsistent property indentation | Adjacent properties have different indent levels |
| **TMDL002** | ERROR | Property has insufficient indentation | Property indent < expected (should be object + 1) |
| **TMDL003** | WARNING | DAX line may have incorrect indentation | DAX line indent < expected (object + 2) |
| **TMDL004** | ERROR | Property inside DAX expression block | Property after RETURN without matching indent |
| **TMDL005** | ERROR | Partition source uses SPACES not TABS | Leading whitespace has spaces, file uses tabs |
| **TMDL006** | ERROR | Mixed TABS and SPACES in line | Leading whitespace has both tabs and spaces |
| **TMDL007** | ERROR | Partition source insufficient indentation | M code has fewer tabs than required |
| **TMDL008** | WARNING | Partition source excessive indentation | M code has more tabs than required |
| **TMDL009** | ERROR | Wrong property for field parameter | `source = {` in calculated partition (should be `expression :=`) |
| **TMDL010** | ERROR | Multi-line field parameter | `expression := {` without `}` on same line |
| **TMDL011** | ERROR | Mixed tabs/spaces at structural level | Tabs and spaces mixed in shallow indentation (0-3 tabs) |
| **TMDL012** | ERROR | DAX at same level as properties | First DAX line has same indent as first property |
| **TMDL013** | ERROR | Duplicate TMDL property | Same property (e.g., lineageTag) appears multiple times |

### Step 3: Indentation Level Validation

**Expected indentation levels (in tabs):**

| Element | Tab Count | Example |
|---------|-----------|---------|
| `table` keyword | 0 | `table Sales` |
| `partition` / `measure` / `column` | 1 | `	partition 'Name' = m` |
| Properties (`mode:`, `formatString:`, `lineageTag:`) | 2 | `		mode: Import` |
| DAX expressions (multi-line) | 3 | `			SWITCH(...)` |
| M code (`let/in`) | 3 | `			let` |
| M steps | 4 | `				Source = ...` |

**Validation procedure:**

1. Find object definitions (measure, column, partition)
2. Record object indentation level
3. Check that properties are at object + 1
4. Check that DAX/M code is at object + 2 (or properties + 1)

### Step 4: DAX/Property Separation Check (TMDL012)

**Critical rule:** Multi-line DAX must be indented deeper than properties.

**Detection procedure:**

1. Find measure/column definition ending with `=`
2. Scan forward to find first DAX line (non-property content)
3. Scan forward to find first property line (`lineageTag:`, `formatString:`, etc.)
4. Compare indentation levels:
   - If DAX indent == property indent → **TMDL012 ERROR**
   - If DAX indent < property indent → **TMDL012 ERROR**

**Example of TMDL012 error:**
```tmdl
measure 'Total Sales' =
		SUMX(Sales, [Amount])      ← 2 tabs (DAX)
		lineageTag: abc-123        ← 2 tabs (Property) ❌ SAME LEVEL!
```

**Correct:**
```tmdl
measure 'Total Sales' =
			SUMX(Sales, [Amount])  ← 3 tabs (DAX)
		lineageTag: abc-123        ← 2 tabs (Property) ✅ Different levels
```

### Step 5: Duplicate Property Check (TMDL013)

**Properties that must be unique within each measure/column:**

- `lineageTag`
- `formatString`
- `displayFolder`
- `dataCategory`
- `isHidden`
- `annotation PBI_FormatHint`

**Detection procedure:**

1. For each measure/column block
2. Track each property occurrence with line number
3. If same property appears multiple times → **TMDL013 ERROR**

### Step 6: Partition-Specific Validation

**For partition `source =` blocks:**

1. Check for `expression :=` vs `source =` usage
   - Calculated partitions (field parameters) use `expression :=`
   - Regular partitions use `source =`
2. Check M code indentation (should be 3 tabs for `let`, 4 tabs for steps)
3. Check for spaces vs tabs in M code lines

### Step 7: Generate Validation Report

**Report format:**

```
================================================================================
TMDL FORMAT VALIDATION REPORT
================================================================================
File: <file_path>
Total Lines: N
Indentation: TABS / SPACES

[SUMMARY]
  Errors:   X
  Warnings: Y

[ERRORS] (Must Fix):
--------------------------------------------------------------------------------

Line 15 [ERROR] TMDL012: DAX expression at same indentation level as properties
  > 		SUMX(Sales, [Amount])
  Recommended fix: Add one more tab before DAX expression

Line 16 [ERROR] TMDL013: Duplicate property "lineageTag" found 2 times
  > 		lineageTag: abc-123
  Recommended fix: Remove duplicate property, keep first occurrence

[WARNINGS] (Should Fix):
--------------------------------------------------------------------------------

Line 10 [WARNING] TMDL003: DAX expression line may have incorrect indentation
  > 	+ [Quantity]
  Recommended fix: Verify indentation matches other DAX lines

================================================================================
[VALIDATION FAILED] - X errors must be fixed before Power BI Desktop can open
================================================================================
```

### Step 8: Fix Recommendations

**For each error code, recommended fix:**

| Code | Fix |
|------|-----|
| TMDL001 | Align all properties to same indentation (object + 1 tabs) |
| TMDL002 | Add tabs to property line (should be at object + 1) |
| TMDL003 | Verify DAX line matches surrounding DAX indentation |
| TMDL004 | Move property outside DAX block, reduce indentation |
| TMDL005 | Replace leading spaces with tabs |
| TMDL006 | Replace all leading whitespace with tabs only |
| TMDL007 | Add tabs to M code line |
| TMDL008 | Remove excess tabs from M code line |
| TMDL009 | Change `source = {` to `expression := {` |
| TMDL010 | Put entire field parameter on single line |
| TMDL011 | Replace mixed indentation with pure tabs |
| TMDL012 | Add one tab before DAX expression, OR add triple backticks |
| TMDL013 | Remove duplicate property, keep first occurrence |

---

## Basic Structure

```tmdl
table TableName

	partition 'PartitionName' = m
		mode: Import
		source =
			let
				Source = ...,
				Step1 = ...,
				Step2 = ...
			in
				Step2
```

## Critical Formatting Rules

### 1. Indentation MUST Use Tabs

**Power BI requires tabs (`\t`), NOT spaces.**

```tmdl
table Sales

	partition 'Sales-Part1' = m     ← 1 tab before 'partition'
		mode: Import                 ← 2 tabs before 'mode'
		source =                     ← 2 tabs before 'source'
			let                      ← 3 tabs before M code
```

**Common Error:** Using spaces instead of tabs causes parsing errors.

### 2. Partition Declaration

Format: `partition 'PartitionName' = m`

- Name enclosed in single quotes
- Space before and after `=`
- Lowercase `m` (denotes M language)

**Examples:**
```tmdl
partition 'Sales' = m
partition 'Sales-Part1' = m
partition 'Customers-2024' = m
```

### 3. Mode Property

Specifies partition mode (2 tabs indentation):

```tmdl
		mode: Import           ← Most common
		mode: DirectQuery      ← For real-time data
		mode: Dual             ← Import + DirectQuery
```

### 4. Source Property

M code expression (2 tabs for `source =`, 3+ tabs for M code):

```tmdl
		source =
			let
				Source = Sql.Database("server", "database"),
				...
			in
				FinalStep
```

## M Code Block Structure

### Let-In Statement

All M partition code uses `let...in` structure:

```m
let
	Step1 = Value1,
	Step2 = Function(Step1),
	Step3 = Transform(Step2)
in
	Step3
```

**Rules:**
- Each step on new line
- Comma after each step EXCEPT the last
- Final step referenced in `in` statement
- Indentation: 3 tabs for steps (relative to `source =`)

### Step Naming

Use descriptive names, not generic Power Query defaults:

**Bad:**
```m
let
	Source = ...,
	#"Filtered Rows" = ...,
	#"Removed Columns" = ...,
	#"Changed Type" = ...
in
	#"Changed Type"
```

**Good:**
```m
let
	Source = Sql.Database("server", "db"),
	RawData = Source{[Schema="dbo",Item="Sales"]}[Data],
	ActiveCustomersOnly = Table.SelectRows(RawData, each [IsActive] = true),
	RelevantColumns = Table.SelectColumns(ActiveCustomersOnly, {"ID", "Name", "Amount"}),
	TypedColumns = Table.TransformColumnTypes(RelevantColumns, {{"Amount", type number}})
in
	TypedColumns
```

### Triple Backticks (Optional but Recommended)

For measures with properties at same indentation as DAX, backticks clarify boundaries. **For partitions, this is rarely needed** but may be used:

```tmdl
partition 'Sales' = m
	```
	mode: Import
	source =
		let
			Source = ...
		in
			Source
	```
```

**When to use backticks in partitions:**
- Complex multi-line partition definitions
- When TMDL parser reports ambiguity
- Rarely needed for standard partitions

## Complete Example

```tmdl
table Sales

	partition 'Sales-2024' = m
		mode: Import
		source =
			let
				// Connect to SQL Server
				Source = Sql.Database("prod-server.database.windows.net", "SalesDB"),

				// Navigate to Sales table
				SalesTable = Source{[Schema="dbo",Item="Sales"]}[Data],

				// Filter for 2024 only
				Sales2024 = Table.SelectRows(SalesTable, each [OrderDate] >= #date(2024,1,1) and [OrderDate] <= #date(2024,12,31)),

				// Remove internal columns
				CleanedData = Table.RemoveColumns(Sales2024, {"InternalID", "TempFlag"}),

				// Set correct data types
				TypedData = Table.TransformColumnTypes(CleanedData, {
					{"OrderDate", type date},
					{"Amount", type number},
					{"CustomerID", type text}
				})
			in
				TypedData
```

## Multiple Partitions (Rare)

Tables can have multiple partitions for incremental refresh:

```tmdl
table Sales

	partition 'Sales-2023' = m
		mode: Import
		source =
			let
				Source = Sql.Database("server", "db"),
				Data2023 = Table.SelectRows(Source, each [Year] = 2023)
			in
				Data2023

	partition 'Sales-2024' = m
		mode: Import
		source =
			let
				Source = Sql.Database("server", "db"),
				Data2024 = Table.SelectRows(Source, each [Year] = 2024)
			in
				Data2024
```

**When to use multiple partitions:**
- Incremental refresh scenarios
- Large historical datasets partitioned by time
- Different source systems for different periods

**Caution:** Adding partitions is complex and should be discussed with user first.

## Calculated Tables (M Code)

Calculated tables created with M code also use partition structure:

```tmdl
table DateTable

	partition DateTable = m
		mode: Import
		source =
			let
				StartDate = #date(2020, 1, 1),
				EndDate = #date(2030, 12, 31),
				DayCount = Duration.Days(EndDate - StartDate) + 1,
				DateList = List.Dates(StartDate, DayCount, #duration(1,0,0,0)),
				TableFromList = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
				TypedDate = Table.TransformColumnTypes(TableFromList, {{"Date", type date}}),
				AddYear = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), type number),
				AddMonth = Table.AddColumn(AddYear, "Month", each Date.Month([Date]), type number)
			in
				AddMonth
```

## Common Errors and Fixes

### Error: "Invalid indentation detected"

**Cause:** Spaces used instead of tabs

**Fix:** Replace all leading spaces with tabs
```python
# In editor script
line = line.replace('    ', '\t')  # 4 spaces → 1 tab
```

### Error: "Unexpected line type"

**Cause:** Missing or incorrect partition declaration

**Fix:** Ensure format is exactly `partition 'Name' = m`

### Error: "Syntax error in M expression"

**Cause:** M code syntax issues (missing comma, unmatched bracket, etc.)

**Fix:**
1. Check for trailing commas after last step
2. Verify all brackets matched: `[]`, `{}`, `()`
3. Ensure `in` statement references valid step name

### Error: "Property not supported in current context"

**Cause:** Properties at wrong indentation level

**Fix:**
- `mode:` and `source =` need exactly 2 tabs
- M code steps need 3+ tabs

## Indentation Reference Table

| Element | Tab Count | Example |
|---------|-----------|---------|
| `table` keyword | 0 | `table Sales` |
| `partition` keyword | 1 | `	partition 'Name' = m` |
| `mode` property | 2 | `		mode: Import` |
| `source` property | 2 | `		source =` |
| M code (`let/in`) | 3 | `			let` |
| M steps | 4 | `				Source = ...` |
| M step continuations | 5+ | `					{"ID", "Name"}` |

## Validation Checklist

Before saving partition changes:

- ✅ All indentation uses tabs (not spaces)
- ✅ Partition declaration format: `partition 'Name' = m`
- ✅ `mode:` and `source =` have 2 tabs
- ✅ M code block has 3+ tabs
- ✅ Each M step ends with comma (except last)
- ✅ `in` statement references valid step name
- ✅ No trailing commas after last step
- ✅ All brackets/parentheses matched
- ✅ Step names are descriptive (not #"Filtered Rows")
- ✅ Comments added for complex logic

## Integration with TMDL Validator

After editing partition M code, **always validate format.**

**Tool Selection (Try Tool First, Fallback to Claude-Native):**

1. **Check for Python validator:**
   ```bash
   test -f ".claude/tools/tmdl_format_validator.py" && echo "TOOL_AVAILABLE" || echo "TOOL_NOT_AVAILABLE"
   ```

2. **If tool available (Developer Edition - recommended):**
   ```bash
   python .claude/tools/tmdl_format_validator.py "<tmdl-file>" --context "Modified <TableName> partition"
   ```
   - Fast, comprehensive validation
   - Auto-fix capability for TMDL012 warnings
   - Precise line number reporting

3. **If tool NOT available (Analyst Edition):**
   - Read the TMDL file and manually verify:
     - All indentation uses tabs (count tab characters)
     - Property placement is correct (not inside DAX blocks)
     - TMDL structure follows patterns in this document
   - Use regex to check indentation patterns
   - Verify against examples in this reference

**The validator/validation checks:**
- Indentation consistency
- Property placement
- TMDL structure
- Partition syntax

**If validation reports errors, fix before proceeding to deployment.**

## Best Practices

1. **Descriptive step names** - Use meaningful names instead of Power Query defaults
2. **Comments for complex logic** - Add `//` comments explaining non-obvious transformations
3. **Consistent formatting** - Follow project patterns discovered by pattern analyzer
4. **Error handling** - Use `try...otherwise` for operations that might fail
5. **Query folding awareness** - Keep foldable steps first
6. **Version control** - Backup files created automatically by editor script
7. **Test in Power BI Desktop** - Verify partition loads correctly after editing
