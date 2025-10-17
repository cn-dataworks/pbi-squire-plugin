"""
XMLA Agent for Power BI Data Querying
======================================
This agent connects to Power BI datasets via XMLA endpoint and executes DAX queries
to retrieve specific records for analysis and troubleshooting.

Usage:
    from xmla_agent import XMLAAgent

    agent = XMLAAgent(server_url, dataset_name)
    result = agent.get_record(table='Sales', column='OrderNumber', value='SO-54321')
"""

import sys
import clr

# Add ADOMD Client DLL to path before importing pyadomd
adomd_path = r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91"
sys.path.append(adomd_path)
clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

import pandas as pd
from pyadomd import Pyadomd
from typing import Optional, Dict, Any, List


class XMLAAgent:
    """Agent for querying Power BI datasets via XMLA endpoint."""

    def __init__(self, server: str, database: str):
        """
        Initialize the XMLA Agent.

        Args:
            server (str): The workspace connection URL
            database (str): The dataset name to query
        """
        self.server = server
        self.database = database
        self.conn_str = f"Provider=MSOLAP;Data Source={server};Initial Catalog={database};"
        self._connection = None

    def connect(self) -> bool:
        """
        Test the connection to the XMLA endpoint.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with Pyadomd(self.conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM $SYSTEM.DBSCHEMA_CATALOGS")
                    cursor.fetchall()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def execute_dax(self, dax_query: str) -> Optional[pd.DataFrame]:
        """
        Execute a DAX query and return results as a DataFrame.

        Args:
            dax_query (str): The DAX query to execute

        Returns:
            pd.DataFrame: Query results, or None if query failed
        """
        print(f"Executing DAX query...")
        print(f"Query:\n{dax_query}\n")

        try:
            with Pyadomd(self.conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(dax_query)
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]

                    df = pd.DataFrame(results, columns=columns)
                    print(f"Query executed successfully. Found {len(df)} row(s).\n")
                    return df

        except Exception as e:
            print(f"Query failed: {e}")
            return None

    def get_record(self, table: str, column: str, value: Any) -> Optional[pd.DataFrame]:
        """
        Retrieve a specific record from a table.

        Args:
            table (str): The table name
            column (str): The column to filter on
            value (Any): The value to search for

        Returns:
            pd.DataFrame: The matching record(s), or None if query failed
        """
        # Format value based on type
        if isinstance(value, str):
            formatted_value = f'"{value}"'
        else:
            formatted_value = str(value)

        dax_query = f"""
        EVALUATE
        FILTER (
            '{table}',
            '{table}'[{column}] = {formatted_value}
        )
        """

        return self.execute_dax(dax_query)

    def get_table_columns(self, table: str) -> Optional[List[str]]:
        """
        Get list of columns in a table.

        Args:
            table (str): The table name

        Returns:
            List[str]: List of column names, or None if query failed
        """
        dax_query = f"""
        EVALUATE
        TOPN(1, '{table}')
        """

        df = self.execute_dax(dax_query)
        if df is not None:
            return df.columns.tolist()
        return None

    def get_records_filtered(self, table: str, filters: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Retrieve records from a table with multiple filter conditions.

        Args:
            table (str): The table name
            filters (Dict[str, Any]): Dictionary of column-value pairs to filter on

        Returns:
            pd.DataFrame: The matching record(s), or None if query failed
        """
        filter_conditions = []
        for column, value in filters.items():
            if isinstance(value, str):
                formatted_value = f'"{value}"'
            else:
                formatted_value = str(value)
            filter_conditions.append(f"'{table}'[{column}] = {formatted_value}")

        filters_string = " && ".join(filter_conditions)

        dax_query = f"""
        EVALUATE
        FILTER (
            '{table}',
            {filters_string}
        )
        """

        return self.execute_dax(dax_query)

    def get_top_n(self, table: str, n: int = 10, order_by: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Get top N records from a table.

        Args:
            table (str): The table name
            n (int): Number of records to retrieve (default: 10)
            order_by (str, optional): Column to order by

        Returns:
            pd.DataFrame: The top N records, or None if query failed
        """
        if order_by:
            dax_query = f"""
            EVALUATE
            TOPN({n}, '{table}', '{table}'[{order_by}], DESC)
            """
        else:
            dax_query = f"""
            EVALUATE
            TOPN({n}, '{table}')
            """

        return self.execute_dax(dax_query)

    def get_measure_value(self, measure_name: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Calculate and return a measure value, optionally with filters.

        Args:
            measure_name (str): The measure name
            filters (Dict[str, Any], optional): Dictionary of column-value pairs to filter on

        Returns:
            Any: The measure value, or None if query failed
        """
        if filters:
            filter_conditions = []
            for column, value in filters.items():
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                else:
                    formatted_value = str(value)
                filter_conditions.append(f"'{column}' = {formatted_value}")

            filters_string = ", ".join(filter_conditions)

            dax_query = f"""
            EVALUATE
            {{
                CALCULATE([{measure_name}], {filters_string})
            }}
            """
        else:
            dax_query = f"""
            EVALUATE
            {{
                [{measure_name}]
            }}
            """

        df = self.execute_dax(dax_query)
        if df is not None and not df.empty:
            return df.iloc[0, 0]
        return None

    def list_tables(self) -> Optional[List[str]]:
        """
        Get list of all tables in the dataset.

        Returns:
            List[str]: List of table names, or None if query failed
        """
        print("Fetching table list...")
        try:
            with Pyadomd(self.conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT [DIMENSION_NAME]
                        FROM $SYSTEM.MDSCHEMA_DIMENSIONS
                        WHERE [CUBE_NAME] = 'Model'
                        ORDER BY [DIMENSION_NAME]
                    """)
                    tables = cursor.fetchall()
                    table_names = [table[0] for table in tables]
                    print(f"Found {len(table_names)} table(s).\n")
                    return table_names
        except Exception as e:
            print(f"Failed to list tables: {e}")
            return None

    def list_measures(self) -> Optional[List[str]]:
        """
        Get list of all measures in the dataset.

        Returns:
            List[str]: List of measure names, or None if query failed
        """
        print("Fetching measure list...")
        try:
            with Pyadomd(self.conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT [MEASURE_NAME]
                        FROM $SYSTEM.MDSCHEMA_MEASURES
                        WHERE [MEASURE_IS_VISIBLE] = true
                        ORDER BY [MEASURE_NAME]
                    """)
                    measures = cursor.fetchall()
                    measure_names = [measure[0] for measure in measures]
                    print(f"Found {len(measure_names)} measure(s).\n")
                    return measure_names
        except Exception as e:
            print(f"Failed to list measures: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Configuration
    SERVER = "powerbi://api.powerbi.com/v1.0/myorg/Weisiger%20Commissions"
    DATABASE = "Your Dataset Name"  # Update this with your actual dataset name

    # Initialize agent
    agent = XMLAAgent(SERVER, DATABASE)

    # Test connection
    print("Testing connection...")
    if agent.connect():
        print("Connection successful!\n")

        # List available tables
        tables = agent.list_tables()
        if tables:
            print("Available tables:")
            for table in tables:
                print(f"  • {table}")

        # Example: Get a specific record
        # result = agent.get_record(table="Sales", column="OrderNumber", value="SO-54321")
        # if result is not None and not result.empty:
        #     print("\nRecord found:")
        #     print(result.to_string())

    else:
        print("Connection failed. Check your settings.")
