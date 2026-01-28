# M Code Pattern Discovery - Interpretation Guide

How to interpret output from `m_pattern_analyzer.py` and apply discovered patterns to new transformations.

## Pattern Analyzer Output Structure

The analyzer scans all partition M code in the project and reports:

1. **Naming Conventions** - How steps, tables, and columns are named
2. **Transformation Patterns** - Common M code structures and approaches
3. **Code Organization** - How M code is structured and commented
4. **Error Handling** - Whether try-otherwise is used and where
5. **Parameter Usage** - If and how parameters are used

## Section 1: Naming Conventions

### Example Output

```
=== NAMING CONVENTIONS ===

Step Names:
- Style: PascalCase (87% of steps)
- Examples: "FilterActiveCustomers", "RemoveInternalColumns", "SetDataTypes"
- Anti-pattern: 23% still use default names like "#"Filtered Rows""

Table Names:
- Style: PascalCase
- Examples: "Sales", "Customer", "Product", "OrderDetails"
- Pattern: Singular names (not plural)

Column Names:
- Style: PascalCase
- Examples: "CustomerID", "OrderDate", "TotalAmount"
- Pattern: Abbreviations: "ID" (not "Id"), "Qty" (not "Quantity")
```

### How to Apply

**When adding new steps:**
```m
// Project uses PascalCase → follow it
FilterActiveOrders = Table.SelectRows(...)

// NOT:
filter_active_orders = Table.SelectRows(...)
#"Filtered Rows" = Table.SelectRows(...)
```

**When creating tables:**
```m
// Project uses singular PascalCase → follow it
table DateDimension

// NOT:
table date_dimensions
table DateDimensions
```

**When naming columns:**
```m
// Project uses "ID" not "Id" → follow it
Table.AddColumn(..., "CustomerID", ...)

// NOT:
Table.AddColumn(..., "CustomerId", ...)
Table.AddColumn(..., "customer_id", ...)
```

## Section 2: Transformation Patterns

### Example Output

```
=== TRANSFORMATION PATTERNS ===

SQL Database Connections:
- Pattern: Sql.Database("server", "database") (100% of connections)
- Server format: Fully qualified domain names
- Example: Sql.Database("prod-sql.company.com", "SalesDB")

Filtering:
- Pattern: Table.SelectRows with simple conditions (93%)
- Complex conditions: Multi-line format (72%)
Example:
	Filtered = Table.SelectRows(Source, each
		[Amount] > 1000
		and [Status] = "Active"
	)

Column Selection:
- Pattern: Table.SelectColumns early in pipeline (85%)
- Typically after navigation, before filtering
Example:
	Selected = Table.SelectColumns(Source, {
		"CustomerID",
		"OrderDate",
		"Amount",
		"Status"
	})

Date Filtering:
- Pattern: Hardcoded date literals (67%)
- Format: #date(YYYY, M, D)
Example:
	Filtered = Table.SelectRows(Source, each
		[OrderDate] >= #date(2024, 1, 1)
	)
```

### How to Apply

**For SQL connections:**
```m
// Project pattern uses fully qualified server names
Source = Sql.Database("prod-sql.company.com", "SalesDB")

// NOT (if pattern says otherwise):
Source = Sql.Database("PROD-SQL", "SalesDB")
```

**For filtering:**
```m
// Project uses multi-line format for complex conditions
Filtered = Table.SelectRows(Source, each
	[Amount] > 1000
	and [Status] = "Active"
	and [Region] = "North"
)

// NOT (if multi-line is the pattern):
Filtered = Table.SelectRows(Source, each [Amount] > 1000 and [Status] = "Active" and [Region] = "North")
```

**For column selection:**
```m
// Project pattern: select columns early, after navigation
let
	Source = Sql.Database(...),
	Navigation = Source{[Schema="dbo",Item="Sales"]}[Data],
	SelectedColumns = Table.SelectColumns(Navigation, {"ID", "Amount", "Date"}),  ← Early
	Filtered = Table.SelectRows(SelectedColumns, each [Amount] > 1000)
in
	Filtered

// NOT (if early selection is the pattern):
let
	Source = Sql.Database(...),
	Navigation = Source{[Schema="dbo",Item="Sales"]}[Data],
	Filtered = Table.SelectRows(Navigation, each [Amount] > 1000),
	SelectedColumns = Table.SelectColumns(Filtered, {"ID", "Amount", "Date"})  ← Late
in
	SelectedColumns
```

## Section 3: Code Organization

### Example Output

```
=== CODE ORGANIZATION ===

Step Grouping:
- Pattern: Logical sections with blank lines between groups
Example:
	let
		// Connection
		Source = Sql.Database(...),

		// Navigation
		RawData = Source{[Schema="dbo",Item="Sales"]}[Data],

		// Filtering
		FilteredData = Table.SelectRows(RawData, ...),

		// Type conversion
		TypedData = Table.TransformColumnTypes(FilteredData, ...)
	in
		TypedData

Comments:
- Frequency: 45% of partitions have comments
- Style: Single-line comments with "//"
- Location: Above step (not inline)
Example:
	// Filter for active customers only (business requirement)
	ActiveOnly = Table.SelectRows(...)
```

### How to Apply

**Use blank lines to separate logical groups:**
```m
let
	// Connection
	Source = Sql.Database("server", "db"),

	// Navigation
	RawData = Source{[Schema="dbo",Item="Sales"]}[Data],

	// Filtering
	ActiveOnly = Table.SelectRows(RawData, each [IsActive] = true),

	// Transformations
	WithCategory = Table.AddColumn(ActiveOnly, "Category", each ...)
in
	WithCategory
```

**Add comments above steps (not inline):**
```m
// Project pattern: comments above step

// Filter for active customers per business requirement SR-2024-015
ActiveOnly = Table.SelectRows(...)

// NOT (if above-step is the pattern):
ActiveOnly = Table.SelectRows(...)  // Filter active customers
```

## Section 4: Error Handling

### Example Output

```
=== ERROR HANDLING ===

Try-Otherwise Usage:
- Frequency: 34% of partitions
- Pattern: Used for division and date parsing
- Fallback: null (78%), 0 (15%), default value (7%)

Examples:
	// Division with null fallback
	SafeDivision = Table.AddColumn(Source, "Ratio", each
		try [Revenue] / [Quantity] otherwise null
	)

	// Date parsing with null fallback
	SafeDate = Table.AddColumn(Source, "ParsedDate", each
		try Date.From([DateText]) otherwise null
	)
```

### How to Apply

**For division:**
```m
// Project pattern: try-otherwise with null fallback
WithRatio = Table.AddColumn(Source, "UnitPrice", each
	try [Revenue] / [Quantity] otherwise null
)

// NOT (if null is the pattern):
WithRatio = Table.AddColumn(Source, "UnitPrice", each
	try [Revenue] / [Quantity] otherwise 0
)
```

**For date/type conversions:**
```m
// Project pattern: try-otherwise with null for type conversions
WithDate = Table.AddColumn(Source, "OrderDate", each
	try Date.From([DateString]) otherwise null
)
```

## Section 5: Parameter Usage

### Example Output

```
=== PARAMETER USAGE ===

Parameters Found: 3
- ServerName (type text): Used in all SQL connections
- StartDate (type date): Used in date filtering (5 partitions)
- EndDate (type date): Used in date filtering (5 partitions)

Pattern: Parameters referenced directly (no intermediate variables)
Example:
	Source = Sql.Database(ServerName, "SalesDB")
	Filtered = Table.SelectRows(Source, each
		[OrderDate] >= StartDate
		and [OrderDate] <= EndDate
	)
```

### How to Apply

**Use parameters for values that change:**
```m
// Project pattern: reference parameters directly
Source = Sql.Database(ServerName, "SalesDB")

// NOT (if direct reference is the pattern):
let
	Server = ServerName,
	Source = Sql.Database(Server, "SalesDB")
...
```

**For date filtering:**
```m
// Project pattern: use StartDate/EndDate parameters
Filtered = Table.SelectRows(Source, each
	[OrderDate] >= StartDate
	and [OrderDate] <= EndDate
)

// NOT (if parameters exist):
Filtered = Table.SelectRows(Source, each
	[OrderDate] >= #date(2024, 1, 1)
	and [OrderDate] <= #date(2024, 12, 31)
)
```

## Pattern Priority

When multiple patterns exist, prioritize:

1. **Consistency within table** - If editing existing partition, match its current style
2. **Majority pattern** - If creating new partition, follow most common pattern (>50%)
3. **Best practices** - If no clear pattern, follow M best practices guide
4. **User preference** - If patterns conflict or unclear, ask user

## Example: Applying All Patterns

**Pattern Discovery Output Summary:**
- Naming: PascalCase for steps, tables, columns
- Filtering: Multi-line format for complex conditions
- Organization: Logical groups with blank lines, comments above steps
- Error Handling: try-otherwise with null for division
- Parameters: StartDate/EndDate used for date filtering

**New Transformation Request:** "Filter sales for active customers in 2024 with revenue > $1000"

**Correctly Applied Pattern:**
```m
let
	// Connection
	Source = Sql.Database("prod-sql.company.com", "SalesDB"),

	// Navigation
	RawSales = Source{[Schema="dbo",Item="Sales"]}[Data],

	// Column selection (early, per project pattern)
	RelevantColumns = Table.SelectColumns(RawSales, {
		"CustomerID",
		"OrderDate",
		"Revenue",
		"Status"
	}),

	// Filtering (multi-line format, using parameters)
	FilteredSales = Table.SelectRows(RelevantColumns, each
		[OrderDate] >= StartDate
		and [OrderDate] <= EndDate
		and [Status] = "Active"
		and [Revenue] > 1000
	),

	// Type conversion
	TypedData = Table.TransformColumnTypes(FilteredSales, {
		{"OrderDate", type date},
		{"Revenue", type number}
	})
in
	TypedData
```

**Inconsistent (violates discovered patterns):**
```m
let
	// Single-line connection
	source = Sql.Database("PROD-SQL", "SalesDB"),  // ❌ lowercase, short server name
	raw_data = source{[Schema="dbo",Item="Sales"]}[Data],  // ❌ snake_case
	#"Filtered Rows" = Table.SelectRows(raw_data, each [OrderDate] >= #date(2024,1,1) and [OrderDate] <= #date(2024,12,31) and [Status] = "Active" and [Revenue] > 1000),  // ❌ default name, single-line, hardcoded dates
	selected = Table.SelectColumns(#"Filtered Rows", {"CustomerID", "OrderDate", "Revenue", "Status"})  // ❌ late column selection
in
	selected
```

## Handling Pattern Conflicts

**Scenario:** Pattern analyzer shows 55% PascalCase, 45% snake_case

**Resolution:**
1. Check which pattern is used in the table being edited (if editing)
2. If creating new, ask user: "I notice the project uses both PascalCase (55%) and snake_case (45%). Which would you prefer for new code?"
3. Document chosen pattern for future consistency

## Pattern Confidence Levels

Analyzer reports confidence based on consistency:

- **High confidence (>80%)**: Follow pattern strictly
- **Medium confidence (50-80%)**: Follow pattern but note alternatives
- **Low confidence (<50%)**: Patterns inconsistent, ask user or use best practices

**Example:**
```
Step naming: PascalCase (87% - High Confidence)
→ Use PascalCase for all new steps

Column alignment: Varied (42% aligned, 58% not - Low Confidence)
→ Ask user preference or default to aligned (best practice)
```

## Summary Checklist

Before applying M code changes:

- ✅ Ran `m_pattern_analyzer.py` to discover project patterns
- ✅ Matched naming convention (PascalCase, snake_case, etc.)
- ✅ Followed transformation patterns (multi-line filtering, column selection timing, etc.)
- ✅ Used code organization pattern (blank lines, comment style, etc.)
- ✅ Applied error handling pattern (try-otherwise usage and fallback values)
- ✅ Used parameters if project pattern indicates
- ✅ Resolved any pattern conflicts with user
- ✅ Documented any deviations from patterns with rationale
