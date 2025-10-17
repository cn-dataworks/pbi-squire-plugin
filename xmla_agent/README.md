# XMLA Agent for Power BI

This agent connects to Power BI datasets via the XMLA endpoint to query data directly from the Analysis Services engine. It's useful for troubleshooting, data validation, and automated analysis.

## What is the XMLA Endpoint?

The XMLA (XML for Analysis) endpoint exposes Power BI's underlying SQL Server Analysis Services engine, allowing external tools and scripts to connect directly to datasets. This enables:

- Querying data using DAX
- Retrieving specific records for troubleshooting
- Analyzing data model metadata
- Automating data validation tasks

**Important:** XMLA endpoint access requires Power BI Premium or Premium Per User capacity.

## Prerequisites

1. **Power BI Premium/Premium Per User**: Your workspace must be in a Premium capacity
2. **XMLA Endpoint Enabled**: Admin must enable read access (or read/write) in capacity settings
3. **Workspace Access**: You must have access to the target workspace
4. **Python 3.7+**: Required to run the scripts

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd xmla_agent
pip install -r requirements.txt
```

### Step 2: Configure Connection

Edit `config.py` and update:

```python
WORKSPACE_URL = "powerbi://api.powerbi.com/v1.0/myorg/Weisiger%20Commissions"
DATASET_NAME = "Your Dataset Name Here"  # Replace with your actual dataset name
```

To find your workspace connection URL:
1. Go to your Power BI workspace
2. Click **Settings** → **Premium** tab
3. Copy the **Workspace Connection** URL at the bottom

### Step 3: Test Connection

Run the connection tester to verify XMLA endpoint is accessible:

```bash
python test_connection.py
```

If successful, you'll see a list of datasets in your workspace.

**If connection fails:**
- XMLA endpoint may not be enabled → Contact your Power BI admin
- You may not have workspace access → Check permissions
- Authentication may have failed → Verify credentials

## Usage Examples

### Example 1: Basic Connection Test

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

if agent.connect():
    print("Connected successfully!")
```

### Example 2: List Available Tables

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

tables = agent.list_tables()
for table in tables:
    print(f"• {table}")
```

### Example 3: Query a Specific Record

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

# Find a specific order by order number
result = agent.get_record(
    table="Sales",
    column="OrderNumber",
    value="SO-54321"
)

if result is not None and not result.empty:
    print(result)
```

### Example 4: Get Top N Records

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

# Get top 10 records from Sales table, ordered by Date
top_sales = agent.get_top_n(
    table="Sales",
    n=10,
    order_by="Date"
)

print(top_sales)
```

### Example 5: Query with Multiple Filters

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

# Find records matching multiple criteria
results = agent.get_records_filtered(
    table="Sales",
    filters={
        "Region": "West",
        "Year": 2024
    }
)

print(results)
```

### Example 6: Execute Custom DAX Query

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

dax_query = """
EVALUATE
SUMMARIZECOLUMNS(
    'Sales'[Region],
    "Total Sales", SUM('Sales'[Amount])
)
ORDER BY [Total Sales] DESC
"""

result = agent.execute_dax(dax_query)
print(result)
```

### Example 7: Get Measure Value

```python
from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME

agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

# Calculate a measure with filters
total_sales = agent.get_measure_value(
    measure_name="Total Sales",
    filters={"Year": 2024, "Region": "East"}
)

print(f"Total Sales for East in 2024: ${total_sales:,.2f}")
```

## Troubleshooting

### "Cannot connect to powerbi://..."

**Cause:** XMLA endpoint is not enabled or you don't have access.

**Solution:**
1. Verify workspace is in Premium capacity
2. Ask admin to enable XMLA endpoint: Admin Portal → Capacity Settings → XMLA Endpoint → Read
3. Confirm you have workspace access

### "The specified database could not be found"

**Cause:** Dataset name in `config.py` doesn't match actual dataset name.

**Solution:**
1. Run `test_connection.py` without specifying a database
2. See list of available datasets
3. Update `DATASET_NAME` in `config.py` with exact name

### Authentication Errors

**Cause:** Azure AD authentication issues.

**Solution:**
1. Ensure you're logged into Azure/Power BI
2. Try running in an environment with valid Azure credentials
3. You may need to authenticate via browser on first connection

## How to Check if XMLA is Enabled (Without Admin Access)

Use **SQL Server Management Studio (SSMS)** or **DAX Studio**:

1. Open SSMS
2. Connect to Analysis Services
3. Enter your workspace connection URL as the server
4. Use Azure AD authentication
5. If it connects, XMLA is enabled ✅
6. If it fails, XMLA is not enabled ❌

## Advanced Usage

### Get Table Columns

```python
columns = agent.get_table_columns("Sales")
print(f"Columns in Sales table: {columns}")
```

### List All Measures

```python
measures = agent.list_measures()
for measure in measures:
    print(f"• {measure}")
```

## API Reference

### XMLAAgent Class

#### `__init__(server: str, database: str)`
Initialize the agent with workspace URL and dataset name.

#### `connect() -> bool`
Test connection to XMLA endpoint.

#### `execute_dax(dax_query: str) -> pd.DataFrame`
Execute a custom DAX query.

#### `get_record(table: str, column: str, value: Any) -> pd.DataFrame`
Get a specific record from a table.

#### `get_records_filtered(table: str, filters: Dict[str, Any]) -> pd.DataFrame`
Get records matching multiple filter conditions.

#### `get_top_n(table: str, n: int, order_by: Optional[str]) -> pd.DataFrame`
Get top N records from a table.

#### `get_measure_value(measure_name: str, filters: Optional[Dict[str, Any]]) -> Any`
Calculate a measure value with optional filters.

#### `list_tables() -> List[str]`
Get list of all tables in the dataset.

#### `list_measures() -> List[str]`
Get list of all measures in the dataset.

#### `get_table_columns(table: str) -> List[str]`
Get list of columns in a specific table.

## Files

- **`xmla_agent.py`**: Main agent class with query methods
- **`test_connection.py`**: Connection tester script
- **`config.py`**: Configuration file for workspace and dataset
- **`requirements.txt`**: Python dependencies
- **`README.md`**: This file

## Notes

- Always use read-only XMLA access unless you need write capabilities
- Large queries may take time to execute
- Results are returned as pandas DataFrames for easy analysis
- Authentication uses Azure AD credentials automatically

## Support

If you encounter issues:
1. Verify workspace is Premium/PPU
2. Check XMLA endpoint is enabled
3. Confirm dataset name is correct
4. Ensure you have workspace access
5. Test connection with `test_connection.py`

For Power BI XMLA documentation, visit: https://learn.microsoft.com/power-bi/enterprise/service-premium-connect-tools
