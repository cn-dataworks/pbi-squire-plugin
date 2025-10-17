"""
Query specific invoice from FACT_RENTAL_INVOICE_DETAIL_RSR
"""

import sys
import clr

# Add ADOMD Client DLL to path
adomd_path = r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91"
sys.path.append(adomd_path)
clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

from xmla_agent import XMLAAgent
from get_token import get_access_token
from config import WORKSPACE_URL, DATASET_NAME


def main():
    print("\n" + "="*70)
    print("Query Invoice from RSR Dataset")
    print("="*70)

    # Get access token
    print("\nAuthenticating...")
    access_token = get_access_token()

    if not access_token:
        print("Failed to get access token.")
        sys.exit(1)

    # Initialize agent with token
    agent = XMLAAgent(WORKSPACE_URL, DATASET_NAME)

    # Update connection string to include token
    agent.conn_str = f"Provider=MSOLAP;Data Source={WORKSPACE_URL};Initial Catalog={DATASET_NAME};Password={access_token};"

    # Query for the invoice
    invoice_num = "P3495801"
    table = "FACT_RENTAL_INVOICE_DETAIL_RSR"

    print(f"\nSearching for invoice_num = {invoice_num} in {table}...")
    print("="*70 + "\n")

    result = agent.get_record(table, "invoice_num", invoice_num)

    if result is not None and not result.empty:
        print(f"FOUND! Retrieved {len(result)} record(s):\n")
        print("="*70)

        # Print results in a readable format
        for idx, row in result.iterrows():
            print(f"\nRecord {idx + 1}:")
            print("-" * 70)
            for col in result.columns:
                value = row[col]
                print(f"  {col}: {value}")

        print("\n" + "="*70)
        print(f"\nTotal records found: {len(result)}")

        # Also save to CSV for easier viewing
        output_file = f"invoice_{invoice_num}_results.csv"
        result.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")

    elif result is not None:
        print(f"NOT FOUND: No records with invoice_num = {invoice_num}")
    else:
        print("ERROR: Query failed. Check table and column names.")


if __name__ == "__main__":
    main()
