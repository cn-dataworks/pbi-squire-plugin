"""
Example test script for Power BI Data Context Agent

This demonstrates how to use the agent in a standalone manner.
"""

import sys
from pathlib import Path

# Add agent to path
agent_path = Path(__file__).parent
sys.path.insert(0, str(agent_path))

from agent import DataContextAgent


def create_test_findings_file():
    """Create a mock findings file for testing."""
    findings_content = """# Analysis: Invoice Commission Calculation Issue

**Created**: 2025-10-13 18:00:00
**Project**: C:\\Projects\\Commissions.Report
**Status**: In Progress

---

## Problem Statement

Invoice P3495801 shows a commission of $50 but should be $92.25 based on the
commission rate and invoice amount. The commission calculation appears to be
incorrect for this rental invoice.

**Key Objects Identified**:
- Invoice: P3495801
- Table: FACT_RENTAL_INVOICE_DETAIL_RSR
- Measure: Total Commission

**Project File Locations**:
- Semantic Model: `C:\\Projects\\Commissions.Report\\.SemanticModel/`
- TMDL Definitions: `C:\\Projects\\Commissions.Report\\.SemanticModel\\definition/`

---

## Section 1: Current Implementation Investigation

[To be populated by powerbi-code-locator agent]

## Section 2: Proposed Changes

[To be populated by powerbi-code-fix-identifier agent]

## Section 3: Test Cases and Impact Analysis

[To be populated by power-bi-verification agent]
"""

    test_file = Path(__file__).parent / "test_findings.md"
    test_file.write_text(findings_content, encoding='utf-8')
    return str(test_file)


def main():
    """Run example test of the agent."""

    print("=" * 70)
    print("Power BI Data Context Agent - Example Test")
    print("=" * 70)
    print()

    # Create test findings file
    print("[Setup] Creating test findings file...")
    findings_file = create_test_findings_file()
    print(f"   Created: {findings_file}")
    print()

    # Initialize agent with test parameters
    agent = DataContextAgent(
        workspace_url="powerbi://api.powerbi.com/v1.0/myorg/Weisiger%20Commissions",
        dataset_name="RSR Commissions Pre Prod v3",
        findings_file=findings_file,
        problem_statement="Invoice P3495801 shows commission of $50 but should be $92.25"
    )

    # Run the agent
    print("[Execution] Running agent...")
    print()

    result = agent.run()

    print()
    print("=" * 70)
    print("Test Result")
    print("=" * 70)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

    if result['data']:
        print(f"Records Retrieved: {len(result['data']['records'])}")
        print(f"Measures Calculated: {len(result['data']['measures'])}")

    print()
    print(f"Check the findings file for data context:")
    print(f"  {findings_file}")
    print()


if __name__ == '__main__':
    main()
