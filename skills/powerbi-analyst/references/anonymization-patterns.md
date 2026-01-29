# Anonymization Patterns Reference

Reference for detecting sensitive columns and generating M code masking transformations.
Used by the `powerbi-anonymization-setup` agent for Claude-native anonymization workflow.

---

## Sensitive Column Detection Patterns

Column names are matched case-insensitively against these regex patterns.
Confidence levels indicate likelihood of containing sensitive data.

### HIGH Confidence - Likely Sensitive

| Category | Pattern | Example Matches | Suggested Masking |
|----------|---------|-----------------|-------------------|
| **Names** | `^(customer\|client\|employee\|user\|person\|contact\|member)_?name$` | CustomerName, client_name | sequential_numbering |
| **Names** | `^(first\|last\|full\|given\|family\|middle)_?name$` | FirstName, last_name | sequential_numbering |
| **Emails** | `^e?mail(_?address)?$` | Email, email_address | fake_domain |
| **Emails** | `^(customer\|client\|user\|contact)_?e?mail$` | CustomerEmail | fake_domain |
| **SSN/ID** | `^ssn$` | SSN | partial_mask |
| **SSN/ID** | `^social_?security(_?number)?$` | SocialSecurityNumber | partial_mask |
| **SSN/ID** | `^tax_?id$` | TaxID | partial_mask |
| **SSN/ID** | `^national_?id$` | NationalID | partial_mask |
| **SSN/ID** | `^(driver_?)?license(_?number)?$` | DriverLicense | partial_mask |
| **SSN/ID** | `^passport(_?number)?$` | PassportNumber | partial_mask |
| **Phone** | `^phone(_?number)?$` | Phone, PhoneNumber | fake_prefix |
| **Phone** | `^(mobile\|cell\|home\|work\|office)_?(phone\|number)?$` | MobilePhone | fake_prefix |
| **Phone** | `^tel(ephone)?$` | Telephone | fake_prefix |
| **Address** | `^(street\|home\|mailing\|billing\|shipping)_?address$` | StreetAddress | generic_format |
| **Address** | `^address(_?line)?[_\d]*$` | Address, Address1 | generic_format |
| **Financial** | `^(salary\|wage\|income\|compensation)$` | Salary | scale_factor |
| **Financial** | `^(account\|card)_?number$` | AccountNumber | partial_mask |
| **Financial** | `^(credit\|debit)_?card$` | CreditCard | partial_mask |
| **Financial** | `^bank_?account$` | BankAccount | partial_mask |
| **Dates** | `^(date_?of_?birth\|dob\|birth_?date)$` | DateOfBirth, DOB | date_offset |

### MEDIUM Confidence - Possibly Sensitive

| Category | Pattern | Example Matches | Suggested Masking |
|----------|---------|-----------------|-------------------|
| **Names** | `^name$` | Name | sequential_numbering |
| **Names** | `^(customer\|client\|employee\|user\|person)$` | Customer | sequential_numbering |
| **Emails** | `email` (anywhere) | PrimaryEmail, WorkEmail | fake_domain |
| **Phone** | `^fax$` | Fax | fake_prefix |
| **Address** | `^(city\|town\|municipality)$` | City | generic_format |
| **Address** | `^(state\|province\|region)$` | State | generic_format |
| **Address** | `^(zip\|postal)_?(code)?$` | ZipCode | generic_format |
| **Financial** | `^(price\|cost\|amount\|total\|balance\|payment)$` | Amount | scale_factor |
| **Financial** | `^(revenue\|profit\|margin)$` | Revenue | scale_factor |
| **Dates** | `^(hire\|start\|end\|termination)_?date$` | HireDate | date_offset |

### LOW Confidence - Review Recommended

| Category | Pattern | Example Matches | Suggested Masking |
|----------|---------|-----------------|-------------------|
| **Address** | `^country$` | Country | generic_format |
| **Freetext** | `^(notes?\|comments?\|description\|remarks?)$` | Notes | placeholder_text |
| **Freetext** | `^(feedback\|review\|message)$` | Feedback | placeholder_text |

---

## Masking Strategy Descriptions

| Strategy | Description | Preserves |
|----------|-------------|-----------|
| `sequential_numbering` | Replace with "Customer 1", "Customer 2", etc. | Uniqueness |
| `fake_domain` | Replace with user123@example.com format | Format |
| `partial_mask` | Show only last 4 characters (XXX-XX-1234) | Partial value |
| `fake_prefix` | Replace with (555) 555-XXXX format | Format |
| `generic_format` | Replace with "123 Main St, Anytown, ST 00000" | Structure |
| `scale_factor` | Multiply by random factor (0.8-1.2) | Distribution, trends |
| `date_offset` | Shift by random number of days (+/- 30) | Sequence, patterns |
| `placeholder_text` | Replace with "[Content redacted for privacy]" | Nothing (full redaction) |

---

## M Code Templates

These templates generate conditional masking code that respects the `DataMode` parameter.
When `DataMode = "Anonymized"`, data is masked. When `DataMode = "Real"`, original data is shown.

### DataMode Parameter Expression

Create this as a named expression in the semantic model:

```m
"Real" meta [
    IsParameterQuery = true,
    Type = "Text",
    IsParameterQueryRequired = true,
    AllowedValues = {"Real", "Anonymized"}
]
```

**TMDL location:** `.SemanticModel/definition/expressions.tmdl`

**TMDL syntax:**
```
expression DataMode =
    "Real"
    meta
    [
        IsParameterQuery = true,
        Type = "Text",
        IsParameterQueryRequired = true,
        AllowedValues = {"Real", "Anonymized"}
    ]
```

---

### sequential_numbering

**Use for:** Names (customer, employee, user names)

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        "{PREFIX} " & Text.From([_MaskIndex])
    else
        [{COLUMN}],
    type text
}
```

**Prefix mapping:**
| Column pattern | Prefix |
|----------------|--------|
| customername, customer | Customer |
| clientname, client | Client |
| employeename, employee | Employee |
| username, user | User |
| personname, person | Person |
| contactname, contact | Contact |
| membername, member | Member |
| firstname, lastname, fullname | Person |
| name (generic) | Entity |

**Requires index:** Yes (add `_MaskIndex` column)

---

### fake_domain

**Use for:** Email addresses

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        "user" & Text.From([_MaskIndex]) & "@example.com"
    else
        [{COLUMN}],
    type text
}
```

**Requires index:** Yes

---

### partial_mask

**Use for:** SSN, Tax ID, Account numbers, Card numbers

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        "XXX-XX-" & Text.End(Text.From([{COLUMN}]), 4)
    else
        [{COLUMN}],
    type text
}
```

**Requires index:** No

---

### fake_prefix

**Use for:** Phone numbers, Fax numbers

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        "(555) 555-" & Text.End(Text.Replace(Text.From([{COLUMN}]), "-", ""), 4)
    else
        [{COLUMN}],
    type text
}
```

**Requires index:** No

---

### generic_format

**Use for:** Addresses, Cities, States, Zip codes

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        Text.From([_MaskIndex]) & " Main Street, Anytown, ST 00000"
    else
        [{COLUMN}],
    type text
}
```

**Requires index:** Yes

---

### scale_factor

**Use for:** Financial amounts (salary, prices, revenue)

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        Number.Round([{COLUMN}] * (0.8 + Number.Random() * 0.4), 2)
    else
        [{COLUMN}],
    type number
}
```

**Requires index:** No

**Note:** Multiplies by random factor between 0.8 and 1.2, preserving relative distribution.

---

### date_offset

**Use for:** Birth dates, Hire dates, other sensitive dates

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        Date.AddDays([{COLUMN}], Number.RoundDown(Number.Random() * 60) - 30)
    else
        [{COLUMN}],
    type date
}
```

**Requires index:** No

**Note:** Shifts dates by random offset between -30 and +30 days.

---

### placeholder_text

**Use for:** Free-text fields (notes, comments, descriptions)

**Template:**
```m
{"{COLUMN}", each
    if #"DataMode" = "Anonymized" then
        "[Content redacted for privacy]"
    else
        [{COLUMN}],
    type text
}
```

**Requires index:** No

---

## Complete Transformation Pattern

When a table has sensitive columns, wrap the transformations like this:

### With Index (for sequential numbering, fake_domain, generic_format)

```m
let
    Source = {PREVIOUS_STEP},

    // Add index for sequential numbering
    IndexedData = Table.AddIndexColumn(Source, "_MaskIndex", 1, 1, Int64.Type),

    // Apply conditional masking based on DataMode parameter
    MaskedData = Table.TransformColumns(IndexedData, {
        // ... column transformations here ...
    }),

    // Remove index column
    Result = Table.RemoveColumns(MaskedData, {"_MaskIndex"})
in
    Result
```

### Without Index (for partial_mask, scale_factor, date_offset, placeholder_text)

```m
let
    Source = {PREVIOUS_STEP},

    // Apply conditional masking based on DataMode parameter
    MaskedData = Table.TransformColumns(Source, {
        // ... column transformations here ...
    })
in
    MaskedData
```

---

## Configuration File Format

Store anonymization configuration in `{PROJECT}/.anonymization/config.json`:

```json
{
  "status": "configured",
  "setup_timestamp": "2024-01-15T10:30:00Z",
  "datamode_parameter": "DataMode",
  "tables": [
    {
      "name": "Customers",
      "columns_masked": ["CustomerName", "Email", "Phone"],
      "masking_strategies": {
        "CustomerName": "sequential_numbering",
        "Email": "fake_domain",
        "Phone": "fake_prefix"
      }
    }
  ]
}
```

---

## Workflow Summary

1. **Detect** - Scan TMDL files for table/column definitions, match against patterns
2. **Confirm** - Present findings to user grouped by confidence, get confirmation
3. **Generate** - Create DataMode parameter and M code transformations
4. **Apply** - Edit partition TMDL files to add masking logic
5. **Configure** - Write config.json and update `.claude/powerbi-analyst.json`
6. **Validate** - Test by toggling DataMode parameter

---

## See Also

- `agents/core/powerbi-anonymization-setup.md` - Agent that implements this workflow
- `SKILL.md` → Step 2: Anonymization Check - Pre-workflow check
- `tools/core/sensitive_column_detector.py` - Python equivalent (Pro only)
- `tools/core/anonymization_generator.py` - Python equivalent (Pro only)
