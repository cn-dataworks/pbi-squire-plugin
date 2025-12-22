# Getting Started with Power BI Analyst

Welcome! This guide helps you get productive with the Power BI Analyst skill in just a few minutes.

---

## What Can This Skill Do?

The Power BI Analyst skill helps you work with Power BI projects by:

- **Diagnosing issues** - Find and fix problems in your measures, calculations, or data model
- **Creating new artifacts** - Build measures, calculated columns, tables, and visuals
- **Analyzing dashboards** - Understand what existing dashboards do and how they work
- **Making changes safely** - All edits create versioned backups first
- **Merging projects** - Combine changes from different project versions

---

## Before You Start

### Requirements

1. **Power BI Project in PBIP format**
   - Your project should have `.SemanticModel/` and `.Report/` folders
   - Not a `.pbix` file (single binary file)

2. **For best results: Power BI Desktop running**
   - Enables live validation and data sampling
   - Without Desktop, the skill works but with limited validation

### Quick Check

Your project should look like this:
```
MyProject/
├── MyProject.pbip
├── MyProject.SemanticModel/
│   └── definition/
│       ├── tables/
│       └── relationships/
└── MyProject.Report/
```

---

## Data Privacy & Masking Guide

### What Claude Can See

When using this skill:

**In File-Only Mode (No Desktop):**
- Table and column names
- Measure formulas (DAX code)
- Report structure and visual configurations
- No actual data values

**In Desktop Mode (MCP connected):**
- Everything above, PLUS:
- Sample data rows when validating queries
- Actual values when testing measures
- Data previews when analyzing the model

### Working with Sensitive Data

**If your project contains sensitive data** (PII, financial records, healthcare, confidential business data), you have several options:

---

### Option 1: Use File-Only Mode

The simplest approach - no data exposure at all.

**How to use:**
1. Close Power BI Desktop
2. Tell Claude: "Work in file-only mode - this project has sensitive data"

**Limitations:**
- Syntax-only validation (can't catch semantic errors)
- No data sampling to verify calculations
- Suitable for reviewing/editing formulas, not for data analysis

---

### Option 2: Create a Masked Copy (Recommended for Full Validation)

Create a version of your project with fake data that preserves structure and relationships.

**Step-by-Step Guide:**

#### Step 1: Copy Your Project
```
1. Copy entire project folder
2. Rename: MyProject → MyProject_Masked
3. Open the masked copy in Power BI Desktop
```

#### Step 2: Add Masking Transformations

In Power Query Editor (Home → Transform Data), add masking steps:

**For Customer Names:**
```powerquery
// Replace names with "Customer 1", "Customer 2", etc.
= Table.AddIndexColumn(#"Previous Step", "MaskIndex", 1, 1),
= Table.AddColumn(#"Added Index", "CustomerName_Masked",
    each "Customer " & Text.From([MaskIndex])),
= Table.RemoveColumns(#"Added Column", {"CustomerName", "MaskIndex"}),
= Table.RenameColumns(#"Removed Columns", {{"CustomerName_Masked", "CustomerName"}})
```

**For Email Addresses:**
```powerquery
// Replace emails with fake format
= Table.TransformColumns(#"Previous Step", {
    {"Email", each "user" & Text.From(Number.Random() * 10000) & "@example.com"}
})
```

**For Social Security Numbers / IDs:**
```powerquery
// Replace with random masked format
= Table.TransformColumns(#"Previous Step", {
    {"SSN", each "XXX-XX-" & Text.From(Number.RoundDown(Number.Random() * 9000 + 1000))}
})
```

**For Phone Numbers:**
```powerquery
// Replace with fake numbers
= Table.TransformColumns(#"Previous Step", {
    {"Phone", each "(555) 555-" & Text.From(Number.RoundDown(Number.Random() * 9000 + 1000))}
})
```

**For Financial Amounts (preserve distribution):**
```powerquery
// Multiply by random factor to obscure real values while keeping relative scale
= Table.TransformColumns(#"Previous Step", {
    {"Amount", each [Amount] * (0.8 + Number.Random() * 0.4)}
})
```

**For Addresses:**
```powerquery
// Replace with generic addresses
= Table.AddIndexColumn(#"Previous Step", "MaskIndex", 1, 1),
= Table.AddColumn(#"Added Index", "Address_Masked",
    each Text.From([MaskIndex]) & " Main Street, Anytown, ST 00000"),
= Table.RemoveColumns(#"Removed Columns", {"Address", "MaskIndex"}),
= Table.RenameColumns(#"Final", {{"Address_Masked", "Address"}})
```

#### Step 3: Refresh and Save
```
1. Click "Close & Apply" in Power Query Editor
2. Wait for data refresh with masked values
3. Save the project
4. Verify: spot-check a few tables to confirm masking worked
```

#### Step 4: Work with Masked Copy
```
1. Open MyProject_Masked in Power BI Desktop
2. Use Claude with full Desktop Mode features
3. All proposed fixes apply to masked copy
4. Manually apply validated fixes to production project
```

**Ask Claude for Help:**
> "Help me create masking transformations for my Customer table which has Name, Email, Phone, and SSN columns"

I can generate the specific M code for your table structure.

---

### Option 3: Selective Table Exclusion

Tell Claude to avoid sampling specific tables:

**How to use:**
> "Don't sample data from the Customers or Transactions tables - they contain PII"

**What happens:**
- Formula validation still works
- Schema analysis still works
- Data sampling skips excluded tables
- Other tables can still be sampled if safe

---

### Option 4: Row-Level Sampling Limits

For tables where some exposure is acceptable:

> "You can sample the Sales table, but limit to 5 rows and exclude the CustomerName column"

---

### Quick Reference: Masking Strategies by Data Type

| Data Type | Masking Strategy | M Code Example |
|-----------|------------------|----------------|
| Names | Sequential numbering | `"Person " & Text.From([Index])` |
| Emails | Fake domain | `"user" & Text.From([Index]) & "@example.com"` |
| SSN/IDs | Partial masking | `"XXX-XX-" & Text.End(Text.From([SSN]), 4)` |
| Phones | Fake prefix | `"(555) 555-" & Text.End([Phone], 4)` |
| Addresses | Generic format | `Text.From([Index]) & " Main St, City, ST"` |
| Amounts | Scale factor | `[Amount] * (0.8 + Number.Random() * 0.4)` |
| Dates | Offset shift | `Date.AddDays([Date], Number.Random() * 30)` |
| Free text | Lorem ipsum | `"Lorem ipsum dolor sit amet..."` |

---

### What Gets Logged

- Conversation history may contain data samples (stored with Anthropic)
- Task findings files are stored locally in `.claude/tasks/`
- No data is sent to external services beyond the Claude conversation
- Use file-only mode if you need zero data exposure in conversation history

---

## Your First Workflow: Evaluate

**Best for:** Understanding problems in existing code

**How to start:**
> "The Total Sales measure is showing incorrect values. Can you help me investigate?"

**What happens:**
1. I'll ask clarifying questions about the problem
2. I'll analyze the relevant code in your project
3. I'll identify the root cause
4. I'll propose a fix with before/after comparison
5. You review and approve the fix

---

## Your First Workflow: Create Artifact

**Best for:** Building new measures, columns, or visuals

**How to start:**
> "Create a Year-over-Year Revenue Growth percentage measure"

**What happens:**
1. I'll ask about your data model (tables, columns available)
2. I'll find similar patterns in your existing code
3. I'll propose the new artifact with appropriate styling
4. You review the specification
5. I implement and validate the new artifact

---

## Your First Workflow: Analyze Dashboard

**Best for:** Understanding what a dashboard does

**How to start:**
> "Tell me what the Sales Overview page does and how its metrics are calculated"

**What happens:**
1. I'll examine the page structure and visuals
2. I'll trace each metric to its underlying measures
3. I'll explain in business terms what each component shows
4. I'll document the findings for future reference

---

## Connection Modes Explained

### Desktop Mode (Recommended for validation)
- Power BI Desktop is open with your project
- Live DAX validation catches errors immediately
- Can sample data to verify calculations
- **Use when:** You need accurate validation and data is masked or non-sensitive

### File-Only Mode (Safe for sensitive data)
- Power BI Desktop is closed or unavailable
- Syntax-only validation (can't catch semantic errors)
- No data access - only file contents
- **Use when:** Working with sensitive data or Desktop unavailable

To explicitly request file-only mode:
> "Work in file-only mode - don't access live data"

---

## Quick Tips

### Be Specific About Problems
Instead of:
> "The dashboard is broken"

Try:
> "The YoY Growth measure shows 0% even when there's data from last year"

### Point to Your Project
Instead of:
> "Look at my project"

Try:
> "My project is at C:/Projects/SalesAnalytics"

### Accept Suggested Defaults
When I ask clarifying questions, I'll often suggest a recommended option. If it looks right, you can just say "yes" or "use the recommendation."

---

## What's Next After Each Workflow?

### After Evaluate
- **If you approve the fix:** "Please implement the proposed changes"
- **If you want modifications:** "Can we adjust the fix to also handle [scenario]?"
- **If you want to start over:** "Let's try a different approach"

### After Create Artifact
- **If you approve:** "Please implement this measure"
- **If you want changes:** "Can we change the format to show 2 decimal places?"
- **If you need another:** "Create another measure for [purpose]"

### After Analyze
- **For deeper understanding:** "Explain how the [specific metric] is calculated"
- **To document findings:** "Save this analysis to [location]"
- **To make changes:** "I'd like to modify the [component]"

---

## Common Phrases You Can Use

| Intent | What to Say |
|--------|-------------|
| Start investigating | "Help me understand why [measure] shows [unexpected behavior]" |
| Create something new | "Create a [measure/column/visual] that [does what]" |
| Understand existing | "Explain what the [component] does" |
| Approve a proposal | "Yes, implement those changes" |
| Request modifications | "Can we adjust [aspect] to [change]?" |
| Request file-only mode | "Use file-only mode - don't access live data" |
| Exclude sensitive table | "Don't sample data from [table] - it's sensitive" |
| Get masking help | "Help me mask the [table] - it has [sensitive columns]" |
| See current status | "What's the status of the current task?" |
| Cancel and restart | "Let's start over with a different approach" |

---

## Need Help?

- **Confused by a term?** Ask "What does [term] mean?" or see the [Glossary](glossary.md)
- **Getting an error?** Check the [Troubleshooting FAQ](troubleshooting-faq.md)
- **Need to mask data?** Ask "Help me create masking for my [table] with [columns]"
- **Not sure what to do?** Just describe your goal in plain language

---

## Example Session

```
You: My Total Revenue measure is showing different numbers than my
     source database. Can you help figure out why?

Claude: I'd be happy to help investigate! A few questions first:

        1. What's your project path?
        2. Is Power BI Desktop open? (I can validate live if so)
        3. Does this project contain sensitive data I should avoid sampling?

You: Project is at C:/Projects/Sales. Desktop is open. This is our
     production data so please don't sample customer tables.

Claude: Got it - I'll avoid sampling customer data. Let me analyze
        the Total Revenue measure and related calculations...
        [proceeds with investigation]
```

---

*For the complete glossary of terms, see [glossary.md](glossary.md)*
*For troubleshooting help, see [troubleshooting-faq.md](troubleshooting-faq.md)*
