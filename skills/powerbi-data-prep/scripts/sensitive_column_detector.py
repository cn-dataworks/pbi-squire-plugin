#!/usr/bin/env python3
"""
Sensitive Column Detector for Power BI Projects

Scans TMDL files to identify columns likely to contain sensitive/PII data
based on naming patterns. Used by the setup-data-anonymization workflow.

Usage:
    python sensitive_column_detector.py "<project-path>"
    python sensitive_column_detector.py "<project-path>" --output "<report-file>"
    python sensitive_column_detector.py "<project-path>" --json "<json-file>"
"""

import sys
import os
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import json
from datetime import datetime


@dataclass
class SensitiveColumn:
    """Represents a detected sensitive column."""
    table: str
    column: str
    pattern_category: str  # names, emails, ssn, phones, amounts, addresses, dates, freetext
    confidence: str  # HIGH, MEDIUM, LOW
    data_type: str
    matched_pattern: str
    suggested_masking: str


@dataclass
class DetectionResult:
    """Complete detection results for a project."""
    scan_timestamp: str
    project_path: str
    tables_scanned: int
    columns_scanned: int
    sensitive_columns: List[SensitiveColumn] = field(default_factory=list)


class SensitiveColumnDetector:
    """Detector for sensitive columns in Power BI TMDL files."""

    # Pattern definitions: (regex, category, confidence, suggested_masking)
    COLUMN_PATTERNS = [
        # Names - HIGH confidence
        (r'(?i)^(customer|client|employee|user|person|contact|member)_?name$', 'names', 'HIGH', 'sequential_numbering'),
        (r'(?i)^(first|last|full|given|family|middle)_?name$', 'names', 'HIGH', 'sequential_numbering'),
        (r'(?i)^name$', 'names', 'MEDIUM', 'sequential_numbering'),
        (r'(?i)^(customer|client|employee|user|person)$', 'names', 'MEDIUM', 'sequential_numbering'),

        # Email - HIGH confidence
        (r'(?i)^e?mail(_?address)?$', 'emails', 'HIGH', 'fake_domain'),
        (r'(?i)^(customer|client|user|contact)_?e?mail$', 'emails', 'HIGH', 'fake_domain'),
        (r'(?i)email', 'emails', 'MEDIUM', 'fake_domain'),

        # SSN/Tax ID - HIGH confidence
        (r'(?i)^ssn$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^social_?security(_?number)?$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^tax_?id$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^national_?id$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^(driver_?)?license(_?number)?$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^passport(_?number)?$', 'identifiers', 'HIGH', 'partial_mask'),

        # Phone - HIGH confidence
        (r'(?i)^phone(_?number)?$', 'phones', 'HIGH', 'fake_prefix'),
        (r'(?i)^(mobile|cell|home|work|office)_?(phone|number)?$', 'phones', 'HIGH', 'fake_prefix'),
        (r'(?i)^tel(ephone)?$', 'phones', 'HIGH', 'fake_prefix'),
        (r'(?i)^fax$', 'phones', 'MEDIUM', 'fake_prefix'),

        # Addresses - MEDIUM confidence
        (r'(?i)^(street|home|mailing|billing|shipping)_?address$', 'addresses', 'HIGH', 'generic_format'),
        (r'(?i)^address(_?line)?[_\d]*$', 'addresses', 'HIGH', 'generic_format'),
        (r'(?i)^(city|town|municipality)$', 'addresses', 'MEDIUM', 'generic_format'),
        (r'(?i)^(state|province|region)$', 'addresses', 'MEDIUM', 'generic_format'),
        (r'(?i)^(zip|postal)_?(code)?$', 'addresses', 'MEDIUM', 'generic_format'),
        (r'(?i)^country$', 'addresses', 'LOW', 'generic_format'),

        # Financial - MEDIUM confidence
        (r'(?i)^(salary|wage|income|compensation)$', 'amounts', 'HIGH', 'scale_factor'),
        (r'(?i)^(account|card)_?number$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^(credit|debit)_?card$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^bank_?account$', 'identifiers', 'HIGH', 'partial_mask'),
        (r'(?i)^(price|cost|amount|total|balance|payment)$', 'amounts', 'MEDIUM', 'scale_factor'),
        (r'(?i)^(revenue|profit|margin)$', 'amounts', 'MEDIUM', 'scale_factor'),

        # Dates - MEDIUM confidence (DOB is sensitive)
        (r'(?i)^(date_?of_?birth|dob|birth_?date)$', 'dates', 'HIGH', 'date_offset'),
        (r'(?i)^(hire|start|end|termination)_?date$', 'dates', 'MEDIUM', 'date_offset'),

        # Free text - LOW confidence
        (r'(?i)^(notes?|comments?|description|remarks?)$', 'freetext', 'LOW', 'placeholder_text'),
        (r'(?i)^(feedback|review|message)$', 'freetext', 'LOW', 'placeholder_text'),
    ]

    # Masking strategy descriptions
    MASKING_STRATEGIES = {
        'sequential_numbering': 'Replace with "Customer 1", "Customer 2", etc.',
        'fake_domain': 'Replace with user123@example.com format',
        'partial_mask': 'Show only last 4 characters (XXX-XX-1234)',
        'fake_prefix': 'Replace with (555) 555-XXXX format',
        'generic_format': 'Replace with generic "123 Main St, City, ST" format',
        'scale_factor': 'Multiply by random factor (0.8-1.2) to preserve distribution',
        'date_offset': 'Shift by random number of days (+/- 30)',
        'placeholder_text': 'Replace with "[REDACTED]" or generic text',
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.tmdl_files = list(self.project_path.rglob('*.tmdl'))

        if not self.tmdl_files:
            raise ValueError(f"No TMDL files found in {project_path}")

        self.tables = {}  # table_name -> list of columns
        self.result = DetectionResult(
            scan_timestamp=datetime.now().isoformat(),
            project_path=str(project_path),
            tables_scanned=0,
            columns_scanned=0
        )

    def scan(self) -> DetectionResult:
        """Run full scan and return detection results."""
        print(f"Scanning {len(self.tmdl_files)} TMDL files...\n")

        # Extract tables and columns
        for tmdl_file in self.tmdl_files:
            self._extract_columns(tmdl_file)

        self.result.tables_scanned = len(self.tables)
        self.result.columns_scanned = sum(len(cols) for cols in self.tables.values())

        print(f"Found {self.result.tables_scanned} tables with {self.result.columns_scanned} columns\n")

        # Detect sensitive columns
        for table_name, columns in self.tables.items():
            for column in columns:
                sensitive = self._check_column(table_name, column)
                if sensitive:
                    self.result.sensitive_columns.append(sensitive)

        return self.result

    def _extract_columns(self, tmdl_file: Path):
        """Extract table and column definitions from TMDL file."""
        content = tmdl_file.read_text(encoding='utf-8')
        lines = content.splitlines()

        current_table = None

        for line in lines:
            # Find table declaration
            table_match = re.match(r'^table\s+([\'"]?)(\w+)\1\s*$', line)
            if table_match:
                current_table = table_match.group(2)
                if current_table not in self.tables:
                    self.tables[current_table] = []
                continue

            if current_table:
                # Find column declarations
                # Format: column ColumnName or column 'Column Name'
                col_match = re.match(r'^\s*column\s+([\'"]?)([^\s\'\"]+)\1', line)
                if col_match:
                    column_name = col_match.group(2)
                    # Extract data type if present
                    data_type = 'unknown'
                    type_match = re.search(r'dataType:\s*(\w+)', line)
                    if type_match:
                        data_type = type_match.group(1)

                    self.tables[current_table].append({
                        'name': column_name,
                        'data_type': data_type
                    })

    def _check_column(self, table_name: str, column: Dict) -> Optional[SensitiveColumn]:
        """Check if a column matches any sensitive pattern."""
        column_name = column['name']
        data_type = column.get('data_type', 'unknown')

        for pattern, category, confidence, masking in self.COLUMN_PATTERNS:
            if re.match(pattern, column_name):
                return SensitiveColumn(
                    table=table_name,
                    column=column_name,
                    pattern_category=category,
                    confidence=confidence,
                    data_type=data_type,
                    matched_pattern=pattern,
                    suggested_masking=masking
                )

        return None

    def generate_report(self) -> str:
        """Generate human-readable detection report."""
        report = []
        report.append("=" * 80)
        report.append("SENSITIVE COLUMN DETECTION REPORT")
        report.append("=" * 80)
        report.append(f"Project: {self.result.project_path}")
        report.append(f"Scan Time: {self.result.scan_timestamp}")
        report.append(f"Tables Scanned: {self.result.tables_scanned}")
        report.append(f"Columns Scanned: {self.result.columns_scanned}")
        report.append("")

        if not self.result.sensitive_columns:
            report.append("No sensitive columns detected based on naming patterns.")
            report.append("")
            report.append("Note: This analysis is based on column names only.")
            report.append("You may still have sensitive data in columns with non-standard names.")
            report.append("")
            return '\n'.join(report)

        # Group by confidence
        high = [c for c in self.result.sensitive_columns if c.confidence == 'HIGH']
        medium = [c for c in self.result.sensitive_columns if c.confidence == 'MEDIUM']
        low = [c for c in self.result.sensitive_columns if c.confidence == 'LOW']

        report.append(f"SENSITIVE COLUMNS FOUND: {len(self.result.sensitive_columns)}")
        report.append(f"  - High Confidence: {len(high)}")
        report.append(f"  - Medium Confidence: {len(medium)}")
        report.append(f"  - Low Confidence: {len(low)}")
        report.append("")

        # High confidence findings
        if high:
            report.append("=" * 80)
            report.append("HIGH CONFIDENCE - Likely Sensitive")
            report.append("=" * 80)
            report.append("")
            for col in high:
                report.append(f"  {col.table}.{col.column}")
                report.append(f"    Category: {col.pattern_category}")
                report.append(f"    Suggested Masking: {self.MASKING_STRATEGIES.get(col.suggested_masking, col.suggested_masking)}")
                report.append("")

        # Medium confidence findings
        if medium:
            report.append("=" * 80)
            report.append("MEDIUM CONFIDENCE - Possibly Sensitive")
            report.append("=" * 80)
            report.append("")
            for col in medium:
                report.append(f"  {col.table}.{col.column}")
                report.append(f"    Category: {col.pattern_category}")
                report.append(f"    Suggested Masking: {self.MASKING_STRATEGIES.get(col.suggested_masking, col.suggested_masking)}")
                report.append("")

        # Low confidence findings
        if low:
            report.append("=" * 80)
            report.append("LOW CONFIDENCE - Review Recommended")
            report.append("=" * 80)
            report.append("")
            for col in low:
                report.append(f"  {col.table}.{col.column}")
                report.append(f"    Category: {col.pattern_category}")
                report.append(f"    Suggested Masking: {self.MASKING_STRATEGIES.get(col.suggested_masking, col.suggested_masking)}")
                report.append("")

        # Summary by table
        report.append("=" * 80)
        report.append("SUMMARY BY TABLE")
        report.append("=" * 80)
        report.append("")

        by_table = defaultdict(list)
        for col in self.result.sensitive_columns:
            by_table[col.table].append(col)

        for table, columns in sorted(by_table.items()):
            report.append(f"  {table}: {len(columns)} sensitive column(s)")
            for col in columns:
                report.append(f"    - {col.column} ({col.pattern_category}, {col.confidence})")
            report.append("")

        report.append("=" * 80)
        report.append("NEXT STEPS")
        report.append("=" * 80)
        report.append("")
        report.append("1. Review the detected columns and confirm which need masking")
        report.append("2. Run: /setup-data-anonymization to generate masking M code")
        report.append("3. The workflow will create a DataMode parameter for toggling")
        report.append("4. Switch to 'Anonymized' mode before using MCP on sensitive data")
        report.append("")
        report.append("=" * 80)

        return '\n'.join(report)

    def to_json(self) -> Dict:
        """Convert results to JSON-serializable dict."""
        return {
            'scan_timestamp': self.result.scan_timestamp,
            'project_path': self.result.project_path,
            'tables_scanned': self.result.tables_scanned,
            'columns_scanned': self.result.columns_scanned,
            'sensitive_columns': [
                {
                    'table': col.table,
                    'column': col.column,
                    'pattern_category': col.pattern_category,
                    'confidence': col.confidence,
                    'data_type': col.data_type,
                    'suggested_masking': col.suggested_masking
                }
                for col in self.result.sensitive_columns
            ],
            'masking_strategies': self.MASKING_STRATEGIES
        }


def main():
    parser = argparse.ArgumentParser(
        description='Detect sensitive columns in Power BI TMDL files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('project_path', help='Path to Power BI project folder (contains .SemanticModel)')
    parser.add_argument('--output', help='Output file for report (default: stdout)')
    parser.add_argument('--json', help='Output JSON file for structured data')
    parser.add_argument('--confidence', choices=['HIGH', 'MEDIUM', 'LOW'],
                        help='Minimum confidence level to include (default: all)')

    args = parser.parse_args()

    try:
        # Initialize detector
        detector = SensitiveColumnDetector(args.project_path)

        # Run scan
        result = detector.scan()

        # Filter by confidence if specified
        if args.confidence:
            confidence_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            min_conf = confidence_order[args.confidence]
            result.sensitive_columns = [
                c for c in result.sensitive_columns
                if confidence_order.get(c.confidence, 0) >= min_conf
            ]

        # Generate report
        report = detector.generate_report()

        # Output report
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"Report saved to: {args.output}")
        else:
            print(report)

        # Output JSON if requested
        if args.json:
            json_data = detector.to_json()
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            print(f"JSON data saved to: {args.json}")

        # Exit code: 0 if no high-confidence issues, 1 if has high-confidence
        high_conf = [c for c in result.sensitive_columns if c.confidence == 'HIGH']
        return 1 if high_conf else 0

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
