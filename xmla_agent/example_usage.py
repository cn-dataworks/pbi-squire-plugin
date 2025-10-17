"""
Example Usage of XMLA Agent
============================
This script demonstrates common use cases for the XMLA Agent.

Before running:
1. Update config.py with your workspace URL and dataset name
2. Ensure XMLA endpoint is enabled
3. Install dependencies: pip install -r requirements.txt
"""

import sys
import clr

# Add ADOMD Client DLL to path before importing pyadomd
adomd_path = r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91"
sys.path.append(adomd_path)
clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

from xmla_agent import XMLAAgent
from config import WORKSPACE_URL, DATASET_NAME


def main():
    print("="*70)
    print("🤖 XMLA Agent - Example Usage")
    print("="*70)

    # Initialize the agent
    print(f"\n📍 Connecting to workspace: Weisiger Commissions")
    print(f"📊 Dataset: {DATASET_NAME}\n")

    agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

    # Test connection
    print("🔌 Testing connection...")
    if not agent.connect():
        print("❌ Connection failed. Please check your configuration.")
        return

    print("✅ Connection successful!\n")

    # Example 1: List all tables
    print("\n" + "="*70)
    print("Example 1: List All Tables")
    print("="*70)
    tables = agent.list_tables()
    if tables:
        print(f"\nFound {len(tables)} tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

    # Example 2: Get table columns
    print("\n" + "="*70)
    print("Example 2: Get Columns from First Table")
    print("="*70)
    if tables and len(tables) > 0:
        first_table = tables[0]
        print(f"\nGetting columns for table: {first_table}")
        columns = agent.get_table_columns(first_table)
        if columns:
            print(f"\nColumns in '{first_table}':")
            for i, col in enumerate(columns, 1):
                print(f"{i}. {col}")

    # Example 3: Get top 5 records from first table
    print("\n" + "="*70)
    print("Example 3: Get Top 5 Records")
    print("="*70)
    if tables and len(tables) > 0:
        first_table = tables[0]
        print(f"\nGetting top 5 records from: {first_table}")
        top_records = agent.get_top_n(first_table, n=5)
        if top_records is not None and not top_records.empty:
            print(f"\n{top_records.to_string()}\n")

    # Example 4: List all measures
    print("\n" + "="*70)
    print("Example 4: List All Measures")
    print("="*70)
    measures = agent.list_measures()
    if measures:
        print(f"\nFound {len(measures)} measures:")
        for i, measure in enumerate(measures, 1):
            print(f"{i}. {measure}")

    # Example 5: Custom DAX query
    print("\n" + "="*70)
    print("Example 5: Custom DAX Query")
    print("="*70)
    print("\nExecuting custom DAX query to get row count from first table...")
    if tables and len(tables) > 0:
        first_table = tables[0]
        dax_query = f"""
        EVALUATE
        ROW(
            "Table", "{first_table}",
            "Row Count", COUNTROWS('{first_table}')
        )
        """
        result = agent.execute_dax(dax_query)
        if result is not None and not result.empty:
            print(f"\n{result.to_string()}\n")

    # Interactive section
    print("\n" + "="*70)
    print("Interactive Mode")
    print("="*70)
    print("\nYou can now query specific records.")
    print("Type 'exit' to quit.\n")

    while True:
        table_name = input("Enter table name (or 'exit'): ").strip()
        if table_name.lower() == 'exit':
            break

        column_name = input("Enter column name: ").strip()
        value = input("Enter value to search for: ").strip()

        print(f"\n🔍 Searching for {column_name} = {value} in {table_name}...")
        result = agent.get_record(table_name, column_name, value)

        if result is not None and not result.empty:
            print("\n✅ Found record(s):")
            print(result.to_string())
            print(f"\nTotal records found: {len(result)}\n")
        elif result is not None:
            print(f"\n❌ No records found matching {column_name} = {value}\n")
        else:
            print("\n❌ Query failed. Check table and column names.\n")

    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
