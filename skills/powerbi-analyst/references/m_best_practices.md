# M Code Best Practices

Style guide and optimization techniques for Power Query M code in Power BI projects.

## Naming Conventions

### Step Names

**Use descriptive, action-oriented names:**

**Bad:**
```m
#"Filtered Rows"
#"Removed Columns"
#"Changed Type"
```

**Good:**
```m
ActiveCustomersOnly
RemoveInternalColumns
SetCorrectDataTypes
```

**Patterns:**
- Start with verb: `Filter`, `Remove`, `Add`, `Transform`, `Select`
- Be specific: `FilterActiveCustomers` not `FilterData`
- Use PascalCase or snake_case consistently within project

### Table and Column Names

**Follow project patterns** discovered by pattern analyzer:

```m
// If project uses PascalCase
CustomerName
OrderDate
TotalAmount

// If project uses snake_case
customer_name
order_date
total_amount
```

**Guidelines:**
- No spaces in names (use camelCase or snake_case)
- Descriptive, not cryptic: `CustomerID` not `CID`
- Consistent abbreviations: If using `ID`, use it everywhere (not mixing `ID`, `Id`, `id`)

## Code Organization

### Let-In Structure

Always use `let...in` for partition M code:

```m
let
	// 1. Connection
	Source = Sql.Database("server", "database"),

	// 2. Navigation
	RawTable = Source{[Schema="dbo",Item="Sales"]}[Data],

	// 3. Filtering
	ActiveOnly = Table.SelectRows(RawTable, each [IsActive] = true),

	// 4. Column selection
	RelevantColumns = Table.SelectColumns(ActiveOnly, {"ID", "Name", "Amount"}),

	// 5. Type conversion
	TypedData = Table.TransformColumnTypes(RelevantColumns, {{"Amount", type number}})
in
	TypedData
```

**Logical grouping:**
1. Connection/source
2. Navigation
3. Filtering (keep data small early)
4. Transformations
5. Type conversion (last)

### Comments

Add comments for:
- Complex logic
- Business rules
- Non-obvious transformations
- Why specific approach was chosen

```m
let
	Source = Sql.Database("server", "db"),

	// Filter to active customers only (business requirement from 2024-01-15)
	ActiveCustomers = Table.SelectRows(Source, each [Status] = "Active"),

	// Calculate discount: 10% for > $1000, 5% otherwise (pricing team requirement)
	WithDiscount = Table.AddColumn(ActiveCustomers, "Discount", each
		if [TotalPurchases] > 1000 then 0.10 else 0.05
	)
in
	WithDiscount
```

## Performance Optimization

### 1. Filter Early, Filter Often

**Bad (loads all data then filters):**
```m
let
	Source = Sql.Database("server", "db"),
	AllData = Source{[Schema="dbo",Item="Sales"]}[Data],
	AddedColumns = Table.AddColumn(AllData, "Year", each Date.Year([OrderDate])),
	Filtered2024 = Table.SelectRows(AddedColumns, each [Year] = 2024)
in
	Filtered2024
```

**Good (filters early):**
```m
let
	Source = Sql.Database("server", "db"),
	AllData = Source{[Schema="dbo",Item="Sales"]}[Data],
	Filtered2024 = Table.SelectRows(AllData, each [OrderDate] >= #date(2024,1,1) and [OrderDate] <= #date(2024,12,31)),
	AddedColumns = Table.AddColumn(Filtered2024, "Year", each Date.Year([OrderDate]))
in
	AddedColumns
```

### 2. Remove Unnecessary Columns Early

**Bad:**
```m
let
	Source = ...,
	Filtered = Table.SelectRows(Source, ...), // Loads all 50 columns
	RemovedColumns = Table.RemoveColumns(Filtered, {"Col1", "Col2", ..., "Col45"}) // Finally removes 45 columns
in
	RemovedColumns
```

**Good:**
```m
let
	Source = ...,
	SelectedColumns = Table.SelectColumns(Source, {"ID", "Name", "Amount", "Date", "Status"}), // Only load 5 columns
	Filtered = Table.SelectRows(SelectedColumns, ...)
in
	Filtered
```

### 3. Preserve Query Folding

Keep foldable operations before non-foldable:

```m
let
	Source = Sql.Database("server", "db"),

	// ✅ These fold to SQL
	Filtered = Table.SelectRows(Source, each [Amount] > 1000),
	Selected = Table.SelectColumns(Filtered, {"ID", "Amount", "Date"}),
	Sorted = Table.Sort(Selected, {{"Amount", Order.Descending}}),

	// ❌ This breaks folding - but on smaller dataset
	WithCategory = Table.AddColumn(Sorted, "Category", each
		if [Amount] > 10000 then "High" else "Low"
	)
in
	WithCategory
```

### 4. Use Table.Buffer Strategically

Only buffer when table is referenced multiple times:

**Without buffer (queries source twice):**
```m
let
	Source = Sql.Database("server", "db"),
	MaxAmount = List.Max(Source[Amount]),  // Query 1
	Filtered = Table.SelectRows(Source, each [Amount] = MaxAmount)  // Query 2
in
	Filtered
```

**With buffer (queries source once):**
```m
let
	Source = Sql.Database("server", "db"),
	Buffered = Table.Buffer(Source),  // Cache result
	MaxAmount = List.Max(Buffered[Amount]),
	Filtered = Table.SelectRows(Buffered, each [Amount] = MaxAmount)
in
	Filtered
```

**Caution:** `Table.Buffer` breaks query folding. Use only when necessary.

## Error Handling

### Try-Otherwise Pattern

Wrap operations that might fail:

```m
let
	Source = ...,

	// Division might fail if Quantity is zero
	SafeDivision = Table.AddColumn(Source, "UnitPrice", each
		try [Revenue] / [Quantity] otherwise null
	)
in
	SafeDivision
```

### Null Handling

Always handle nulls in calculations:

**Bad:**
```m
// Fails if Amount is null
TotalWithTax = [Amount] * 1.08
```

**Good:**
```m
// Returns null if Amount is null
TotalWithTax = if [Amount] = null then null else [Amount] * 1.08
```

**Better (using null-coalescing):**
```m
// Treats null as 0
TotalWithTax = ([Amount] ?? 0) * 1.08
```

## Code Reusability

### Use Parameters

Create parameters for values that change:

**Bad (hardcoded):**
```m
Table.SelectRows(Source, each [OrderDate] >= #date(2024,1,1))
```

**Good (parameterized):**
```m
// Parameter: StartDate = #date(2024,1,1)
Table.SelectRows(Source, each [OrderDate] >= StartDate)
```

### Custom Functions

For repeated logic, create custom functions:

```m
// Custom function to calculate discount
(orderAmount as number) as number =>
	if orderAmount > 10000 then orderAmount * 0.10
	else if orderAmount > 1000 then orderAmount * 0.05
	else 0
```

Use in table:
```m
AddDiscount = Table.AddColumn(Source, "Discount", each CalculateDiscount([OrderAmount]))
```

## Data Type Best Practices

### Explicit Type Conversion

Always specify types explicitly:

```m
Table.TransformColumnTypes(Source, {
	{"OrderDate", type date},
	{"Amount", type number},
	{"CustomerID", type text},
	{"IsActive", type logical}
})
```

### Type Hints in AddColumn

Specify type when adding columns:

```m
Table.AddColumn(Source, "FullName", each [FirstName] & " " & [LastName], type text)
Table.AddColumn(Source, "Total", each [Qty] * [Price], type number)
```

## Common Anti-Patterns

### ❌ Anti-Pattern 1: Loading Full Table Before Filtering

```m
// Loads millions of rows then filters
let
	Source = Sql.Database("server", "db"),
	AllSales = Source{[Schema="dbo",Item="Sales"]}[Data],
	FilteredSales = Table.SelectRows(AllSales, each [Year] = 2024)
in
	FilteredSales
```

**Fix:** Filter at source level if possible, or filter immediately after navigation.

### ❌ Anti-Pattern 2: Multiple Steps for Same Column

```m
// Three separate steps to transform one column
RenamedAmount = Table.RenameColumns(Source, {{"Amt", "Amount"}}),
TypedAmount = Table.TransformColumnTypes(RenamedAmount, {{"Amount", type number}}),
RoundedAmount = Table.TransformColumns(TypedAmount, {{"Amount", Number.Round}})
```

**Fix:** Combine operations:
```m
TransformedAmount = Table.TransformColumns(
	Table.RenameColumns(Source, {{"Amt", "Amount"}}),
	{{"Amount", each Number.Round(Number.From(_)), type number}}
)
```

### ❌ Anti-Pattern 3: Using #"Step Names" with Special Characters

```m
#"Filtered Rows"
#"Changed Type1"
#"Removed Other Columns"
```

**Fix:** Use descriptive names without special characters:
```m
ActiveCustomersOnly
SetDataTypes
SelectRelevantColumns
```

### ❌ Anti-Pattern 4: No Error Handling on Risky Operations

```m
// Fails if Quantity is zero or null
Ratio = [Revenue] / [Quantity]
```

**Fix:**
```m
Ratio = try [Revenue] / [Quantity] otherwise null
// Or with explicit checks
Ratio = if [Quantity] = null or [Quantity] = 0 then null else [Revenue] / [Quantity]
```

## Formatting Standards

### Indentation

Use consistent indentation (3-4 tabs per TMDL structure):

```m
let
	Source = ...,
	Filtered = Table.SelectRows(
		Source,
		each [Amount] > 1000
	),
	Transformed = Table.TransformColumnTypes(
		Filtered,
		{
			{"Amount", type number},
			{"Date", type date}
		}
	)
in
	Transformed
```

### Line Length

Break long lines for readability:

**Bad:**
```m
Filtered = Table.SelectRows(Source, each [Amount] > 1000 and [Status] = "Active" and [Region] = "North" and [Category] <> "Excluded")
```

**Good:**
```m
Filtered = Table.SelectRows(Source, each
	[Amount] > 1000
	and [Status] = "Active"
	and [Region] = "North"
	and [Category] <> "Excluded"
)
```

### Alignment

Align similar operations for readability:

```m
Table.TransformColumnTypes(Source, {
	{"OrderDate",   type date},
	{"Amount",      type number},
	{"CustomerID",  type text},
	{"IsActive",    type logical}
})
```

## Documentation

### Inline Comments

```m
let
	// Connect to production SQL Server
	Source = Sql.Database("prod-server", "SalesDB"),

	// Get raw sales data
	RawSales = Source{[Schema="dbo",Item="Sales"]}[Data],

	// Business rule: Only include sales from active customers (defined as Status = 'A')
	// Per requirement SR-2024-015 from 2024-01-20
	ActiveSalesOnly = Table.SelectRows(RawSales, each [CustomerStatus] = "A"),

	// Remove PII columns per data governance policy
	WithoutPII = Table.RemoveColumns(ActiveSalesOnly, {"SSN", "CreditCard", "Email"})
in
	WithoutPII
```

### Header Comments

For complex partitions, add header explaining purpose:

```m
// ==============================================================================
// Sales Data - Filtered for Active Customers Only
// ==============================================================================
// Purpose: Provide sales data for reporting, excluding inactive customers
// Source: Production SQL Server (prod-server.database.windows.net)
// Refresh: Daily at 2 AM UTC
// Last Modified: 2024-11-19 by Jane Doe
// Change Log:
//   - 2024-11-19: Added revenue category classification
//   - 2024-10-15: Removed PII columns per DG policy
// ==============================================================================

let
	Source = Sql.Database("prod-server", "SalesDB"),
	...
in
	Result
```

## Performance Checklist

Before finalizing M code changes:

- ✅ Foldable operations before non-foldable?
- ✅ Filtering applied early?
- ✅ Unnecessary columns removed early?
- ✅ Data types explicitly set?
- ✅ Error handling for risky operations?
- ✅ Query folding validated and breaks documented?
- ✅ Comments added for complex logic?
- ✅ Step names are descriptive?
- ✅ No hardcoded values (use parameters)?
- ✅ Tested refresh time acceptable?

## Project-Specific Patterns

**Always check project patterns first** using `m_pattern_analyzer.py`:

- Naming convention (PascalCase, snake_case, etc.)
- Comment style (if any)
- Error handling approach
- Parameter usage patterns
- Custom function patterns

**Follow project conventions for consistency**, even if they differ from general best practices.
