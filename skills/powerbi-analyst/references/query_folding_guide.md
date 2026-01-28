# Query Folding Guide

## What is Query Folding?

Query folding is Power Query's ability to push transformations back to the data source (SQL Server, Azure, etc.) instead of loading all data into Power BI and transforming it there.

**Benefits:**
- ✅ Faster refresh times (source does the heavy lifting)
- ✅ Less memory usage in Power BI
- ✅ Reduced network traffic
- ✅ Leverages database indexes and optimization

**When it works:**
- Source supports query folding (SQL databases, Azure, etc.)
- Transformations can be translated to source query language (SQL)
- No operations that require Power BI's M engine

## Operations That Preserve Query Folding

### ✅ Always Safe (Translates to SQL)

**Filtering rows:**
```m
Table.SelectRows(Source, each [Amount] > 1000)
// Translates to: WHERE Amount > 1000
```

**Selecting columns:**
```m
Table.SelectColumns(Source, {"CustomerID", "Amount", "Date"})
// Translates to: SELECT CustomerID, Amount, Date
```

**Renaming columns:**
```m
Table.RenameColumns(Source, {{"old_name", "NewName"}})
// Translates to: SELECT old_name AS NewName
```

**Sorting:**
```m
Table.Sort(Source, {{"Amount", Order.Descending}})
// Translates to: ORDER BY Amount DESC
```

**Removing columns:**
```m
Table.RemoveColumns(Source, {"TempColumn", "InternalID"})
// Translates to: SELECT ... (excluding those columns)
```

**Basic aggregation:**
```m
Table.Group(Source, {"CustomerID"}, {{"Total", each List.Sum([Amount]), type number}})
// Translates to: GROUP BY CustomerID; SUM(Amount)
```

**Inner joins:**
```m
Table.NestedJoin(Sales, {"CustomerID"}, Customers, {"ID"}, "Customer", JoinKind.Inner)
// Translates to: INNER JOIN
```

### ⚠️ Usually Safe (Check Source Capabilities)

**Left outer joins:**
```m
Table.NestedJoin(Sales, {"CustomerID"}, Customers, {"ID"}, "Customer", JoinKind.LeftOuter)
// Translates to: LEFT JOIN
```

**Full outer joins:**
```m
// May not fold on all sources
Table.NestedJoin(TableA, {"ID"}, TableB, {"ID"}, "B", JoinKind.FullOuter)
```

**Distinct rows:**
```m
Table.Distinct(Source, {"CustomerID"})
// Translates to: SELECT DISTINCT
```

## Operations That Break Query Folding

### ❌ Always Breaks Folding

**Adding custom columns with M functions:**
```m
Table.AddColumn(Source, "FullName", each [FirstName] & " " & [LastName])
// Cannot translate to SQL - requires loading data
```

**Text operations:**
```m
Table.AddColumn(Source, "FirstInitial", each Text.Start([FirstName], 1))
// Text functions don't translate to SQL
```

**Date extractions (non-native):**
```m
Table.AddColumn(Source, "Year", each Date.Year([OrderDate]))
// May break folding depending on source
```

**Conditional columns:**
```m
Table.AddColumn(Source, "Category", each if [Amount] > 1000 then "High" else "Low")
// Complex logic breaks folding
```

**Merging with non-database sources:**
```m
Table.NestedJoin(DatabaseTable, {"ID"}, ExcelTable, {"ID"}, "Excel", JoinKind.Inner)
// One source isn't a database - cannot fold
```

**Appending non-database sources:**
```m
Table.Combine({DatabaseTable, CSVTable})
// Mixed sources break folding
```

**Pivot/Unpivot:**
```m
Table.Pivot(Source, List.Distinct(Source[Category]), "Category", "Amount")
// Too complex for SQL translation
```

**Grouping with complex aggregations:**
```m
Table.Group(Source, {"ID"}, {{"Custom", each Text.Combine([Names], ", "), type text}})
// Custom aggregation function breaks folding
```

### ❌ Advanced Operations

**Buffering (intentionally breaks):**
```m
Table.Buffer(Source)
// Explicitly loads data into memory
```

**List operations:**
```m
Table.AddColumn(Source, "Count", each List.Count([Items]))
// List functions don't translate to SQL
```

**Record operations:**
```m
Table.AddColumn(Source, "Data", each Record.FieldNames(_))
// Record functions break folding
```

## How to Check Query Folding

### In Power BI Desktop

1. Open Power Query Editor
2. Right-click on the last step before your custom transformation
3. If "View Native Query" is available → Query folding is working
4. If greyed out → Query folding is broken

### Common Breaking Points

Query folding typically breaks at the **first non-foldable step**. All subsequent steps also don't fold.

**Example:**
```m
let
    Source = Sql.Database("server", "db"),          // ✅ Folds
    Navigation = Source{[Schema="dbo"]}[Data],      // ✅ Folds
    FilterRows = Table.SelectRows(...),             // ✅ Folds
    AddedCustom = Table.AddColumn(...),             // ❌ BREAKS HERE
    FilterRows2 = Table.SelectRows(...),            // ❌ Doesn't fold
    RemovedColumns = Table.RemoveColumns(...)       // ❌ Doesn't fold
in
    RemovedColumns
```

Even though `FilterRows2` and `RemovedColumns` would normally fold, they don't because `AddedCustom` broke the chain.

## Strategies to Preserve Query Folding

### Strategy 1: Move Non-Foldable Steps to End

**Bad:**
```m
let
    Source = Sql.Database("server", "db"),
    AddFullName = Table.AddColumn(Source, "FullName", each [First] & " " & [Last]),  // Breaks folding
    FilterActive = Table.SelectRows(AddFullName, each [IsActive] = true)             // Doesn't fold
in
    FilterActive
```

**Good:**
```m
let
    Source = Sql.Database("server", "db"),
    FilterActive = Table.SelectRows(Source, each [IsActive] = true),          // ✅ Folds
    AddFullName = Table.AddColumn(FilterActive, "FullName", each [First] & " " & [Last])  // Breaks but on smaller dataset
in
    AddFullName
```

### Strategy 2: Use Native Database Functions

**Bad:**
```m
Table.AddColumn(Source, "Year", each Date.Year([OrderDate]))  // Breaks folding
```

**Good (if source supports):**
```m
// Use SQL expression in original query
let
    Source = Sql.Database("server", "db"),
    WithYear = Sql.Databases("server"){[Name="db"]}[Data]{[Schema="dbo",Item="vw_OrdersWithYear"]}[Data]
in
    WithYear
```

### Strategy 3: Create Views at Source

Instead of complex M transformations:
- Create SQL view at source with transformations
- Query the view in Power BI
- All operations stay at source

### Strategy 4: Accept the Break for Small Datasets

If dataset is small (<100K rows), breaking query folding may be acceptable:
- Refresh time is still fast
- M code is simpler and more maintainable
- Trade-off: Complexity vs Performance

**When to accept:**
- Dimension tables (< 100K rows)
- Reference tables
- Tables that rarely refresh
- Complex transformations unavoidable

**When to avoid:**
- Fact tables (millions of rows)
- Frequently refreshed datasets
- Large historical data
- Performance-critical scenarios

## Detecting Query Folding Breaks in M Code

### Red Flags

**Text operations on columns:**
- `Text.Start`, `Text.End`, `Text.Middle`
- `Text.Replace`, `Text.Combine`
- `&` (concatenation operator)

**Date/time extraction:**
- `Date.Year`, `Date.Month`, `Date.Day`
- `DateTime.Date`, `DateTime.Time`

**Custom columns with logic:**
- `if...then...else` statements
- `Table.AddColumn` with function

**List/Record operations:**
- `List.Sum`, `List.Count`, `List.Max`
- `Record.Field`, `Record.FieldNames`

**Non-native aggregations:**
- `Text.Combine` in aggregation
- Custom aggregation functions

## Query Folding Validation Workflow

1. **Identify transformation type** from user request
2. **Check against folding rules** (this guide)
3. **Determine if it breaks folding**
   - Yes → Warn user, present alternatives
   - No → Proceed confidently
4. **If breaks folding:**
   - Estimate dataset size impact
   - Suggest foldable alternatives if available
   - Get user confirmation before applying

## Example Validation

**User Request:** "Add a FullName column combining FirstName and LastName"

**Analysis:**
- Transformation: Custom column with text concatenation
- Query folding impact: ❌ **BREAKS FOLDING**
- Reason: `&` operator and `Table.AddColumn` don't translate to SQL

**Warning to user:**
```
⚠️ QUERY FOLDING WARNING

The proposed transformation will break query folding:
- Transformation: Add FullName column (FirstName & " " & LastName)
- Impact: All data will be loaded into Power BI before concatenation
- Dataset size: ~500K rows

Recommendations:
1. ✅ Proceed (Acceptable for this dataset size)
2. Consider creating a view at source with FullName pre-calculated
3. Apply this transformation last to minimize data loaded

Continue with this transformation? [Y/N]
```

## References

- [Microsoft Docs: Query Folding](https://learn.microsoft.com/en-us/power-query/power-query-folding)
- [Query Folding Indicators](https://learn.microsoft.com/en-us/power-query/step-folding-indicators)
