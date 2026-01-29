# TMDL Partition Structure

Complete specification for M code partition formatting in TMDL files.

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

2. **If tool available (Pro edition - recommended):**
   ```bash
   python .claude/tools/tmdl_format_validator.py "<tmdl-file>" --context "Modified <TableName> partition"
   ```
   - Fast, comprehensive validation
   - Auto-fix capability for TMDL012 warnings
   - Precise line number reporting

3. **If tool NOT available (Core edition):**
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
