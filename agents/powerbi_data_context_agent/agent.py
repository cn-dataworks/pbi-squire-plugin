"""
Power BI Data Context Agent

This agent retrieves relevant data from Power BI datasets via XMLA endpoint to provide
concrete examples and context for problem analysis.

Agent Type: powerbi-data-context-agent
Purpose: Enhance analysis with actual data from the Power BI dataset
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Add xmla_agent to path
xmla_path = Path(__file__).parent.parent.parent / "xmla_agent"
sys.path.insert(0, str(xmla_path))

# Add ADOMD Client DLL to path
import clr
adomd_path = r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91"
sys.path.append(adomd_path)
clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

from xmla_agent import XMLAAgent
from get_token import get_access_token


class DataContextAgent:
    """
    Agent for retrieving data context from Power BI datasets to assist with analysis.
    """

    def __init__(self, workspace_url: str, dataset_name: str, findings_file: str, problem_statement: str):
        """
        Initialize the Data Context Agent.

        Args:
            workspace_url: Power BI workspace XMLA connection URL
            dataset_name: Name of the dataset to query
            findings_file: Path to the findings markdown file
            problem_statement: The problem description to analyze
        """
        self.workspace_url = workspace_url
        self.dataset_name = dataset_name
        self.findings_file = findings_file
        self.problem_statement = problem_statement
        self.agent = None
        self.access_token = None

    def run(self) -> Dict[str, Any]:
        """
        Main execution method for the agent.

        Returns:
            Dict with status, message, and data retrieved
        """
        print("=" * 70)
        print("Power BI Data Context Agent")
        print("=" * 70)
        print(f"\nDataset: {self.dataset_name}")
        print(f"Findings File: {self.findings_file}")
        print("\n" + "=" * 70)

        try:
            # Step 1: Analyze problem statement
            print("\n[Step 1/5] Analyzing problem statement...")
            analysis = self._analyze_problem_statement()

            if not analysis['should_retrieve']:
                print("   No data retrieval needed for this problem type")
                return {
                    'status': 'skipped',
                    'message': 'Data context not applicable for this problem',
                    'data': None
                }

            print(f"   Strategy: {analysis['strategy']}")
            print(f"   Identifiers found: {analysis['identifiers']}")
            print(f"   Tables to query: {analysis['tables']}")

            # Step 2: Authenticate
            print("\n[Step 2/5] Authenticating to Power BI...")
            auth_result = self._authenticate()

            if not auth_result['success']:
                if auth_result.get('auth_required'):
                    # Authentication blocked - need user interaction
                    print("   [BLOCKED] User authentication required")
                    print("\n" + "=" * 70)
                    print("Data Context Agent: AUTH_REQUIRED")
                    print("=" * 70)
                    return {
                        'status': 'auth_required',
                        'message': 'User authentication required to retrieve data from Power BI',
                        'auth_info': auth_result['auth_info'],
                        'data': None
                    }
                else:
                    # Other authentication error
                    error_msg = auth_result.get('error', 'Authentication failed')
                    print(f"   [ERROR] Authentication failed: {error_msg}")
                    return {
                        'status': 'error',
                        'message': f'Authentication failed: {error_msg}',
                        'data': None
                    }

            print("   [SUCCESS] Authentication successful")

            # Step 3: Retrieve data
            print("\n[Step 3/5] Retrieving data from dataset...")
            data_context = self._retrieve_data(analysis)

            if not data_context:
                print("   No data retrieved")
                return {
                    'status': 'warning',
                    'message': 'Could not retrieve data',
                    'data': None
                }

            print(f"   Retrieved {len(data_context['records'])} record(s)")

            # Step 4: Format data
            print("\n[Step 4/5] Formatting data context...")
            formatted_content = self._format_data_context(data_context, analysis)

            # Step 5: Update findings file
            print("\n[Step 5/5] Updating findings file...")
            self._update_findings_file(formatted_content)
            print("   Findings file updated successfully")

            print("\n" + "=" * 70)
            print("Data Context Agent: COMPLETED")
            print("=" * 70)

            return {
                'status': 'success',
                'message': 'Data context added to findings',
                'data': data_context
            }

        except Exception as e:
            print(f"\n[ERROR] Agent failed: {str(e)}")
            print("=" * 70)
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }

    def _analyze_problem_statement(self) -> Dict[str, Any]:
        """
        Analyze the problem statement to determine data retrieval strategy.

        Returns:
            Dict with analysis results
        """
        statement_lower = self.problem_statement.lower()

        # Extract identifiers
        identifiers = self._extract_identifiers(self.problem_statement)

        # Determine tables to query
        tables = self._identify_tables(self.problem_statement, identifiers)

        # Determine strategy
        strategy = 'specific_records' if identifiers else 'sample_data'

        # Check if we should retrieve data
        should_retrieve = self._should_retrieve_data(statement_lower, identifiers)

        return {
            'should_retrieve': should_retrieve,
            'strategy': strategy,
            'identifiers': identifiers,
            'tables': tables,
            'measures': self._extract_measures(self.problem_statement)
        }

    def _extract_identifiers(self, text: str) -> Dict[str, List[str]]:
        """
        Extract identifiers (invoice numbers, order IDs, etc.) from text.

        Returns:
            Dict of identifier types to values
        """
        identifiers = {}

        # Invoice patterns
        invoice_patterns = [
            r'\b[A-Z]?\d{7,9}\b',  # P3495801, 12345678
            r'\bINV-\d+\b',         # INV-12345
        ]
        invoices = []
        for pattern in invoice_patterns:
            invoices.extend(re.findall(pattern, text, re.IGNORECASE))
        if invoices:
            identifiers['invoice'] = list(set(invoices))

        # Order patterns
        order_patterns = [
            r'\b(?:SO|PO)-\d+\b',  # SO-12345, PO-67890
        ]
        orders = []
        for pattern in order_patterns:
            orders.extend(re.findall(pattern, text, re.IGNORECASE))
        if orders:
            identifiers['order'] = list(set(orders))

        # Customer ID patterns
        customer_patterns = [
            r'\bCUST-\d+\b',           # CUST-12345
            r'\bcustomer\s+(\d{5,})\b',  # customer 679695
        ]
        customers = []
        for pattern in customer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            customers.extend(matches)
        if customers:
            identifiers['customer'] = list(set(customers))

        # Contract patterns
        contract_patterns = [
            r'\bcontract\s+([A-Z]\d{5,})\b',  # contract P34958
        ]
        contracts = []
        for pattern in contract_patterns:
            contracts.extend(re.findall(pattern, text, re.IGNORECASE))
        if contracts:
            identifiers['contract'] = list(set(contracts))

        return identifiers

    def _identify_tables(self, text: str, identifiers: Dict[str, List[str]]) -> List[str]:
        """
        Identify which tables should be queried based on context.

        Returns:
            List of table names
        """
        tables = []

        # Explicit table mentions
        table_patterns = [
            r'in\s+(?:the\s+)?(\w+)\s+table',
            r'table\s+(\w+)',
            r'from\s+(\w+)'
        ]

        for pattern in table_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tables.extend(matches)

        # Infer tables from identifiers
        if 'invoice' in identifiers:
            tables.append('FACT_RENTAL_INVOICE_DETAIL_RSR')

        if 'order' in identifiers:
            tables.append('FACT_EQUIPMENT_SALES_RPO_CONTRACT_RSR_SALES')

        if 'customer' in identifiers:
            tables.append('DIM_CUSTOMER')

        # Remove duplicates, preserve order
        seen = set()
        unique_tables = []
        for table in tables:
            table_upper = table.upper()
            if table_upper not in seen:
                seen.add(table_upper)
                unique_tables.append(table_upper)

        return unique_tables

    def _extract_measures(self, text: str) -> List[str]:
        """
        Extract measure names mentioned in the problem statement.

        Returns:
            List of measure names
        """
        measures = []

        # Common measure patterns
        patterns = [
            r'(?:measure|calculation)\s+["\']?(\w+(?:\s+\w+)*)["\']?',
            r'\[([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\]',  # [Total Sales]
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            measures.extend(matches)

        return list(set(measures))

    def _should_retrieve_data(self, statement_lower: str, identifiers: Dict) -> bool:
        """
        Determine if data retrieval is beneficial for this problem.

        Returns:
            Boolean indicating whether to retrieve data
        """
        # Skip conditions
        skip_keywords = [
            'syntax error', 'parse error', 'add table', 'create relationship',
            'formatting', 'color', 'layout', 'no data needed', 'visual'
        ]

        if any(keyword in statement_lower for keyword in skip_keywords):
            return False

        # Strong indicators (always retrieve)
        if identifiers:
            return True

        if re.search(r'should be .+ but (?:is|shows)', statement_lower):
            return True

        # Moderate indicators
        moderate_keywords = [
            'calculation', 'aggregate', 'sum', 'total', 'measure',
            'filter', 'context', 'value', 'amount', 'incorrect', 'wrong'
        ]

        if any(keyword in statement_lower for keyword in moderate_keywords):
            return True

        return False

    def _authenticate(self) -> dict:
        """
        Authenticate to Power BI via Azure AD.

        Returns:
            dict with 'success' (bool) and optional 'auth_info' if auth required
        """
        try:
            # Don't wait for user in non-interactive mode - return flow details immediately
            token_result = get_access_token(return_flow_on_timeout=True, wait_for_user=False)

            # Check if authentication succeeded
            if isinstance(token_result, str):
                # Success - token_result is the access token
                self.access_token = token_result

                # Initialize agent with token
                self.agent = XMLAAgent(self.workspace_url, self.dataset_name)
                self.agent.conn_str = f"Provider=MSOLAP;Data Source={self.workspace_url};Initial Catalog={self.dataset_name};Password={self.access_token};"

                # Test connection
                if self.agent.connect():
                    return {'success': True}
                else:
                    return {'success': False, 'error': 'Connection test failed'}

            # Check if auth is required (device code flow timeout)
            elif isinstance(token_result, dict) and token_result.get('status') == 'auth_required':
                # Return auth required status with flow details
                return {
                    'success': False,
                    'auth_required': True,
                    'auth_info': token_result
                }

            # Authentication failed for other reasons
            else:
                return {'success': False, 'error': 'Authentication failed'}

        except Exception as e:
            print(f"   Authentication error: {e}")
            return {'success': False, 'error': str(e)}

    def _retrieve_data(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve data based on the analysis strategy.

        Returns:
            Dict containing retrieved data
        """
        data_context = {
            'records': [],
            'measures': {},
            'related_data': {}
        }

        try:
            if analysis['strategy'] == 'specific_records':
                # Retrieve specific records
                for table in analysis['tables']:
                    for id_type, id_values in analysis['identifiers'].items():
                        for id_value in id_values:
                            # Determine column name
                            column = self._map_identifier_to_column(id_type)

                            result = self.agent.get_record(table, column, id_value)

                            if result is not None and not result.empty:
                                data_context['records'].append({
                                    'table': table,
                                    'identifier': f"{column}={id_value}",
                                    'count': len(result),
                                    'data': result
                                })

            elif analysis['strategy'] == 'sample_data':
                # Get sample data from identified tables
                for table in analysis['tables'][:2]:  # Limit to 2 tables
                    result = self.agent.get_top_n(table, n=5)

                    if result is not None and not result.empty:
                        data_context['records'].append({
                            'table': table,
                            'identifier': 'sample',
                            'count': len(result),
                            'data': result
                        })

            # Retrieve measure values if mentioned
            for measure_name in analysis['measures']:
                try:
                    value = self.agent.get_measure_value(measure_name)
                    if value is not None:
                        data_context['measures'][measure_name] = value
                except:
                    pass  # Measure might not exist

            return data_context if data_context['records'] else None

        except Exception as e:
            print(f"   Data retrieval error: {e}")
            return None

    def _map_identifier_to_column(self, id_type: str) -> str:
        """
        Map identifier type to likely column name.

        Returns:
            Column name
        """
        mapping = {
            'invoice': 'invoice_num',
            'order': 'order_id',
            'customer': 'customer_id',
            'contract': 'contract_id'
        }
        return mapping.get(id_type, 'id')

    def _format_data_context(self, data_context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Format the data context as markdown.

        Returns:
            Formatted markdown string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "",
            "## Data Context",
            "",
            f"**Retrieved**: {timestamp}",
            f"**Source**: {self.dataset_name} (via XMLA)",
            f"**Query Strategy**: {analysis['strategy'].replace('_', ' ').title()}",
            "",
            "---",
            ""
        ]

        # Add records
        for record_group in data_context['records']:
            table = record_group['table']
            identifier = record_group['identifier']
            count = record_group['count']
            data = record_group['data']

            lines.append(f"### {table}")
            lines.append("")
            lines.append(f"**Identifier**: {identifier}")
            lines.append(f"**Records Found**: {count}")
            lines.append("")

            # Format as table for each record
            for idx, (_, row) in enumerate(data.iterrows(), 1):
                if count > 1:
                    lines.append(f"#### Record {idx}")
                    lines.append("")

                lines.append("| Field | Value |")
                lines.append("|-------|-------|")

                for col in data.columns:
                    # Clean column name for display
                    display_col = col.split('[')[1].rstrip(']') if '[' in col else col
                    value = row[col]

                    # Format value
                    if value is None or (isinstance(value, float) and value != value):  # NaN check
                        value_str = "None"
                    elif isinstance(value, float):
                        value_str = f"{value:,.2f}"
                    else:
                        value_str = str(value)

                    lines.append(f"| {display_col} | {value_str} |")

                lines.append("")

            lines.append("---")
            lines.append("")

        # Add measures if retrieved
        if data_context['measures']:
            lines.append("### Calculated Measure Values")
            lines.append("")
            lines.append("| Measure | Value |")
            lines.append("|---------|-------|")

            for measure, value in data_context['measures'].items():
                lines.append(f"| {measure} | {value} |")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _update_findings_file(self, data_context_content: str):
        """
        Insert the data context section into the findings file.

        Args:
            data_context_content: Formatted markdown content to insert
        """
        # Read existing findings
        with open(self.findings_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the insertion point (after Problem Statement section)
        # Look for the next ## heading after Problem Statement
        pattern = r'(## Problem Statement.*?)(\n## )'

        if re.search(pattern, content, re.DOTALL):
            # Insert before the next section
            content = re.sub(
                pattern,
                r'\1\n' + data_context_content + r'\2',
                content,
                count=1,
                flags=re.DOTALL
            )
        else:
            # If no next section found, append at the end
            content += "\n" + data_context_content

        # Write updated content
        with open(self.findings_file, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """
    Main entry point when agent is invoked.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Power BI Data Context Agent')
    parser.add_argument('--workspace-url', required=True, help='Power BI workspace XMLA URL')
    parser.add_argument('--dataset-name', required=True, help='Power BI dataset name')
    parser.add_argument('--findings-file', required=True, help='Path to findings markdown file')
    parser.add_argument('--problem-statement', required=True, help='Problem description')

    args = parser.parse_args()

    agent = DataContextAgent(
        workspace_url=args.workspace_url,
        dataset_name=args.dataset_name,
        findings_file=args.findings_file,
        problem_statement=args.problem_statement
    )

    result = agent.run()

    # Exit with appropriate code
    if result['status'] == 'success':
        sys.exit(0)
    elif result['status'] == 'skipped' or result['status'] == 'warning':
        sys.exit(0)  # Not a failure
    elif result['status'] == 'auth_required':
        # Special exit code for auth required (2)
        print("\n" + "=" * 70)
        print("[!] AUTHENTICATION REQUIRED")
        print("=" * 70)
        print("\nThe agent requires user authentication to proceed.")
        print("\nTo authenticate:")
        if 'auth_info' in result and result['auth_info']:
            auth_info = result['auth_info']
            print(f"  1. Open: {auth_info.get('verification_uri', 'https://microsoft.com/devicelogin')}")
            print(f"  2. Enter code: {auth_info.get('user_code', 'N/A')}")
            print(f"  3. Sign in with your Power BI credentials")
            print(f"  4. Re-run this agent after authentication")
        print("\n" + "=" * 70)
        sys.exit(2)  # Exit code 2 = auth required
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
