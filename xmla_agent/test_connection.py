"""
XMLA Connection Tester
======================
This script tests whether the XMLA endpoint is enabled for your Power BI workspace
and whether you have access to it.

Usage:
    python test_connection.py
"""

import sys
import os

# Add ADOMD Client DLL to path before importing pyadomd
import clr
adomd_path = r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91"
sys.path.append(adomd_path)
clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

from pyadomd import Pyadomd


# Default workspace connection URL
DEFAULT_SERVER = "powerbi://api.powerbi.com/v1.0/myorg/Weisiger%20Commissions"


def test_xmla_connection(server, database=None):
    """
    Tests the connection to a Power BI XMLA endpoint.

    Args:
        server (str): The workspace connection URL (e.g., powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName)
        database (str, optional): The name of a specific dataset to test

    Returns:
        bool: True if connection successful, False otherwise
    """
    print("\n" + "="*70)
    print("Testing XMLA Endpoint Connection")
    print("="*70)
    print(f"\nServer: {server}")
    if database:
        print(f"Database: {database}")
    print("\nAttempting to connect...\n")

    try:
        # Attempt to establish connection
        # Construct connection string
        if database:
            conn_str = f"Provider=MSOLAP;Data Source={server};Initial Catalog={database};"
        else:
            conn_str = f"Provider=MSOLAP;Data Source={server};"

        with Pyadomd(conn_str) as conn:
            # If we get here, connection was successful
            print("SUCCESS! Connection established.\n")

            # Try to get some basic info
            with conn.cursor() as cursor:
                # Get list of available databases (datasets)
                cursor.execute("SELECT * FROM $SYSTEM.DBSCHEMA_CATALOGS")
                catalogs = cursor.fetchall()

                if catalogs:
                    print(f"Found {len(catalogs)} dataset(s) in workspace:")
                    for catalog in catalogs:
                        print(f"   - {catalog[0]}")

                # If a specific database was provided, get table info
                if database:
                    print(f"\nTables in '{database}':")
                    cursor.execute("""
                        SELECT [DIMENSION_NAME]
                        FROM $SYSTEM.MDSCHEMA_DIMENSIONS
                        WHERE [CUBE_NAME] = 'Model'
                        ORDER BY [DIMENSION_NAME]
                    """)
                    tables = cursor.fetchall()
                    for table in tables:
                        print(f"   - {table[0]}")

            print("\n" + "="*70)
            print("XMLA endpoint is ENABLED and accessible!")
            print("="*70)
            return True

    except Exception as e:
        print(f"FAILED: Could not connect to XMLA endpoint.\n")
        print(f"Error details:\n{str(e)}\n")
        print("="*70)
        print("Possible reasons:")
        print("  1. XMLA endpoint is not enabled on your Premium capacity")
        print("  2. You don't have access to this workspace")
        print("  3. The workspace connection URL is incorrect")
        print("  4. Authentication failed")
        print("\nNext steps:")
        print("  - Verify the workspace connection URL")
        print("  - Contact your Power BI admin to enable XMLA endpoint")
        print("="*70)
        return False


def main():
    """Main function to test connection with user input."""

    print("\nXMLA Connection Tester")
    print("=" * 70)

    # Use default server
    server = DEFAULT_SERVER
    print(f"\nTesting workspace: Weisiger Commissions")
    print(f"URL: {server}")

    # Ask if user wants to specify a dataset
    print("\nDo you want to test a specific dataset?")
    database = input("Enter Dataset Name (press Enter to skip): ").strip()
    if not database:
        database = None

    # Test the connection
    success = test_xmla_connection(server, database)

    if success:
        print("\nYou're all set! You can now use the XMLA agent to query data.")
        sys.exit(0)
    else:
        print("\nConnection test failed. Please resolve the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
