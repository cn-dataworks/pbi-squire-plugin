# Power BI Data Context Agent

## Overview

The Power BI Data Context Agent retrieves relevant data from Power BI datasets via XMLA endpoint to provide concrete examples and context for problem analysis. This agent enhances the evaluation workflow by giving subsequent agents access to actual data values, not just code.

## Agent Type

`powerbi-data-context-agent`

## Purpose

- Retrieve specific records mentioned in problem statements
- Provide sample data for general issues
- Calculate measure values for context
- Document data context in findings files

## When This Agent Runs

This agent is invoked automatically by the `/evaluate-pbi-project-file` orchestrator when:

### Always Runs When:
- Specific identifiers are found (invoice P3495801, order SO-123)
- Value discrepancies mentioned ("should be $92 but shows $50")
- Specific record references ("this customer", "invoice X")

### Runs Unless Excluded:
- Measure behavior issues mentioned
- Calculation problems described
- Aggregation discrepancies noted

### Never Runs When:
- Pure syntax errors
- Model structure changes only (add table, create relationship)
- Visual/formatting issues
- User explicitly says "no data needed"

## How to Invoke

### Via Orchestrator (Automatic)

The agent is typically invoked automatically by `/evaluate-pbi-project-file`:

```bash
/evaluate-pbi-project-file --project "C:\Projects\Commissions.Report" --description "Invoice P3495801 shows commission of $50 but should be $92.25"
```

The orchestrator will detect the invoice number and automatically invoke this agent.

### Direct Invocation (Manual)

You can also invoke the agent directly:

```python
from agents.powerbi_data_context_agent.agent import DataContextAgent

agent = DataContextAgent(
    workspace_url="powerbi://api.powerbi.com/v1.0/myorg/Weisiger%20Commissions",
    dataset_name="RSR Commissions Pre Prod v3",
    findings_file="agent_scratchpads/20251013-180000-invoice-issue/findings.md",
    problem_statement="Invoice P3495801 shows commission of $50 but should be $92.25"
)

result = agent.run()
```

### Via Command Line

```bash
python agents/powerbi_data_context_agent/agent.py \
  --workspace-url "powerbi://api.powerbi.com/v1.0/myorg/Weisiger%20Commissions" \
  --dataset-name "RSR Commissions Pre Prod v3" \
  --findings-file "agent_scratchpads/20251013-180000-invoice-issue/findings.md" \
  --problem-statement "Invoice P3495801 shows commission of $50 but should be $92.25"
```

## Agent Workflow

### Step 1: Problem Analysis
- Extracts identifiers (invoice numbers, customer IDs, etc.)
- Identifies tables to query
- Determines retrieval strategy (specific records vs. sample data)
- Decides if data retrieval is beneficial

### Step 2: Authentication
- Initiates Azure AD device code flow
- Prompts user to authenticate via browser
- Establishes connection to Power BI XMLA endpoint

### Step 3: Data Retrieval
- Queries identified tables for specific records or samples
- Calculates mentioned measures with context
- Retrieves related data if needed

### Step 4: Data Formatting
- Formats retrieved data as markdown tables
- Organizes by table and record
- Includes timestamps and source information

### Step 5: Findings Update
- Inserts "Data Context" section into findings file
- Places section after "Problem Statement"
- Preserves all existing content

## Output Format

The agent adds a section to the findings file:

```markdown
## Data Context

**Retrieved**: 2025-10-13 18:15:30
**Source**: RSR Commissions Pre Prod v3 (via XMLA)
**Query Strategy**: Specific Records

---

### FACT_RENTAL_INVOICE_DETAIL_RSR

**Identifier**: invoice_num=P3495801
**Records Found**: 2

#### Record 1

| Field | Value |
|-------|-------|
| CONTRACT_ID | P34958 |
| CUSTOMER_ID | 679695 |
| INVOICE_AMOUNT | 184.50 |
| SALES_REP_ID | 230 |
| NAME_SALES_REP1 | Loy Baldwin |
| ...

#### Record 2

| Field | Value |
|-------|-------|
| CONTRACT_ID | P34958 |
| CUSTOMER_ID | 679695 |
| INVOICE_AMOUNT | 184.50 |
| SALES_REP_ID | 637 |
| NAME_SALES_REP2 | Riley Smith |
| ...

---

### Calculated Measure Values

| Measure | Value |
|---------|-------|
| Total Commission | 50.00 |

---
```

## Requirements

### System Requirements
- Windows (for ADOMD Client)
- Python 3.7+
- Microsoft Analysis Services ADOMD Client installed

### Power BI Requirements
- Premium or Premium Per User workspace
- XMLA endpoint enabled (Read access minimum)
- User must have dataset read permissions

### Python Packages
- pyadomd
- pandas
- msal (for authentication)
- pythonnet

## Configuration

The agent uses workspace and dataset configuration from the orchestrator or command-line arguments. No separate config file is required.

### Environment Variables (Optional)

```bash
# Set default workspace
export PBI_WORKSPACE_URL="powerbi://api.powerbi.com/v1.0/myorg/YourWorkspace"

# Set default dataset
export PBI_DATASET_NAME="Your Dataset Name"
```

## Error Handling

### Authentication Failures
- **Error**: Cannot authenticate to XMLA endpoint
- **Action**: Logs warning, returns status='error'
- **Impact**: Workflow continues without data context

### Connection Failures
- **Error**: Cannot connect to workspace or dataset
- **Action**: Logs error, returns status='error'
- **Impact**: Workflow continues without data context

### Query Failures
- **Error**: DAX query fails or returns no results
- **Action**: Logs error, notes in findings
- **Impact**: Partial data context may be available

### Invalid Identifiers
- **Error**: Extracted identifier doesn't exist
- **Action**: Notes in output, continues with other identifiers
- **Impact**: Some data missing but agent completes

## Return Values

The agent returns a dict with:

```python
{
    'status': 'success' | 'skipped' | 'warning' | 'error',
    'message': 'Description of result',
    'data': {
        'records': [...],      # Retrieved records
        'measures': {...},     # Calculated measures
        'related_data': {...}  # Related table data
    }
}
```

### Status Meanings

- **success**: Data retrieved and added to findings
- **skipped**: Data retrieval not needed for this problem type
- **warning**: Partial data retrieved or non-critical issues
- **error**: Failed to retrieve data (authentication, connection, etc.)

## Examples

### Example 1: Specific Invoice

**Problem**: "Invoice P3495801 shows commission of $50 but should be $92.25"

**Agent Action**:
1. Extracts identifier: P3495801
2. Identifies table: FACT_RENTAL_INVOICE_DETAIL_RSR
3. Queries: `get_record('FACT_RENTAL_INVOICE_DETAIL_RSR', 'invoice_num', 'P3495801')`
4. Finds 2 records (split commission)
5. Adds detailed data context to findings

**Result**: Subsequent agents see actual invoice data including amounts, sales reps, dates, etc.

### Example 2: General Calculation Issue

**Problem**: "The Total Sales measure returns incorrect values"

**Agent Action**:
1. No specific identifiers found
2. Identifies measure: Total Sales
3. Retrieves sample data from Sales table
4. Calculates Total Sales measure for context
5. Adds sample data and measure value to findings

**Result**: Agents see representative data and current measure behavior

### Example 3: Syntax Error (Skipped)

**Problem**: "DAX syntax error in Total Revenue measure"

**Agent Action**:
1. Detects "syntax error" keyword
2. Determines data retrieval not needed
3. Returns status='skipped'

**Result**: No data context added, workflow continues immediately to code analysis

## Integration with Workflow

This agent fits into the `/evaluate-pbi-project-file` workflow at Phase 3.5:

```
Phase 1: Validation & Setup
Phase 2: Interactive Problem Clarification
Phase 3: Scratchpad Creation
Phase 3.5: Data Context Retrieval  <-- THIS AGENT
Phase 4: Code Analysis
  - powerbi-code-locator (reads data context)
  - powerbi-code-fix-identifier (uses data context)
  - power-bi-verification (validates against data context)
Phase 5: Completion
```

## Benefits

1. **Concrete Examples**: Agents see actual data, not just descriptions
2. **Faster Diagnosis**: Real values expose calculation errors immediately
3. **Better Validation**: Can verify fixes against specific records
4. **Complete Documentation**: Findings include both data and code
5. **Reproducibility**: Exact records allow others to reproduce the issue

## Limitations

1. **XMLA Required**: Only works with Premium/PPU workspaces
2. **Authentication**: Requires interactive user authentication
3. **Performance**: Large datasets may slow retrieval
4. **Permissions**: User must have read access to dataset
5. **Token Expiry**: Long-running analyses may need re-authentication

## Troubleshooting

### "Could not authenticate"
- Ensure you completed the device code flow in the browser
- Verify you have access to the workspace
- Check that XMLA endpoint is enabled

### "Cannot connect to dataset"
- Verify dataset name is correct (case-sensitive)
- Check workspace URL format
- Ensure you have read permissions

### "No data retrieved"
- Verify identifiers exist in the dataset
- Check table names match actual table names
- Ensure columns exist in the tables

### "Agent taking too long"
- Reduce number of tables queried
- Limit sample size (default is 5 records)
- Check network connection to Power BI

## Developer Notes

### Adding New Identifier Patterns

To support additional identifier types, update `_extract_identifiers()`:

```python
# Add pattern
new_patterns = [
    r'\bYOUR-PATTERN-\d+\b',
]

# Add mapping
def _map_identifier_to_column(self, id_type: str) -> str:
    mapping = {
        'your_type': 'your_column_name'
    }
```

### Customizing Data Format

To change how data is displayed, modify `_format_data_context()`:

```python
def _format_data_context(self, data_context, analysis):
    # Customize markdown generation here
    pass
```

### Extending Retrieval Strategies

Add new strategies in `_retrieve_data()`:

```python
elif analysis['strategy'] == 'your_new_strategy':
    # Implement custom retrieval logic
    pass
```

## Version History

- **v1.0** (2025-10-13): Initial implementation
  - Specific record retrieval
  - Sample data retrieval
  - Measure calculation
  - Findings file integration
