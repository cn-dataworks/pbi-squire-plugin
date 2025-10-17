# Power BI Data Context Agent Design

## Purpose

Enhance the `/evaluate-pbi-project-file` workflow by retrieving relevant data from Power BI datasets via XMLA endpoint to provide concrete examples and context for problem analysis.

## Integration Point in Workflow

**Insert as Phase 3.5 (between Scratchpad Creation and Agent Orchestration)**

### Updated Workflow:

1. **Phase 1**: Validation & Setup
2. **Phase 2**: Interactive Problem Clarification
3. **Phase 3**: Scratchpad Creation
4. **Phase 3.5**: Data Context Retrieval ⭐ NEW
5. **Phase 4**: Agent Orchestration (code-locator → fix-identifier → verification)
6. **Phase 5**: Completion

### Why This Position?

- ✅ Findings file exists (can write data to it)
- ✅ Problem statement is refined (can analyze what data to retrieve)
- ✅ Data is available to all subsequent agents
- ✅ Doesn't slow down initial user interaction
- ✅ Orchestrator can conditionally skip if not needed

---

## Agent Specification

### Agent Name
`powerbi-data-context-agent`

### Agent Type
Specialized agent for XMLA data retrieval and context enrichment

### Trigger Conditions

The orchestrator should invoke this agent when the problem statement contains:

#### Strong Indicators (Always Run):
- Specific identifiers: invoice numbers, order IDs, customer IDs, contract numbers
- Phrases like: "this record", "invoice X shows", "customer Y has"
- Calculation discrepancies: "total should be X but shows Y"
- Aggregation issues: "sum is wrong", "total doesn't match"

#### Moderate Indicators (Run Unless Excluded):
- Measure behavior issues: "measure returns incorrect value"
- Filter context problems: "value changes based on slicer"
- Time intelligence issues: "YoY calculation is off"

#### Skip Indicators (Don't Run):
- Pure syntax issues: "DAX syntax error", "parse error"
- Model structure only: "add a new table", "create relationship"
- Visual/formatting only: "change color", "adjust layout"
- User explicitly says "no data needed"

---

## Agent Workflow

### Input Parameters

```json
{
  "findings_file_path": "agent_scratchpads/20251013-180000-invoice-commission-issue/findings.md",
  "project_path": "C:\\Projects\\Commissions.Report",
  "workspace_url": "powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName",
  "dataset_name": "RSR Commissions Pre Prod v3",
  "problem_statement": "Invoice P3495801 shows commission of $50 but should be $92.25"
}
```

### Step 1: Problem Analysis

Parse problem statement to extract:

1. **Entity Identifiers**
   - Regex patterns for common IDs:
     - Invoice: `[A-Z]?\d{7,9}`, `INV-\d+`
     - Order: `SO-\d+`, `PO-\d+`
     - Customer: `CUST-\d+`, customer names
     - Contract: `[A-Z]\d{5,}`
   - Named entities in problem description

2. **Tables Mentioned**
   - Direct mentions: "in the Sales table"
   - Inferred from identifiers: invoice → FACT_RENTAL_INVOICE_DETAIL_RSR

3. **Measures/Calculations Mentioned**
   - Explicit: "Total Sales measure"
   - Inferred: "commission calculation"

4. **Data Retrieval Strategy**
   - Specific records: identifiers found
   - Sample data: no identifiers, general issue
   - Calculated values: measures mentioned
   - Comparison data: "should be X but is Y"

### Step 2: XMLA Connection & Authentication

1. Get Azure AD access token using device code flow
2. Construct connection string with token
3. Connect to workspace and dataset
4. Verify connection and list available tables

### Step 3: Data Retrieval Execution

Based on strategy from Step 1:

#### Strategy A: Specific Record Retrieval

```python
# Example: Retrieve invoice P3495801
agent.get_record(
    table="FACT_RENTAL_INVOICE_DETAIL_RSR",
    column="invoice_num",
    value="P3495801"
)
```

#### Strategy B: Sample Data Retrieval

```python
# Example: Get 10 representative records
agent.get_top_n(
    table="FACT_RENTAL_INVOICE_DETAIL_RSR",
    n=10,
    order_by="invoice_date"
)
```

#### Strategy C: Measure Calculation

```python
# Example: Calculate measure for specific context
agent.get_measure_value(
    measure_name="Total Commission",
    filters={"invoice_num": "P3495801"}
)
```

#### Strategy D: Related Data

```python
# Example: Get related records from multiple tables
# Invoice → Sales Rep → Commission Rate
invoice_data = agent.get_record("FACT_RENTAL_INVOICE_DETAIL_RSR", "invoice_num", "P3495801")
sales_rep_id = invoice_data['SALES_REP_ID'][0]
sales_rep_data = agent.get_record("DIM_SALES_REP", "SALES_REP_ID", sales_rep_id)
```

### Step 4: Data Formatting

Format retrieved data for maximum clarity:

```markdown
## Data Context

**Retrieved**: 2025-10-13 18:15:30
**Source**: RSR Commissions Pre Prod v3 (via XMLA)
**Query Method**: Specific record retrieval

---

### Record: Invoice P3495801

**Source Table**: FACT_RENTAL_INVOICE_DETAIL_RSR
**Records Found**: 2 (split commission between 2 reps)

#### Record 1: Sales Rep 230 (Loy Baldwin)
| Field | Value |
|-------|-------|
| Contract ID | P34958 |
| Customer ID | 679695 |
| Invoice Amount | $184.50 |
| Invoice Date | 2025-09-26 |
| Payment Status | UNPAID |
| Commission Pay Date | 10/13/2025 |
| Sales Position | SALES_REP1 |

#### Record 2: Sales Rep 637 (Riley Smith)
| Field | Value |
|-------|-------|
| Contract ID | P34958 |
| Customer ID | 679695 |
| Invoice Amount | $184.50 |
| Invoice Date | 2025-09-26 |
| Payment Status | UNPAID |
| Commission Pay Date | 10/13/2025 |
| Sales Position | SALES_REP2 |

---

### Calculated Measure Values

Executing DAX measures for this context:

| Measure | Value | Notes |
|---------|-------|-------|
| Total Commission | $50.00 | Current value from model |
| Expected Commission | $92.25 | From problem statement |
| Variance | -$42.25 | Discrepancy to investigate |

---

### Related Data

**Sales Rep Details (ID: 230)**:
- Name: Loy Baldwin
- Commission Rate: 25%
- Division: Eastern

**Sales Rep Details (ID: 637)**:
- Name: Riley Smith
- Commission Rate: 25%
- Division: Eastern

---
```

### Step 5: Insert into Findings File

Read the findings file, locate the Problem Statement section, and insert the Data Context section immediately after:

```markdown
# Analysis: Invoice Commission Calculation Issue

**Created**: 2025-10-13 18:00:00
**Project**: C:\Projects\Commissions.Report
**Status**: In Progress

---

## Problem Statement

Invoice P3495801 shows commission of $50 but should be $92.25...

---

## Data Context    <-- INSERTED HERE

[Data context content...]

---

## Section 1: Current Implementation Investigation

[To be populated by powerbi-code-locator agent]
```

---

## Orchestrator Decision Logic

Add to Phase 3.5 in `/evaluate-pbi-project-file`:

```python
# After Phase 3: Scratchpad Creation
# Before Phase 4: Agent Orchestration

def should_retrieve_data_context(problem_statement: str, project_path: str) -> bool:
    """
    Determine if data context retrieval would benefit the analysis.
    """
    # Strong indicators - always retrieve
    strong_patterns = [
        r'invoice[:\s]+[A-Z]?\d{7,}',  # Invoice numbers
        r'order[:\s]+\w+-\d+',          # Order IDs
        r'customer[:\s]+\d+',           # Customer IDs
        r'should be \$[\d,.]+ but (?:is|shows) \$[\d,.]+',  # Value discrepancies
        r'record \w+ shows',            # Specific record mentions
    ]

    for pattern in strong_patterns:
        if re.search(pattern, problem_statement, re.IGNORECASE):
            return True

    # Moderate indicators - retrieve unless excluded
    moderate_keywords = [
        'calculation', 'aggregate', 'sum', 'total', 'measure',
        'filter', 'context', 'value', 'amount', 'incorrect'
    ]

    skip_keywords = [
        'syntax error', 'parse error', 'add table', 'create relationship',
        'formatting', 'color', 'layout', 'no data needed'
    ]

    statement_lower = problem_statement.lower()

    # Check for skip conditions
    if any(keyword in statement_lower for keyword in skip_keywords):
        return False

    # Check for moderate indicators
    if any(keyword in statement_lower for keyword in moderate_keywords):
        return True

    return False


# In the orchestrator workflow:

if should_retrieve_data_context(problem_statement, project_path):
    print("📊 Retrieving data context to assist with analysis...")

    # Launch data context agent
    agent_result = Task(
        subagent_type="powerbi-data-context-agent",
        description="Retrieve relevant data context",
        prompt=f"""
        Retrieve relevant data from the Power BI dataset to provide context for this problem.

        Findings file: {findings_file_path}
        Project path: {project_path}
        Workspace: {workspace_url}
        Dataset: {dataset_name}

        Problem statement:
        {problem_statement}

        Instructions:
        1. Analyze the problem statement to identify specific records, measures, or data points mentioned
        2. Authenticate to the XMLA endpoint
        3. Retrieve relevant data using appropriate queries
        4. Format the data clearly with tables and sections
        5. Insert a "Data Context" section into the findings file after the Problem Statement

        The data context should help subsequent agents understand the concrete examples and values involved in this issue.
        """
    )

    if agent_result.success:
        print("✅ Data context added to findings file")
    else:
        print("⚠️ Data context retrieval failed, continuing without it")
        # Don't fail the entire workflow
else:
    print("ℹ️ Data context retrieval not needed for this type of issue")
```

---

## Error Handling

### Authentication Failures
- **Error**: Cannot authenticate to XMLA endpoint
- **Action**: Log warning, skip data context, continue workflow
- **Message**: "⚠️ Could not retrieve data context (authentication failed). Proceeding with code analysis only."

### Connection Failures
- **Error**: Cannot connect to workspace or dataset
- **Action**: Log warning, skip data context, continue workflow
- **Message**: "⚠️ Could not connect to Power BI dataset. XMLA endpoint may not be enabled. Proceeding without data context."

### Query Failures
- **Error**: DAX query fails or returns no results
- **Action**: Log the specific error, note in findings file
- **Message**: Add to findings: "⚠️ Attempted to retrieve data but query failed: [error details]"

### Invalid Identifiers
- **Error**: Extracted identifier doesn't exist in dataset
- **Action**: Note in findings, suggest alternative
- **Message**: "ℹ️ Could not find [identifier] in dataset. Please verify the value in the problem statement."

---

## Configuration

### Required Settings

Add to Power BI project configuration:

```python
# config.py or project settings
XMLA_CONFIG = {
    "workspace_url": "powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName",
    "dataset_name": "RSR Commissions Pre Prod v3",
    "timeout": 300,  # seconds
    "max_records": 100,  # safety limit
    "authentication_method": "device_code"  # or "service_principal"
}
```

### Optional Parameters

```python
DATA_CONTEXT_OPTIONS = {
    "enabled": True,  # Global toggle
    "auto_detect": True,  # Use heuristics
    "always_retrieve_for_tables": ["FACT_*"],  # Pattern matching
    "max_tables_to_query": 5,  # Prevent excessive queries
    "include_measure_calculations": True,
    "include_related_tables": True,
    "save_raw_data_to_csv": True  # For detailed analysis
}
```

---

## Benefits

1. **Concrete Examples**: Agents see actual data, not just descriptions
2. **Faster Diagnosis**: Real values help identify calculation errors
3. **Better Validation**: Can verify fixes against actual records
4. **Documentation**: Data context preserved in findings for future reference
5. **Reproducibility**: Specific records allow others to reproduce the issue

---

## Limitations

1. **XMLA Requirement**: Only works with Premium/PPU workspaces
2. **Authentication**: Requires user interaction (device code flow)
3. **Performance**: Large datasets may slow down retrieval
4. **Permissions**: User must have dataset read permissions
5. **Token Expiry**: Long analyses may need re-authentication

---

## Future Enhancements

1. **Token Caching**: Store and reuse tokens within session
2. **Service Principal Auth**: Support unattended execution
3. **Smart Sampling**: Use statistical methods to select representative data
4. **Change Detection**: Compare data before/after model updates
5. **Automated Test Data**: Generate test datasets based on retrieved patterns
