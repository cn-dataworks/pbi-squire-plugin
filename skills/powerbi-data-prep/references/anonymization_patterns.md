# M Code Anonymization Patterns

Reusable templates for masking sensitive data in Power BI M code. Each pattern includes conditional logic to toggle between real and anonymized data using a `DataMode` parameter.

## DataMode Parameter Setup

Before using these patterns, create a `DataMode` parameter in your model:

```m
// Named Expression: DataMode
"Real" meta [
    IsParameterQuery = true,
    Type = "Text",
    IsParameterQueryRequired = true,
    AllowedValues = {"Real", "Anonymized"}
]
```

**Default value**: "Real" (shows actual data)
**To anonymize**: Change to "Anonymized" and refresh

---

## Pattern Categories

### 1. Names - Sequential Numbering

Replaces names with "Customer 1", "Customer 2", etc.

**Use for**: CustomerName, FirstName, LastName, EmployeeName, ContactName

```m
let
    Source = {{PREVIOUS_STEP}},

    // Add index for sequential numbering
    IndexedTable = Table.AddIndexColumn(Source, "_MaskIndex", 1, 1, Int64.Type),

    // Conditional masking based on DataMode parameter
    MaskedColumn = Table.TransformColumns(IndexedTable, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                "{{PREFIX}} " & Text.From([_MaskIndex])
            else
                [{{COLUMN_NAME}}],
            type text
        }
    }),

    // Remove index column
    Result = Table.RemoveColumns(MaskedColumn, {"_MaskIndex"})
in
    Result
```

**Variables**:
- `{{COLUMN_NAME}}`: The column to mask (e.g., CustomerName)
- `{{PREFIX}}`: Prefix for masked values (e.g., "Customer", "Employee", "Person")

**Query Folding**: BREAKS (uses Text operations)

---

### 2. Email - Fake Domain

Replaces emails with user123@example.com format.

**Use for**: Email, EmailAddress, ContactEmail, UserEmail

```m
let
    Source = {{PREVIOUS_STEP}},

    // Add index for unique emails
    IndexedTable = Table.AddIndexColumn(Source, "_MaskIndex", 1, 1, Int64.Type),

    // Conditional masking
    MaskedColumn = Table.TransformColumns(IndexedTable, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                "user" & Text.From([_MaskIndex]) & "@example.com"
            else
                [{{COLUMN_NAME}}],
            type text
        }
    }),

    // Remove index column
    Result = Table.RemoveColumns(MaskedColumn, {"_MaskIndex"})
in
    Result
```

**Query Folding**: BREAKS

---

### 3. Identifiers - Partial Mask

Shows only last 4 characters (XXX-XX-1234 format).

**Use for**: SSN, TaxID, AccountNumber, CardNumber, LicenseNumber

```m
let
    Source = {{PREVIOUS_STEP}},

    // Conditional partial masking
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                "XXX-XX-" & Text.End(Text.From([{{COLUMN_NAME}}]), 4)
            else
                [{{COLUMN_NAME}}],
            type text
        }
    })
in
    MaskedColumn
```

**For account/card numbers** (longer format):
```m
{"{{COLUMN_NAME}}", each
    if #"DataMode" = "Anonymized" then
        Text.Repeat("*", Text.Length(Text.From([{{COLUMN_NAME}}])) - 4) &
        Text.End(Text.From([{{COLUMN_NAME}}]), 4)
    else
        [{{COLUMN_NAME}}],
    type text
}
```

**Query Folding**: BREAKS

---

### 4. Phone Numbers - Fake Prefix

Replaces with (555) 555-XXXX format (keeps last 4 for reference).

**Use for**: Phone, PhoneNumber, Mobile, CellPhone, HomePhone, WorkPhone

```m
let
    Source = {{PREVIOUS_STEP}},

    // Conditional phone masking
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                "(555) 555-" & Text.End(Text.Replace(Text.From([{{COLUMN_NAME}}]), "-", ""), 4)
            else
                [{{COLUMN_NAME}}],
            type text
        }
    })
in
    MaskedColumn
```

**Alternative (completely random)**:
```m
{"{{COLUMN_NAME}}", each
    if #"DataMode" = "Anonymized" then
        "(555) 555-" & Text.From(Number.RoundDown(Number.Random() * 9000 + 1000))
    else
        [{{COLUMN_NAME}}],
    type text
}
```

**Query Folding**: BREAKS

---

### 5. Addresses - Generic Format

Replaces with generic "123 Main St" format.

**Use for**: Address, StreetAddress, BillingAddress, ShippingAddress

```m
let
    Source = {{PREVIOUS_STEP}},

    // Add index for unique addresses
    IndexedTable = Table.AddIndexColumn(Source, "_MaskIndex", 1, 1, Int64.Type),

    // Conditional address masking
    MaskedColumn = Table.TransformColumns(IndexedTable, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                Text.From([_MaskIndex]) & " Main Street, Anytown, ST 00000"
            else
                [{{COLUMN_NAME}}],
            type text
        }
    }),

    // Remove index column
    Result = Table.RemoveColumns(MaskedColumn, {"_MaskIndex"})
in
    Result
```

**For individual address components**:
```m
// City
{"City", each if #"DataMode" = "Anonymized" then "Anytown" else [City], type text}

// State
{"State", each if #"DataMode" = "Anonymized" then "ST" else [State], type text}

// Zip Code
{"ZipCode", each if #"DataMode" = "Anonymized" then "00000" else [ZipCode], type text}
```

**Query Folding**: BREAKS

---

### 6. Numerical Data - Strategy Selection Guide

Before anonymizing numerical columns, answer these questions to select the best strategy:

#### Decision Questions

| Question | If Yes | If No |
|----------|--------|-------|
| Are values typically small integers (0-20)? | Use **Hybrid** or **Random Replacement** | Scale Factor may work |
| Must values stay non-negative? | Add floor: `Number.Max(0, ...)` | Allow negative results |
| Do column totals need to add up? | Apply same factor per row | Independent randomization OK |
| Is the exact distribution shape critical? | Use **Scale Factor** | Hybrid or Random OK |
| Are there many zero values? | Use **Hybrid** (zeros get variation) | Any strategy works |

---

#### Strategy A: Hybrid (Percentage + Minimum Floor) — RECOMMENDED FOR INTEGERS

Best for: Mixed-scale data, small integers, counts, quantities

Uses whichever is larger: percentage-based noise OR a minimum floor. This ensures meaningful variation for small numbers while scaling proportionally for large ones.

**Use for**: Count, Quantity, Units, Score, Rating, Age, YearsExperience, SmallAmounts

```m
let
    Source = {{PREVIOUS_STEP}},

    // Hybrid: Percentage (25%) with Minimum Floor (2)
    // Ensures small values get meaningful variation
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                let
                    PercentNoise = Number.Abs(_) * {{PERCENTAGE}},
                    MinFloor = {{MIN_FLOOR}},
                    NoiseRange = Number.Max(MinFloor, PercentNoise),
                    RandomNoise = (Number.Random() * 2 - 1) * NoiseRange,
                    Result = Number.Max(0, Number.RoundDown(_ + RandomNoise))
                in
                    Result
            else
                _,
            Int64.Type
        }
    })
in
    MaskedColumn
```

**Variables**:
- `{{PERCENTAGE}}`: Noise percentage for large values (default: 0.25 = 25%)
- `{{MIN_FLOOR}}`: Minimum noise amount for small values (default: 2)

**Example behavior with 25% / floor 2**:

| Original | Percentage Noise | Min Floor | Actual Noise | Possible Range |
|----------|------------------|-----------|--------------|----------------|
| 1000 | 250 | 2 | **250** | 750–1250 |
| 100 | 25 | 2 | **25** | 75–125 |
| 10 | 2.5 | 2 | **2.5** | 7–13 |
| 4 | 1 | 2 | **2** | 2–6 |
| 1 | 0.25 | 2 | **2** | 0–3 |
| 0 | 0 | 2 | **2** | 0–2 |

**For decimal results** (e.g., ratings 1.0-5.0):
```m
{"{{COLUMN_NAME}}", each
    if #"DataMode" = "Anonymized" then
        let
            PercentNoise = Number.Abs(_) * {{PERCENTAGE}},
            MinFloor = {{MIN_FLOOR}},
            NoiseRange = Number.Max(MinFloor, PercentNoise),
            RandomNoise = (Number.Random() * 2 - 1) * NoiseRange,
            Result = Number.Max(0, Number.Round(_ + RandomNoise, 2))
        in
            Result
    else
        _,
    type number
}
```

**Query Folding**: BREAKS

---

#### Strategy B: Scale Factor — RECOMMENDED FOR LARGE FINANCIAL VALUES

Best for: Large monetary amounts where distribution shape matters

Multiplies by random factor to preserve relative differences. Works well when values are consistently large (>100).

**Use for**: Salary, Revenue, Profit, LargeAmounts, Balance, Payment (when typically >$100)

```m
let
    Source = {{PREVIOUS_STEP}},

    // Scale factor: Multiplies by 0.8x to 1.2x
    // Preserves distribution shape and relative differences
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                Number.Round(_ * (0.8 + Number.Random() * 0.4), 2)
            else
                _,
            type number
        }
    })
in
    MaskedColumn
```

**For integer amounts** (no decimals):
```m
{"{{COLUMN_NAME}}", each
    if #"DataMode" = "Anonymized" then
        Number.RoundDown(_ * (0.8 + Number.Random() * 0.4))
    else
        _,
    Int64.Type
}
```

**Limitation**: For small values (0-20), this produces minimal variation:
- Value of 5 → range 4-6 (often unchanged)
- Value of 1 → range 0-1 (binary outcome)
- Value of 0 → always 0

Use **Hybrid** strategy instead for small integers.

**Query Folding**: BREAKS

---

#### Strategy C: Random Replacement — FOR COMPLETE OBFUSCATION

Best for: When original values should be completely hidden, not just obscured

Replaces with random values within a specified range. No correlation to original.

**Use for**: Sensitive counts, security-critical data, test data generation

```m
let
    Source = {{PREVIOUS_STEP}},

    // Random replacement: Generates random value in range
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                Number.RoundDown(Number.Random() * ({{MAX_VALUE}} - {{MIN_VALUE}}) + {{MIN_VALUE}})
            else
                _,
            Int64.Type
        }
    })
in
    MaskedColumn
```

**Variables**:
- `{{MIN_VALUE}}`: Minimum of random range (e.g., 0)
- `{{MAX_VALUE}}`: Maximum of random range (e.g., 100)

**Query Folding**: BREAKS

---

#### Strategy D: Bucketing — FOR CATEGORICAL ANALYSIS

Best for: When exact values don't matter, only ranges

Converts numbers to range labels. Useful for demographics, age groups, etc.

**Use for**: Age, Income brackets, Score ranges

```m
let
    Source = {{PREVIOUS_STEP}},

    // Bucketing: Convert to range labels
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                if _ <= 20 then "0-20"
                else if _ <= 50 then "21-50"
                else if _ <= 100 then "51-100"
                else "100+"
            else
                Text.From(_),
            type text
        }
    })
in
    MaskedColumn
```

**Note**: Changes column type from number to text. DAX measures using this column will need adjustment.

**Query Folding**: BREAKS

---

#### Quick Reference: Which Strategy to Use

| Data Type | Typical Range | Recommended Strategy |
|-----------|---------------|---------------------|
| Unit counts | 0-20 | **Hybrid** (floor=2) |
| Quantities | 0-100 | **Hybrid** (floor=2-3) |
| Scores/ratings | 1-10 | **Hybrid** (floor=1) |
| Age | 0-120 | **Hybrid** (floor=3) |
| Salary | 30K-500K | **Scale Factor** |
| Revenue | 1K-10M | **Scale Factor** |
| Small prices | $1-$50 | **Hybrid** (floor=2) |
| Large prices | $100-$10K | **Scale Factor** |
| Sensitive counts | any | **Random Replacement** |
| Demographics | varies | **Bucketing** |

**Note**: Number.Random() generates different values on each refresh for all strategies.

---

### 7. Dates - Offset Shift

Shifts dates by random number of days (+/- 30).

**Use for**: DateOfBirth, DOB, HireDate, StartDate, EndDate

```m
let
    Source = {{PREVIOUS_STEP}},

    // Conditional date offset
    // Shifts by -30 to +30 days randomly
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                Date.AddDays([{{COLUMN_NAME}}], Number.RoundDown(Number.Random() * 60) - 30)
            else
                [{{COLUMN_NAME}}],
            type date
        }
    })
in
    MaskedColumn
```

**For datetime columns**:
```m
{"{{COLUMN_NAME}}", each
    if #"DataMode" = "Anonymized" then
        DateTime.From(Date.AddDays(DateTime.Date([{{COLUMN_NAME}}]),
                      Number.RoundDown(Number.Random() * 60) - 30))
    else
        [{{COLUMN_NAME}}],
    type datetime
}
```

**Query Folding**: BREAKS

---

### 8. Free Text - Placeholder

Replaces with placeholder text.

**Use for**: Notes, Comments, Description, Feedback, Message, Remarks

```m
let
    Source = {{PREVIOUS_STEP}},

    // Conditional text replacement
    MaskedColumn = Table.TransformColumns(Source, {
        {"{{COLUMN_NAME}}", each
            if #"DataMode" = "Anonymized" then
                "[Content redacted for privacy]"
            else
                [{{COLUMN_NAME}}],
            type text
        }
    })
in
    MaskedColumn
```

**Alternative (preserves length indication)**:
```m
{"{{COLUMN_NAME}}", each
    if #"DataMode" = "Anonymized" then
        "[Redacted - " & Text.From(Text.Length(Text.From([{{COLUMN_NAME}}]))) & " chars]"
    else
        [{{COLUMN_NAME}}],
    type text
}
```

**Query Folding**: BREAKS

---

## Complete Table Example

Masking multiple columns in one transformation:

```m
let
    Source = Sql.Database("server", "database"),
    RawData = Source{[Schema="dbo",Item="Customers"]}[Data],

    // Add index for sequential numbering
    IndexedData = Table.AddIndexColumn(RawData, "_MaskIndex", 1, 1, Int64.Type),

    // Apply all masking in one step
    MaskedData = if #"DataMode" = "Anonymized" then
        Table.TransformColumns(IndexedData, {
            {"CustomerName", each "Customer " & Text.From([_MaskIndex]), type text},
            {"Email", each "user" & Text.From([_MaskIndex]) & "@example.com", type text},
            {"Phone", each "(555) 555-" & Text.End(Text.Replace(Text.From([Phone]), "-", ""), 4), type text},
            {"SSN", each "XXX-XX-" & Text.End(Text.From([SSN]), 4), type text},
            {"Salary", each Number.Round([Salary] * (0.8 + Number.Random() * 0.4), 2), type number}
        })
    else
        IndexedData,

    // Clean up
    CleanedData = Table.RemoveColumns(MaskedData, {"_MaskIndex"}),

    // Final type casting
    TypedData = Table.TransformColumnTypes(CleanedData, {
        {"CustomerName", type text},
        {"Email", type text},
        {"Phone", type text},
        {"SSN", type text},
        {"Salary", Currency.Type}
    })
in
    TypedData
```

---

## Usage Notes

### Query Folding Impact

All masking operations **break query folding** because they use:
- Text operations (Text.From, Text.End, Text.Replace)
- Random number generation (Number.Random)
- Date calculations (Date.AddDays)

**Recommendation**: Apply filters and column selection BEFORE masking steps to minimize data loaded.

### Consistent Masking

If you need the same masked value for the same original value (e.g., for joins):
- Use index-based masking instead of Number.Random()
- Consider hashing: `Text.From(Number.Mod(Number.FromText(Text.From([Value])), 10000))`

### Schema Preservation

All patterns preserve:
- Column names
- Data types
- Column order

This ensures DAX measures and relationships continue to work.

### Switching Modes

To switch between Real and Anonymized:
1. Open Power BI Desktop
2. Go to Transform Data > Parameters
3. Change DataMode value
4. Click Close & Apply
5. Data refreshes with new mode
