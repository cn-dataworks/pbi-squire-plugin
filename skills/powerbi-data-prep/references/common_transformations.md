# Common M Code Transformations

Library of frequently-used Power Query transformations with M code snippets, query folding impact, and usage guidance.

## Table of Contents

- [Filtering Operations](#filtering-operations)
- [Column Operations](#column-operations)
- [Table Combination](#table-combination)
- [Aggregation](#aggregation)
- [Data Type Operations](#data-type-operations)
- [Text Operations](#text-operations)
- [Date Operations](#date-operations)
- [Conditional Logic](#conditional-logic)
- [Table Reshaping](#table-reshaping)

---

## Filtering Operations

### Filter Rows - Single Condition

**Query Folding:** ✅ Preserves

```m
Table.SelectRows(Source, each [Amount] > 1000)
```

**Variations:**
```m
// Equals
Table.SelectRows(Source, each [Status] = "Active")

// Not equals
Table.SelectRows(Source, each [Status] <> "Deleted")

// Contains (breaks folding)
Table.SelectRows(Source, each Text.Contains([Name], "Corp"))

// Null check
Table.SelectRows(Source, each [Amount] <> null)
```

### Filter Rows - Multiple Conditions (AND)

**Query Folding:** ✅ Preserves

```m
Table.SelectRows(Source, each [Amount] > 1000 and [Status] = "Active")
```

### Filter Rows - Multiple Conditions (OR)

**Query Folding:** ✅ Preserves

```m
Table.SelectRows(Source, each [Status] = "Active" or [Status] = "Pending")
```

### Filter Rows - In List

**Query Folding:** ✅ Preserves

```m
Table.SelectRows(Source, each List.Contains({"Active", "Pending", "Review"}, [Status]))
```

### Remove Blank Rows

**Query Folding:** ✅ Preserves

```m
Table.SelectRows(Source, each [CustomerID] <> null and [CustomerID] <> "")
```

---

## Column Operations

### Select Specific Columns

**Query Folding:** ✅ Preserves

```m
Table.SelectColumns(Source, {"CustomerID", "OrderDate", "Amount", "Status"})
```

### Remove Columns

**Query Folding:** ✅ Preserves

```m
Table.RemoveColumns(Source, {"TempField", "InternalID", "Notes"})
```

### Rename Columns

**Query Folding:** ✅ Preserves

```m
Table.RenameColumns(Source, {
    {"old_name", "NewName"},
    {"customer_id", "CustomerID"},
    {"order_dt", "OrderDate"}
})
```

### Reorder Columns

**Query Folding:** ✅ Preserves

```m
Table.ReorderColumns(Source, {"CustomerID", "OrderDate", "Amount", "Status"})
```

### Add Custom Column - Concatenation

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "FullName", each [FirstName] & " " & [LastName], type text)
```

**Alternative (if source supports):**
Create view at source with concatenation.

### Add Custom Column - Conditional

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "Category", each
    if [Amount] > 10000 then "High"
    else if [Amount] > 1000 then "Medium"
    else "Low",
    type text
)
```

### Add Custom Column - Calculation

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "Total", each [Quantity] * [UnitPrice], type number)
```

### Duplicate Column

**Query Folding:** ✅ Preserves

```m
Table.DuplicateColumn(Source, "Amount", "Amount_Original")
```

---

## Table Combination

### Merge (Join) - Inner Join

**Query Folding:** ✅ Preserves (if both sources support folding)

```m
Table.NestedJoin(
    Sales,
    {"CustomerID"},
    Customers,
    {"ID"},
    "CustomerInfo",
    JoinKind.Inner
)
```

Then expand the joined column:
```m
Table.ExpandTableColumn(
    MergedTable,
    "CustomerInfo",
    {"Name", "Region"},
    {"CustomerName", "CustomerRegion"}
)
```

### Merge - Left Outer Join

**Query Folding:** ✅ Preserves (usually)

```m
Table.NestedJoin(
    Sales,
    {"CustomerID"},
    Customers,
    {"ID"},
    "CustomerInfo",
    JoinKind.LeftOuter
)
```

### Merge - Multiple Keys

**Query Folding:** ✅ Preserves

```m
Table.NestedJoin(
    TableA,
    {"CustomerID", "Year"},
    TableB,
    {"ID", "FiscalYear"},
    "Matched",
    JoinKind.Inner
)
```

### Append Tables (Union)

**Query Folding:** ✅ Preserves (if all sources support folding)

```m
Table.Combine({
    Sales2023,
    Sales2024,
    Sales2025
})
```

**Requirements:**
- All tables have same column structure
- All sources support query folding

---

## Aggregation

### Group By - Simple Sum

**Query Folding:** ✅ Preserves

```m
Table.Group(
    Source,
    {"CustomerID"},
    {{"TotalAmount", each List.Sum([Amount]), type number}}
)
```

### Group By - Multiple Aggregations

**Query Folding:** ✅ Preserves

```m
Table.Group(
    Source,
    {"CustomerID", "Year"},
    {
        {"TotalAmount", each List.Sum([Amount]), type number},
        {"OrderCount", each Table.RowCount(_), type number},
        {"AvgAmount", each List.Average([Amount]), type number}
    }
)
```

### Group By - Count Distinct

**Query Folding:** ✅ Preserves

```m
Table.Group(
    Source,
    {"Region"},
    {{"DistinctCustomers", each List.Distinct([CustomerID]), type list}}
)
```

Then count:
```m
Table.TransformColumns(
    Grouped,
    {{"DistinctCustomers", List.Count, type number}}
)
```

### Group By - Custom Aggregation

**Query Folding:** ❌ Breaks

```m
Table.Group(
    Source,
    {"CustomerID"},
    {{"CustomerNames", each Text.Combine([Name], ", "), type text}}
)
```

---

## Data Type Operations

### Change Data Type - Single Column

**Query Folding:** ✅ Preserves

```m
Table.TransformColumnTypes(Source, {{"Amount", type number}})
```

### Change Data Type - Multiple Columns

**Query Folding:** ✅ Preserves

```m
Table.TransformColumnTypes(Source, {
    {"Amount", type number},
    {"OrderDate", type date},
    {"CustomerID", type text},
    {"IsActive", type logical}
})
```

### Replace Null Values

**Query Folding:** ⚠️ May preserve (source-dependent)

```m
Table.ReplaceValue(Source, null, 0, Replacer.ReplaceValue, {"Amount"})
```

### Replace Specific Values

**Query Folding:** ⚠️ May preserve

```m
Table.ReplaceValue(Source, "N/A", null, Replacer.ReplaceValue, {"Status"})
```

---

## Text Operations

### Trim Whitespace

**Query Folding:** ❌ Breaks

```m
Table.TransformColumns(Source, {{"Name", Text.Trim, type text}})
```

### Uppercase

**Query Folding:** ❌ Breaks

```m
Table.TransformColumns(Source, {{"Name", Text.Upper, type text}})
```

### Lowercase

**Query Folding:** ❌ Breaks

```m
Table.TransformColumns(Source, {{"Email", Text.Lower, type text}})
```

### Extract First N Characters

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "FirstInitial", each Text.Start([FirstName], 1), type text)
```

### Split Column by Delimiter

**Query Folding:** ❌ Breaks

```m
Table.SplitColumn(
    Source,
    "FullName",
    Splitter.SplitTextByDelimiter(" ", QuoteStyle.None),
    {"FirstName", "LastName"}
)
```

---

## Date Operations

### Extract Year

**Query Folding:** ❌ Breaks (usually)

```m
Table.AddColumn(Source, "Year", each Date.Year([OrderDate]), type number)
```

**Alternative:** Create view at source with `YEAR(OrderDate)`.

### Extract Month

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "Month", each Date.Month([OrderDate]), type number)
```

### Extract Month Name

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "MonthName", each Date.MonthName([OrderDate]), type text)
```

### Date Difference (Days)

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "DaysSince", each Duration.Days(DateTime.LocalNow() - [OrderDate]), type number)
```

### Filter by Date Range

**Query Folding:** ✅ Preserves

```m
Table.SelectRows(Source, each [OrderDate] >= #date(2024, 1, 1) and [OrderDate] <= #date(2024, 12, 31))
```

---

## Conditional Logic

### If-Then-Else Column

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "PriceCategory", each
    if [Price] > 100 then "Premium"
    else if [Price] > 50 then "Standard"
    else "Budget",
    type text
)
```

### Case/Switch Logic

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "RegionName", each
    if [RegionCode] = "NE" then "Northeast"
    else if [RegionCode] = "SE" then "Southeast"
    else if [RegionCode] = "MW" then "Midwest"
    else if [RegionCode] = "SW" then "Southwest"
    else if [RegionCode] = "W" then "West"
    else "Unknown",
    type text
)
```

---

## Table Reshaping

### Remove Duplicates

**Query Folding:** ✅ Preserves

```m
Table.Distinct(Source, {"CustomerID"})
```

### Pivot Table

**Query Folding:** ❌ Breaks

```m
Table.Pivot(
    Source,
    List.Distinct(Source[Category]),
    "Category",
    "Amount",
    List.Sum
)
```

### Unpivot Columns

**Query Folding:** ❌ Breaks

```m
Table.UnpivotOtherColumns(
    Source,
    {"ID", "Name"},
    "Attribute",
    "Value"
)
```

### Transpose Table

**Query Folding:** ❌ Breaks

```m
Table.Transpose(Source)
```

---

## Special Patterns

### Create Date Table

**Query Folding:** N/A (Generated table)

```m
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2030, 12, 31),
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, NumberOfDays, #duration(1,0,0,0)),
    DateTable = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    ChangedType = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    AddYear = Table.AddColumn(ChangedType, "Year", each Date.Year([Date]), type number),
    AddMonth = Table.AddColumn(AddYear, "Month", each Date.Month([Date]), type number),
    AddMonthName = Table.AddColumn(AddMonth, "MonthName", each Date.MonthName([Date]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each "Q" & Number.ToText(Date.QuarterOfYear([Date])), type text),
    AddDayOfWeek = Table.AddColumn(AddQuarter, "DayOfWeek", each Date.DayOfWeek([Date]), type number),
    AddDayName = Table.AddColumn(AddDayOfWeek, "DayName", each Date.DayOfWeekName([Date]), type text)
in
    AddDayName
```

### Error Handling - Try/Otherwise

**Query Folding:** ❌ Breaks

```m
Table.AddColumn(Source, "SafeDivision", each
    try [Revenue] / [Quantity] otherwise null,
    type number
)
```

### Conditional Column Removal

```m
let
    Source = ...,
    ColumnNames = Table.ColumnNames(Source),
    ColumnsToRemove = List.Select(ColumnNames, each Text.StartsWith(_, "Temp")),
    Result = Table.RemoveColumns(Source, ColumnsToRemove)
in
    Result
```

---

## Transformation Cheat Sheet

| Operation | Query Folding | Complexity | Use When |
|-----------|--------------|------------|----------|
| Filter rows | ✅ | Simple | Always preferred |
| Select columns | ✅ | Simple | Always preferred |
| Rename columns | ✅ | Simple | Always safe |
| Sort | ✅ | Simple | Always safe |
| Remove duplicates | ✅ | Simple | Always safe |
| Join tables | ✅ | Medium | Both sources fold |
| Append tables | ✅ | Medium | All sources fold |
| Group/aggregate | ✅ | Medium | Standard aggregations |
| Add custom column | ❌ | Medium | Accept break for small data |
| Text operations | ❌ | Simple | Accept break or use view |
| Date extractions | ❌ | Simple | Accept break or use view |
| Pivot/unpivot | ❌ | Complex | Small datasets only |
| Custom aggregation | ❌ | Complex | Last resort |

---

## Best Practices

1. **Keep Foldable Steps First**: Minimize data loaded into Power BI
2. **Use Native Functions**: Prefer operations that translate to SQL
3. **Document Complex Logic**: Add comments for non-obvious transformations
4. **Test Performance**: Check refresh times before and after changes
5. **Consider Alternatives**: View at source often better than complex M code
6. **Use Parameters**: Make values configurable for maintainability
7. **Error Handling**: Wrap risky operations in `try...otherwise`
8. **Consistent Naming**: Follow project conventions from pattern analysis
