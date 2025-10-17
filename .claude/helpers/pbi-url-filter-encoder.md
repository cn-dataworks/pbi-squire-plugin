# Power BI URL Filter Encoding Reference

This document provides the encoding logic needed to construct Power BI Service URL filter parameters from filter metadata. This enables automated browser testing by navigating directly to pre-filtered dashboard views, bypassing unreliable DOM-based slicer interactions.

## Overview

Power BI Service supports URL query parameters to apply filters to reports. The syntax is:

```
https://app.powerbi.com/groups/{workspace}/reports/{reportId}/{pageId}?filter={encodedFilterExpression}
```

## Encoding Rules

### Rule 1: Table and Column Name Encoding

Table and column names use a special Power BI encoding format for special characters:

| Character | Encoding | Example |
|-----------|----------|---------|
| Space (` `) | `_x0020_` | `Sales Data` → `Sales_x0020_Data` |
| Underscore (`_`) | `_x005F_` | `SALES_REP` → `SALES_x005F_REP` |

**Important:** Only table and column names use this encoding, NOT filter values.

### Rule 2: Filter Value Escaping

Filter values have different rules:

| Character | Escaping | Example |
|-----------|----------|---------|
| Single Quote (`'`) | Double it (`''`) | `O'Brien` → `O''Brien` |
| Other special chars | No escaping needed | `:`, `/`, `\|\|` are preserved as-is |

### Rule 3: URL Encoding

After constructing the filter string, the entire expression must be URL-encoded using standard `encodeURIComponent()`.

## Encoding Functions (Pseudo-code)

These functions represent the encoding logic. Agents should implement this logic using their available tools and capabilities.

### Function 1: Encode Power BI Names

```typescript
function encodePbiName(name: string): string {
  // First encode underscores (important: do this BEFORE encoding spaces)
  let encoded = name.replace(/_/g, '_x005F_');

  // Then encode spaces
  encoded = encoded.replace(/ /g, '_x0020_');

  return encoded;
}
```

**Examples:**
```typescript
encodePbiName("DIM_SALES_REP")  → "DIM_x005F_SALES_x005F_REP"
encodePbiName("Sales Data")     → "Sales_x0020_Data"
encodePbiName("My_Table Name")  → "My_x005F_Table_x0020_Name"
```

### Function 2: Escape Filter Values

```typescript
function escapeFilterValue(value: string): string {
  // Escape single quotes by doubling them
  return value.replace(/'/g, "''");
}
```

**Examples:**
```typescript
escapeFilterValue("O'Brien")                       → "O''Brien"
escapeFilterValue("Sold/Funded in: Jul-2025")     → "Sold/Funded in: Jul-2025"  // No change
escapeFilterValue("Bob's Store || Main Branch")   → "Bob''s Store || Main Branch"
```

### Function 3: Build Single Filter Expression

```typescript
function buildFilterExpression(
  table: string,
  column: string,
  operator: string,
  value: string
): string {
  const encodedTable = encodePbiName(table);
  const encodedColumn = encodePbiName(column);
  const escapedValue = escapeFilterValue(value);

  return `${encodedTable}/${encodedColumn} ${operator} '${escapedValue}'`;
}
```

**Examples:**
```typescript
buildFilterExpression("DIM_SALES_REP", "NAME_SALES_REP", "eq", "Walton, John")
→ "DIM_x005F_SALES_x005F_REP/NAME_x005F_SALES_x005F_REP eq 'Walton, John'"

buildFilterExpression("DIM_DATE", "COMM_FUNDED_PAID_SNAPSHOT_DISPLAY", "eq", "Sold/Funded in: Jul-2025 || Payroll in: Aug-2025")
→ "DIM_x005F_DATE/COMM_x005F_FUNDED_x005F_PAID_x005F_SNAPSHOT_x005F_DISPLAY eq 'Sold/Funded in: Jul-2025 || Payroll in: Aug-2025'"
```

### Function 4: Construct Filtered URL

```typescript
function constructFilteredUrl(
  baseUrl: string,
  filters: Array<{table: string, column: string, operator: string, value: string}>
): string {
  // Remove any existing query parameters from base URL
  const cleanBaseUrl = baseUrl.split('?')[0];

  // Build individual filter expressions
  const filterExpressions = filters.map(f =>
    buildFilterExpression(f.table, f.column, f.operator, f.value)
  );

  // Join multiple filters with ' and '
  const combinedFilter = filterExpressions.join(' and ');

  // URL-encode the entire filter string
  const encodedFilter = encodeURIComponent(combinedFilter);

  // Construct final URL
  return `${cleanBaseUrl}?filter=${encodedFilter}`;
}
```

**Example:**
```typescript
const baseUrl = "https://app.powerbi.com/groups/me/reports/59136055-6fca-43a5-877b-b3b1419f93b8/5f17bcbf5472817e1a1c?experience=power-bi";

const filters = [
  {
    table: "DIM_SALES_REP",
    column: "NAME_SALES_REP",
    operator: "eq",
    value: "Walton, John"
  },
  {
    table: "DIM_DATE",
    column: "COMM_FUNDED_PAID_SNAPSHOT_DISPLAY",
    operator: "eq",
    value: "Sold/Funded in: Jul-2025 || Payroll in: Aug-2025"
  }
];

constructFilteredUrl(baseUrl, filters)
→ "https://app.powerbi.com/groups/me/reports/59136055-6fca-43a5-877b-b3b1419f93b8/5f17bcbf5472817e1a1c?filter=DIM_x005F_SALES_x005F_REP%2FNAME_x005F_SALES_x005F_REP%20eq%20%27Walton%2C%20John%27%20and%20DIM_x005F_DATE%2FCOMM_x005F_FUNDED_x005F_PAID_x005F_SNAPSHOT_x005F_DISPLAY%20eq%20%27Sold%2FFunded%20in%3A%20Jul-2025%20%7C%7C%20Payroll%20in%3A%20Aug-2025%27"
```

## Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `Table/Column eq 'Value'` |
| `ne` | Not equals | `Table/Column ne 'Value'` |
| `lt` | Less than | `Table/Column lt 100` |
| `le` | Less than or equal | `Table/Column le 100` |
| `gt` | Greater than | `Table/Column gt 100` |
| `ge` | Greater than or equal | `Table/Column ge 100` |
| `in` | In (multiple values) | `Table/Column in ('A', 'B', 'C')` |

## Special Cases

### Multiple Values (IN operator)

```typescript
// For filtering on multiple values, use the 'in' operator
buildFilterExpression("Store", "Territory", "in", "('NC', 'TN')")
→ "Store/Territory in ('NC', 'TN')"
```

**Note:** When using `in` operator, the value should already be formatted as `('value1', 'value2', ...)`.

### Numeric Values

```typescript
// Numbers don't require quotes
buildFilterExpression("Sales", "Amount", "gt", "1000")
→ "Sales/Amount gt 1000"
```

### Date Values

```typescript
// Dates can use OData V3 or V4 format
buildFilterExpression("Orders", "OrderDate", "ge", "datetime'2025-01-01T00:00:00'")
→ "Orders/OrderDate ge datetime'2025-01-01T00:00:00'"

// Or simpler format (OData V4)
buildFilterExpression("Orders", "OrderDate", "ge", "2025-01-01")
→ "Orders/OrderDate ge 2025-01-01"
```

## Limitations

1. **Maximum 10 AND Conditions:** You can combine at most 10 filter expressions with `and`
2. **Not Supported in All Scenarios:**
   - "Publish to web" embedded reports
   - SharePoint Online report web parts
3. **Case Sensitivity:** Table and column names are case-sensitive; values are not

## Common Pitfalls

### ❌ WRONG: Encoding special characters in values
```typescript
// Don't use Power BI encoding for values - this is WRONG
buildFilterExpression("DIM_DATE", "MONTH_YEAR", "eq", "Jul_x0020_2025")
```

### ✅ CORRECT: Preserve special characters in values
```typescript
// Values keep their original characters - this is CORRECT
buildFilterExpression("DIM_DATE", "MONTH_YEAR", "eq", "Jul 2025")
```

### ❌ WRONG: Not escaping single quotes
```typescript
buildFilterExpression("Customer", "Name", "eq", "O'Brien")
→ Syntax error due to unescaped quote
```

### ✅ CORRECT: Escaping single quotes
```typescript
buildFilterExpression("Customer", "Name", "eq", "O''Brien")
→ "Customer/Name eq 'O''Brien'"
```

### ❌ WRONG: Encoding spaces before underscores
```typescript
// This creates incorrect encoding
let name = "MY_TABLE NAME";
name = name.replace(/ /g, '_x0020_');  // "MY_TABLE_x0020_NAME"
name = name.replace(/_/g, '_x005F_');  // "MY_x005F_TABLE_x005F_x0020_x005F_NAME" ❌
```

### ✅ CORRECT: Encoding underscores before spaces
```typescript
// This creates correct encoding
let name = "MY_TABLE NAME";
name = name.replace(/_/g, '_x005F_');  // "MY_x005F_TABLE NAME"
name = name.replace(/ /g, '_x0020_');  // "MY_x005F_TABLE_x0020_NAME" ✅
```

## Implementation Guide for Agents

### For power-bi-verification Agent

When creating test cases with filter requirements:

1. Read the `.tmdl` files to discover table and column names
2. Create a `Filter Metadata` section in YAML format:
   ```yaml
   filters:
     - table: DIM_SALES_REP
       column: NAME_SALES_REP
       operator: eq
       value: "Walton, John"
   ```
3. Include this metadata in Section 3 test case documentation

### For powerbi-playwright-tester Agent

When executing tests with filter metadata:

1. Parse the YAML `Filter Metadata` section
2. Apply the encoding functions to build the filter URL
3. Navigate to the constructed URL
4. Wait for the dashboard to load (pre-filtered)
5. Execute test validations

## Testing Your Encoding

To verify your encoding is correct:

1. Manually construct a filter URL using the functions above
2. Paste it into a browser address bar
3. Verify the Power BI report loads with the correct filters applied
4. If filters don't apply correctly, check:
   - Table/column names match exactly (case-sensitive)
   - Underscores are encoded as `_x005F_` in names
   - Spaces are encoded as `_x0020_` in names
   - Single quotes are doubled in values
   - The full filter string is URL-encoded with `encodeURIComponent()`

## References

- Power BI Service URL Filter Documentation: https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-url-filters
- OData V4 Filter Syntax: https://www.odata.org/documentation/
- Unicode Character Encoding Table: https://www.unicode.org/charts/

---

**Last Updated:** 2025-10-05
**Version:** 1.0
