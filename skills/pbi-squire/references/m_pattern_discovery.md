# M Code Pattern Discovery

Complete guide for discovering and applying M code patterns in Power BI projects. Supports both Developer Edition (Python tool) and Analyst Edition (Claude-native analysis).

---

## Quick Reference

| Edition | Pattern Discovery Method |
|---------|-------------------------|
| **Pro** | Run `m_pattern_analyzer.py` → structured JSON output |
| **Core** | Use Grep/Read tools → apply detection rules below |

---

## Part 1: Pattern Detection (Claude-Native)

When Python tool is not available, use these instructions to discover patterns by scanning TMDL files directly.

### Step 1: Find M Code Partitions

**Locate all partition definitions:**

```
Grep pattern: partition\s+'[^']+'\s*=\s*m
Path: <project>/.SemanticModel/definition/tables/
```

**For each partition found, extract:**
1. Partition name (in single quotes)
2. M code block (after `source =` until next `partition` or `table` keyword)

### Step 2: Analyze Naming Conventions

**Scan step names (lines matching `StepName = ...`):**

| Pattern | Regex | Example |
|---------|-------|---------|
| PascalCase | `^[A-Z][a-z]+(?:[A-Z][a-z]+)*$` | `FilterActiveCustomers` |
| camelCase | `^[a-z]+(?:[A-Z][a-z]+)*$` | `filterActiveCustomers` |
| snake_case | `^[a-z]+(?:_[a-z]+)*$` | `filter_active_customers` |
| Default (Power Query) | `^#".*"$` | `#"Filtered Rows"` |

**Count occurrences of each style and calculate percentages.**

**Skip M keywords:** `let`, `in`, `each`, `and`, `or`, `not`, `true`, `false`, `null`

**Report:**
```
Naming Style Analysis:
- PascalCase: X% (N occurrences) ← dominant if >50%
- snake_case: Y% (M occurrences)
- Default names: Z% (K occurrences) ← anti-pattern
```

### Step 3: Analyze Transformation Patterns

**Search for these function patterns in M code:**

| Function | What It Indicates | Search Pattern |
|----------|-------------------|----------------|
| `Sql.Database(` | SQL connection style | Note server format (FQDN vs short name) |
| `Table.SelectRows(` | Row filtering | Check single-line vs multi-line format |
| `Table.SelectColumns(` | Column selection | Check position in pipeline (early vs late) |
| `Table.RemoveColumns(` | Column removal | Alternative to SelectColumns |
| `Table.AddColumn(` | Custom columns | Note naming pattern for new columns |
| `Table.TransformColumnTypes(` | Type setting | Check inline vs list format |
| `Table.NestedJoin(` or `Table.Join(` | Merge operations | Note join type preferences |
| `Table.Group(` | Aggregations | Note aggregation patterns |
| `#date(` | Date literals | Indicates hardcoded vs parameterized dates |

**Report:**
```
Transformation Patterns Found:
- SQL Connections: N partitions (server format: FQDN/short)
- Row Filtering: N partitions (single-line/multi-line: X%/Y%)
- Column Selection: N partitions (early/late in pipeline: X%/Y%)
- Date Literals: N partitions (hardcoded dates present)
```

### Step 4: Analyze Code Organization

**Check for comments:**

| Comment Style | Pattern |
|---------------|---------|
| Single-line | `//` at start of line or after code |
| Multi-line | `/* ... */` blocks |

**Check for logical grouping:**
- Blank lines between step groups
- Section comments (e.g., `// Connection`, `// Filtering`)

**Report:**
```
Code Organization:
- Comments: X% of partitions have comments
  - Style: Single-line (//): N occurrences
  - Style: Multi-line (/* */): M occurrences
- Blank line grouping: X% of partitions use blank lines between sections
```

### Step 5: Analyze Error Handling

**Search for try-otherwise patterns:**

```
Pattern: try\s+.*\s+otherwise\s+(\w+|null|0|"")
```

**Count fallback value usage:**

| Fallback | Meaning |
|----------|---------|
| `null` | Returns blank for errors |
| `0` | Returns zero for errors |
| `""` | Returns empty string |
| Other | Custom default value |

**Report:**
```
Error Handling:
- try-otherwise usage: X% of partitions
- Common fallback values:
  - null: N occurrences
  - 0: M occurrences
```

### Step 6: Analyze Parameter Usage

**Search for parameter-like names:**

```
Pattern: \b([A-Z][a-zA-Z]+(?:Date|Name|Path|Server|Database|URL|Key|Value))\b
```

**Common parameters to detect:**
- `ServerName`, `DatabaseName` - connection parameters
- `StartDate`, `EndDate` - date range parameters
- `FilePath`, `FolderPath` - file source parameters

**Report:**
```
Parameter Usage:
- Likely parameters found: N
- Examples: ServerName, StartDate, EndDate
- Usage: Direct reference (vs intermediate variable)
```

### Step 7: Generate Recommendations

Based on analysis, provide recommendations:

**Naming:**
- If one style >50%: "Use [style] for new step names (dominant pattern)"
- If mixed: "Mixed naming styles detected - recommend standardizing on [majority]"

**Organization:**
- If comments >30%: "Comments are commonly used - add comments for complex logic"
- If comments <30%: "Low comment usage - consider adding comments for maintainability"

**Error Handling:**
- If try-otherwise >20%: "Error handling is used - apply try-otherwise for risky operations"
- If try-otherwise <20%: "Limited error handling - consider adding try-otherwise where needed"

---

## Part 2: Pattern Application

Once patterns are discovered (via Python tool or Claude-native analysis), apply them consistently.

### Naming Conventions

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

### Transformation Patterns

**SQL connections - match server format:**
```m
// Project pattern uses fully qualified server names
Source = Sql.Database("prod-sql.company.com", "SalesDB")

// NOT (if FQDN is the pattern):
Source = Sql.Database("PROD-SQL", "SalesDB")
```

**Filtering - match line format:**
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

**Column selection - match pipeline position:**
```m
// Project pattern: select columns early, after navigation
let
	Source = Sql.Database(...),
	Navigation = Source{[Schema="dbo",Item="Sales"]}[Data],
	SelectedColumns = Table.SelectColumns(Navigation, {"ID", "Amount", "Date"}),  // ← Early
	Filtered = Table.SelectRows(SelectedColumns, each [Amount] > 1000)
in
	Filtered

// NOT (if early selection is the pattern):
let
	Source = Sql.Database(...),
	Navigation = Source{[Schema="dbo",Item="Sales"]}[Data],
	Filtered = Table.SelectRows(Navigation, each [Amount] > 1000),
	SelectedColumns = Table.SelectColumns(Filtered, {"ID", "Amount", "Date"})  // ← Late
in
	SelectedColumns
```

### Code Organization

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

**Match comment style:**
```m
// Project pattern: comments above step (not inline)

// Filter for active customers per business requirement SR-2024-015
ActiveOnly = Table.SelectRows(...)

// NOT (if above-step is the pattern):
ActiveOnly = Table.SelectRows(...)  // Filter active customers
```

### Error Handling

**Match fallback value pattern:**
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

### Parameter Usage

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

**For date filtering with parameters:**
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

---

## Part 3: Pattern Priority

When multiple patterns exist, prioritize:

1. **Consistency within table** - If editing existing partition, match its current style
2. **Majority pattern** - If creating new partition, follow most common pattern (>50%)
3. **Best practices** - If no clear pattern, follow M best practices guide
4. **User preference** - If patterns conflict or unclear, ask user

### Pattern Confidence Levels

| Confidence | Threshold | Action |
|------------|-----------|--------|
| High | >80% | Follow pattern strictly |
| Medium | 50-80% | Follow pattern, note alternatives |
| Low | <50% | Ask user or use best practices |

### Handling Pattern Conflicts

**Scenario:** Pattern analyzer shows 55% PascalCase, 45% snake_case

**Resolution:**
1. Check which pattern is used in the table being edited (if editing)
2. If creating new, ask user: "I notice the project uses both PascalCase (55%) and snake_case (45%). Which would you prefer for new code?"
3. Document chosen pattern for future consistency

---

## Part 4: Complete Example

**Pattern Discovery Output Summary:**
- Naming: PascalCase for steps, tables, columns (87%)
- Filtering: Multi-line format for complex conditions (72%)
- Organization: Logical groups with blank lines, comments above steps (45%)
- Error Handling: try-otherwise with null for division (34%)
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
	source = Sql.Database("PROD-SQL", "SalesDB"),  // ❌ lowercase, short server name
	raw_data = source{[Schema="dbo",Item="Sales"]}[Data],  // ❌ snake_case
	#"Filtered Rows" = Table.SelectRows(raw_data, each [OrderDate] >= #date(2024,1,1) and [OrderDate] <= #date(2024,12,31) and [Status] = "Active" and [Revenue] > 1000),  // ❌ default name, single-line, hardcoded dates
	selected = Table.SelectColumns(#"Filtered Rows", {"CustomerID", "OrderDate", "Revenue", "Status"})  // ❌ late column selection
in
	selected
```

---

## Checklist

Before applying M code changes:

- [ ] Discovered patterns using Python tool OR Claude-native analysis
- [ ] Matched naming convention (PascalCase, snake_case, etc.)
- [ ] Followed transformation patterns (multi-line filtering, column selection timing)
- [ ] Used code organization pattern (blank lines, comment style)
- [ ] Applied error handling pattern (try-otherwise usage and fallback values)
- [ ] Used parameters if project pattern indicates
- [ ] Resolved any pattern conflicts with user
- [ ] Documented any deviations from patterns with rationale

---

## See Also

- [M Best Practices](m_best_practices.md) - Default patterns when project has none
- [Query Folding Guide](query_folding_guide.md) - Performance-aware transformations
- [Tool Fallback Pattern](tool-fallback-pattern.md) - Pro vs Core tool usage
