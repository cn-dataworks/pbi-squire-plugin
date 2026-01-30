#!/usr/bin/env python3
"""
Anonymization M Code Generator

Generates conditional masking M code for Power BI partitions based on
detected sensitive columns. Creates backup of original files before modification.

Usage:
    python anonymization_generator.py "<project-path>" --columns "<detection-json>"
    python anonymization_generator.py "<project-path>" --columns "<detection-json>" --preview
    python anonymization_generator.py "<project-path>" --columns "<detection-json>" --apply
"""

import sys
import os
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import shutil


@dataclass
class MaskingTemplate:
    """Template for a masking operation."""
    category: str
    m_code_snippet: str
    requires_index: bool
    data_type: str


class AnonymizationGenerator:
    """Generates M code for data anonymization."""

    # M code templates for each masking strategy
    MASKING_TEMPLATES = {
        'sequential_numbering': MaskingTemplate(
            category='names',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                "{prefix} " & Text.From([_MaskIndex])
            else
                [{column}],
            type text
        }}''',
            requires_index=True,
            data_type='text'
        ),

        'fake_domain': MaskingTemplate(
            category='emails',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                "user" & Text.From([_MaskIndex]) & "@example.com"
            else
                [{column}],
            type text
        }}''',
            requires_index=True,
            data_type='text'
        ),

        'partial_mask': MaskingTemplate(
            category='identifiers',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                "XXX-XX-" & Text.End(Text.From([{column}]), 4)
            else
                [{column}],
            type text
        }}''',
            requires_index=False,
            data_type='text'
        ),

        'fake_prefix': MaskingTemplate(
            category='phones',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                "(555) 555-" & Text.End(Text.Replace(Text.From([{column}]), "-", ""), 4)
            else
                [{column}],
            type text
        }}''',
            requires_index=False,
            data_type='text'
        ),

        'generic_format': MaskingTemplate(
            category='addresses',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                Text.From([_MaskIndex]) & " Main Street, Anytown, ST 00000"
            else
                [{column}],
            type text
        }}''',
            requires_index=True,
            data_type='text'
        ),

        'scale_factor': MaskingTemplate(
            category='amounts',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                Number.Round([{column}] * (0.8 + Number.Random() * 0.4), 2)
            else
                [{column}],
            type number
        }}''',
            requires_index=False,
            data_type='number'
        ),

        'date_offset': MaskingTemplate(
            category='dates',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                Date.AddDays([{column}], Number.RoundDown(Number.Random() * 60) - 30)
            else
                [{column}],
            type date
        }}''',
            requires_index=False,
            data_type='date'
        ),

        'placeholder_text': MaskingTemplate(
            category='freetext',
            m_code_snippet='''{{"{column}", each
            if #"DataMode" = "Anonymized" then
                "[Content redacted for privacy]"
            else
                [{column}],
            type text
        }}''',
            requires_index=False,
            data_type='text'
        ),
    }

    # Prefix mappings for sequential numbering
    COLUMN_PREFIXES = {
        'customername': 'Customer',
        'customer': 'Customer',
        'clientname': 'Client',
        'client': 'Client',
        'employeename': 'Employee',
        'employee': 'Employee',
        'username': 'User',
        'user': 'User',
        'personname': 'Person',
        'person': 'Person',
        'contactname': 'Contact',
        'contact': 'Contact',
        'membername': 'Member',
        'member': 'Member',
        'firstname': 'Person',
        'lastname': 'Person',
        'fullname': 'Person',
        'name': 'Entity',
    }

    def __init__(self, project_path: str, columns_json: str):
        self.project_path = Path(project_path)
        self.tmdl_files = list(self.project_path.rglob('*.tmdl'))

        # Load column detection results
        with open(columns_json, 'r', encoding='utf-8') as f:
            self.detection_data = json.load(f)

        self.sensitive_columns = self.detection_data.get('sensitive_columns', [])

        # Group columns by table
        self.columns_by_table = {}
        for col in self.sensitive_columns:
            table = col['table']
            if table not in self.columns_by_table:
                self.columns_by_table[table] = []
            self.columns_by_table[table].append(col)

        self.generated_code = {}
        self.backup_dir = self.project_path / '.anonymization' / 'backups'

    def generate(self) -> Dict[str, str]:
        """Generate M code for all tables with sensitive columns."""
        print(f"Generating anonymization M code for {len(self.columns_by_table)} tables...\n")

        for table_name, columns in self.columns_by_table.items():
            m_code = self._generate_table_code(table_name, columns)
            self.generated_code[table_name] = m_code

        return self.generated_code

    def _generate_table_code(self, table_name: str, columns: List[Dict]) -> str:
        """Generate M code for a single table."""
        # Check if any column requires index
        requires_index = any(
            self.MASKING_TEMPLATES.get(col['suggested_masking'], MaskingTemplate('', '', False, '')).requires_index
            for col in columns
        )

        # Build transformation snippets
        transformations = []
        for col in columns:
            masking = col['suggested_masking']
            template = self.MASKING_TEMPLATES.get(masking)

            if template:
                snippet = template.m_code_snippet.format(
                    column=col['column'],
                    prefix=self._get_prefix(col['column'])
                )
                transformations.append(snippet)

        if not transformations:
            return ""

        # Combine into complete M code block
        transform_list = ',\n        '.join(transformations)

        if requires_index:
            m_code = f'''// Anonymization for {table_name}
// Generated by anonymization_generator.py

let
    Source = {{PREVIOUS_STEP}},

    // Add index for sequential numbering
    IndexedData = Table.AddIndexColumn(Source, "_MaskIndex", 1, 1, Int64.Type),

    // Apply conditional masking based on DataMode parameter
    MaskedData = Table.TransformColumns(IndexedData, {{
        {transform_list}
    }}),

    // Remove index column
    Result = Table.RemoveColumns(MaskedData, {{"_MaskIndex"}})
in
    Result'''
        else:
            m_code = f'''// Anonymization for {table_name}
// Generated by anonymization_generator.py

let
    Source = {{PREVIOUS_STEP}},

    // Apply conditional masking based on DataMode parameter
    MaskedData = Table.TransformColumns(Source, {{
        {transform_list}
    }})
in
    MaskedData'''

        return m_code

    def _get_prefix(self, column_name: str) -> str:
        """Get appropriate prefix for sequential numbering."""
        col_lower = column_name.lower().replace('_', '')
        return self.COLUMN_PREFIXES.get(col_lower, 'Item')

    def create_backup(self):
        """Create backup of original TMDL files."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_subdir = self.backup_dir / timestamp

        print(f"Creating backup in {backup_subdir}...")

        for tmdl_file in self.tmdl_files:
            # Preserve relative path structure
            rel_path = tmdl_file.relative_to(self.project_path)
            backup_path = backup_subdir / rel_path

            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tmdl_file, backup_path)

        print(f"Backup complete: {len(self.tmdl_files)} files backed up\n")
        return backup_subdir

    def generate_datamode_parameter(self) -> str:
        """Generate M code for DataMode parameter."""
        return '''"Real" meta [
    IsParameterQuery = true,
    Type = "Text",
    IsParameterQueryRequired = true,
    AllowedValues = {"Real", "Anonymized"}
]'''

    def generate_config(self) -> Dict:
        """Generate configuration file content."""
        return {
            'status': 'configured',
            'setup_timestamp': datetime.now().isoformat(),
            'datamode_parameter': 'DataMode',
            'tables': [
                {
                    'name': table,
                    'columns_masked': [col['column'] for col in columns],
                    'masking_strategies': {col['column']: col['suggested_masking'] for col in columns}
                }
                for table, columns in self.columns_by_table.items()
            ],
            'backups_dir': str(self.backup_dir)
        }

    def preview(self) -> str:
        """Generate preview report of what will be changed."""
        report = []
        report.append("=" * 80)
        report.append("ANONYMIZATION PREVIEW")
        report.append("=" * 80)
        report.append(f"Project: {self.project_path}")
        report.append(f"Tables to modify: {len(self.columns_by_table)}")
        report.append("")

        for table_name, columns in self.columns_by_table.items():
            report.append("-" * 80)
            report.append(f"TABLE: {table_name}")
            report.append("-" * 80)
            report.append("")
            report.append("Columns to mask:")
            for col in columns:
                report.append(f"  - {col['column']}: {col['suggested_masking']}")
            report.append("")
            report.append("Generated M code:")
            report.append("")
            report.append(self.generated_code.get(table_name, 'No code generated'))
            report.append("")

        report.append("=" * 80)
        report.append("DATAMODE PARAMETER")
        report.append("=" * 80)
        report.append("")
        report.append("Add this named expression to your model:")
        report.append("")
        report.append(self.generate_datamode_parameter())
        report.append("")

        report.append("=" * 80)
        report.append("NEXT STEPS")
        report.append("=" * 80)
        report.append("")
        report.append("1. Review the generated M code above")
        report.append("2. Run with --apply to modify TMDL files")
        report.append("3. Add the DataMode parameter to your model")
        report.append("4. Open in Power BI Desktop and test both modes")
        report.append("")

        return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Generate anonymization M code for Power BI projects',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('project_path', help='Path to Power BI project folder')
    parser.add_argument('--columns', required=True, help='JSON file with detected sensitive columns')
    parser.add_argument('--preview', action='store_true', help='Preview changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply changes to TMDL files')
    parser.add_argument('--output', help='Output directory for generated M code files')

    args = parser.parse_args()

    try:
        # Initialize generator
        generator = AnonymizationGenerator(args.project_path, args.columns)

        # Generate M code
        generated = generator.generate()

        if args.preview or (not args.apply):
            # Show preview
            preview = generator.preview()
            print(preview)

        if args.output:
            # Save generated code to files
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            for table_name, m_code in generated.items():
                output_file = output_dir / f"{table_name}_anonymization.m"
                output_file.write_text(m_code, encoding='utf-8')
                print(f"Saved: {output_file}")

            # Save config
            config = generator.generate_config()
            config_file = output_dir / 'anonymization_config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"Saved: {config_file}")

            # Save DataMode parameter
            param_file = output_dir / 'DataMode_parameter.m'
            param_file.write_text(generator.generate_datamode_parameter(), encoding='utf-8')
            print(f"Saved: {param_file}")

        if args.apply:
            print("\n" + "=" * 80)
            print("APPLYING CHANGES")
            print("=" * 80)

            # Create backup first
            backup_dir = generator.create_backup()

            # Note: Actual TMDL modification would require parsing and
            # inserting the M code into the correct partition location.
            # This is a complex operation that should be done carefully.
            print("Note: Automatic TMDL modification not yet implemented.")
            print("Please manually integrate the generated M code into your partitions.")
            print(f"\nGenerated M code files saved to: {args.output or 'use --output to save'}")
            print(f"Backup created at: {backup_dir}")

            # Save config to project
            config_dir = Path(args.project_path) / '.anonymization'
            config_dir.mkdir(parents=True, exist_ok=True)

            config = generator.generate_config()
            config_file = config_dir / 'config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"Config saved to: {config_file}")

        return 0

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
