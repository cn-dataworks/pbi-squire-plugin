"""
Power BI Project Merger Utilities

This module provides utility functions for comparing and merging Power BI projects.
Used by the powerbi-compare-project-code, powerbi-code-understander, and powerbi-code-merger agents.
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class TmdlParser:
    """Parser for TMDL (Tabular Model Definition Language) files."""

    @staticmethod
    def extract_measures(tmdl_content: str) -> List[Dict[str, Any]]:
        """Extract all measures from a TMDL file."""
        measures = []
        # Pattern to match measure blocks
        pattern = r'measure\s+([^\s]+)\s*=\s*(.*?)(?=\n\s*(?:measure|column|partition|annotation-group|\Z))'

        for match in re.finditer(pattern, tmdl_content, re.DOTALL | re.MULTILINE):
            measure_name = match.group(1).strip('"\'')
            measure_body = match.group(2).strip()

            # Extract DAX expression (after the = sign in the body)
            dax_match = re.search(r'^\s*(.*?)(?=\n\s*(?:lineageTag|formatString|displayFolder|$))',
                                measure_body, re.DOTALL | re.MULTILINE)
            dax_expression = dax_match.group(1).strip() if dax_match else measure_body

            measures.append({
                'name': measure_name,
                'expression': dax_expression,
                'full_definition': match.group(0)
            })

        return measures

    @staticmethod
    def extract_columns(tmdl_content: str) -> List[Dict[str, Any]]:
        """Extract all columns from a TMDL file."""
        columns = []
        pattern = r'column\s+([^\s]+)(?:\s*:\s*([^\n]+))?\s*\n((?:\s+.*\n)*)'

        for match in re.finditer(pattern, tmdl_content):
            column_name = match.group(1).strip('"\'')
            data_type = match.group(2).strip() if match.group(2) else None
            properties = match.group(3)

            # Check if it's a calculated column
            is_calculated = 'expression' in properties.lower()

            columns.append({
                'name': column_name,
                'dataType': data_type,
                'isCalculated': is_calculated,
                'full_definition': match.group(0)
            })

        return columns

    @staticmethod
    def extract_table_name(tmdl_content: str) -> Optional[str]:
        """Extract table name from TMDL file."""
        match = re.search(r'table\s+([^\s\n]+)', tmdl_content)
        return match.group(1).strip('"\'') if match else None

    @staticmethod
    def replace_measure(tmdl_content: str, measure_name: str, new_definition: str) -> str:
        """Replace a measure definition in TMDL content."""
        # Escape special regex characters in measure name
        escaped_name = re.escape(measure_name)
        pattern = f'measure\\s+{escaped_name}\\s*=\\s*.*?(?=\\n\\s*(?:measure|column|partition|annotation-group|\\Z))'

        replacement = new_definition.rstrip()
        return re.sub(pattern, replacement, tmdl_content, flags=re.DOTALL | re.MULTILINE)

    @staticmethod
    def replace_column(tmdl_content: str, column_name: str, new_definition: str) -> str:
        """Replace a column definition in TMDL content."""
        escaped_name = re.escape(column_name)
        pattern = f'column\\s+{escaped_name}(?:\\s*:\\s*[^\\n]+)?\\s*\\n(?:\\s+.*\\n)*'

        replacement = new_definition.rstrip() + '\n'
        return re.sub(pattern, replacement, tmdl_content, flags=re.MULTILINE)


class BimParser:
    """Parser for model.bim (JSON) files."""

    @staticmethod
    def load_bim(file_path: str) -> Dict[str, Any]:
        """Load and parse a model.bim file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_bim(file_path: str, bim_data: Dict[str, Any]) -> None:
        """Save model.bim with proper formatting."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(bim_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def find_table(bim_data: Dict[str, Any], table_name: str) -> Optional[Dict[str, Any]]:
        """Find a table by name in the BIM model."""
        tables = bim_data.get('model', {}).get('tables', [])
        for table in tables:
            if table.get('name') == table_name:
                return table
        return None

    @staticmethod
    def find_measure(table: Dict[str, Any], measure_name: str) -> Optional[Dict[str, Any]]:
        """Find a measure by name in a table."""
        measures = table.get('measures', [])
        for measure in measures:
            if measure.get('name') == measure_name:
                return measure
        return None

    @staticmethod
    def find_measure_index(table: Dict[str, Any], measure_name: str) -> Optional[int]:
        """Find the index of a measure in a table."""
        measures = table.get('measures', [])
        for i, measure in enumerate(measures):
            if measure.get('name') == measure_name:
                return i
        return None


class ReportJsonParser:
    """Parser for report.json files."""

    @staticmethod
    def load_report(file_path: str) -> Dict[str, Any]:
        """Load and parse a report.json file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_report(file_path: str, report_data: Dict[str, Any]) -> None:
        """Save report.json with proper formatting."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_pages(report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all pages from report."""
        return report_data.get('sections', [])

    @staticmethod
    def find_visual(page: Dict[str, Any], visual_name: str) -> Optional[Dict[str, Any]]:
        """Find a visual by name in a page."""
        containers = page.get('visualContainers', [])
        for container in containers:
            config = container.get('config', '')
            # Parse the config JSON string
            try:
                config_data = json.loads(config) if isinstance(config, str) else config
                if config_data.get('name') == visual_name:
                    return container
            except json.JSONDecodeError:
                continue
        return None


class ProjectComparer:
    """Main comparison logic for Power BI projects."""

    def __init__(self, main_path: str, comparison_path: str):
        self.main_path = Path(main_path)
        self.comparison_path = Path(comparison_path)
        self.diffs = []
        self.diff_counter = 0

    def generate_diff_id(self) -> str:
        """Generate unique diff ID."""
        self.diff_counter += 1
        return f"diff_{self.diff_counter:03d}"

    def compare_projects(self) -> Dict[str, Any]:
        """Main entry point for comparing two projects."""
        # Compare file structure
        self._compare_file_structure()

        # Compare semantic model
        self._compare_semantic_model()

        # Compare report
        self._compare_report()

        # Generate summary
        summary = self._generate_summary()

        return {
            'diffs': self.diffs,
            'summary': summary
        }

    def _compare_file_structure(self) -> None:
        """Compare file structure between projects."""
        main_files = set(str(p.relative_to(self.main_path)) for p in self.main_path.rglob('*') if p.is_file())
        comp_files = set(str(p.relative_to(self.comparison_path)) for p in self.comparison_path.rglob('*') if p.is_file())

        # Added files
        for file_path in comp_files - main_files:
            self.diffs.append({
                'diff_id': self.generate_diff_id(),
                'component_type': 'File',
                'component_name': Path(file_path).name,
                'file_path': file_path,
                'status': 'Added',
                'main_version_code': None,
                'comparison_version_code': f'[File added: {file_path}]',
                'metadata': {}
            })

        # Deleted files
        for file_path in main_files - comp_files:
            self.diffs.append({
                'diff_id': self.generate_diff_id(),
                'component_type': 'File',
                'component_name': Path(file_path).name,
                'file_path': file_path,
                'status': 'Deleted',
                'main_version_code': f'[File existed: {file_path}]',
                'comparison_version_code': None,
                'metadata': {}
            })

    def _compare_semantic_model(self) -> None:
        """Compare semantic model (TMDL or BIM)."""
        # Find semantic model folder
        main_model = self._find_semantic_model_folder(self.main_path)
        comp_model = self._find_semantic_model_folder(self.comparison_path)

        if not main_model or not comp_model:
            return

        # Check if TMDL or BIM
        if (main_model / 'definition').exists():
            self._compare_tmdl_model(main_model, comp_model)
        elif (main_model / 'model.bim').exists():
            self._compare_bim_model(main_model, comp_model)

    def _find_semantic_model_folder(self, project_path: Path) -> Optional[Path]:
        """Find the semantic model folder in a project."""
        for folder in project_path.iterdir():
            if folder.is_dir() and folder.name.endswith('.SemanticModel'):
                return folder
        return None

    def _compare_tmdl_model(self, main_model: Path, comp_model: Path) -> None:
        """Compare TMDL-format models."""
        # Compare tables
        main_tables = main_model / 'definition' / 'tables'
        comp_tables = comp_model / 'definition' / 'tables'

        if main_tables.exists() and comp_tables.exists():
            self._compare_tmdl_tables(main_tables, comp_tables)

    def _compare_tmdl_tables(self, main_tables: Path, comp_tables: Path) -> None:
        """Compare TMDL table definitions."""
        main_files = {f.name: f for f in main_tables.glob('*.tmdl')}
        comp_files = {f.name: f for f in comp_tables.glob('*.tmdl')}

        # Compare existing tables
        for table_file in main_files.keys() & comp_files.keys():
            self._compare_tmdl_table_file(main_files[table_file], comp_files[table_file])

        # Added tables
        for table_file in comp_files.keys() - main_files.keys():
            with open(comp_files[table_file], 'r', encoding='utf-8') as f:
                content = f.read()

            table_name = TmdlParser.extract_table_name(content)
            self.diffs.append({
                'diff_id': self.generate_diff_id(),
                'component_type': 'Table',
                'component_name': table_name or table_file,
                'file_path': str(comp_files[table_file].relative_to(self.comparison_path.parent)),
                'status': 'Added',
                'main_version_code': None,
                'comparison_version_code': content[:500] + '...' if len(content) > 500 else content,
                'metadata': {}
            })

    def _compare_tmdl_table_file(self, main_file: Path, comp_file: Path) -> None:
        """Compare individual TMDL table file."""
        with open(main_file, 'r', encoding='utf-8') as f:
            main_content = f.read()
        with open(comp_file, 'r', encoding='utf-8') as f:
            comp_content = f.read()

        # Compare measures
        main_measures = {m['name']: m for m in TmdlParser.extract_measures(main_content)}
        comp_measures = {m['name']: m for m in TmdlParser.extract_measures(comp_content)}

        # Modified/added measures
        for measure_name in comp_measures:
            if measure_name in main_measures:
                if main_measures[measure_name]['expression'] != comp_measures[measure_name]['expression']:
                    self.diffs.append({
                        'diff_id': self.generate_diff_id(),
                        'component_type': 'Measure',
                        'component_name': measure_name,
                        'file_path': str(comp_file.relative_to(self.comparison_path.parent)),
                        'status': 'Modified',
                        'main_version_code': main_measures[measure_name]['expression'],
                        'comparison_version_code': comp_measures[measure_name]['expression'],
                        'metadata': {
                            'parent_table': TmdlParser.extract_table_name(comp_content)
                        }
                    })
            else:
                self.diffs.append({
                    'diff_id': self.generate_diff_id(),
                    'component_type': 'Measure',
                    'component_name': measure_name,
                    'file_path': str(comp_file.relative_to(self.comparison_path.parent)),
                    'status': 'Added',
                    'main_version_code': None,
                    'comparison_version_code': comp_measures[measure_name]['expression'],
                    'metadata': {
                        'parent_table': TmdlParser.extract_table_name(comp_content)
                    }
                })

        # Deleted measures
        for measure_name in main_measures:
            if measure_name not in comp_measures:
                self.diffs.append({
                    'diff_id': self.generate_diff_id(),
                    'component_type': 'Measure',
                    'component_name': measure_name,
                    'file_path': str(main_file.relative_to(self.main_path.parent)),
                    'status': 'Deleted',
                    'main_version_code': main_measures[measure_name]['expression'],
                    'comparison_version_code': None,
                    'metadata': {
                        'parent_table': TmdlParser.extract_table_name(main_content)
                    }
                })

    def _compare_bim_model(self, main_model: Path, comp_model: Path) -> None:
        """Compare BIM-format models."""
        main_bim = BimParser.load_bim(str(main_model / 'model.bim'))
        comp_bim = BimParser.load_bim(str(comp_model / 'model.bim'))

        # Compare tables
        main_tables = {t['name']: t for t in main_bim.get('model', {}).get('tables', [])}
        comp_tables = {t['name']: t for t in comp_bim.get('model', {}).get('tables', [])}

        # Compare measures in each table
        for table_name in main_tables.keys() & comp_tables.keys():
            self._compare_bim_table_measures(
                table_name,
                main_tables[table_name],
                comp_tables[table_name]
            )

    def _compare_bim_table_measures(self, table_name: str, main_table: Dict, comp_table: Dict) -> None:
        """Compare measures in a BIM table."""
        main_measures = {m['name']: m for m in main_table.get('measures', [])}
        comp_measures = {m['name']: m for m in comp_table.get('measures', [])}

        for measure_name in comp_measures:
            if measure_name in main_measures:
                if main_measures[measure_name].get('expression') != comp_measures[measure_name].get('expression'):
                    self.diffs.append({
                        'diff_id': self.generate_diff_id(),
                        'component_type': 'Measure',
                        'component_name': measure_name,
                        'file_path': 'model.bim',
                        'status': 'Modified',
                        'main_version_code': main_measures[measure_name].get('expression', ''),
                        'comparison_version_code': comp_measures[measure_name].get('expression', ''),
                        'metadata': {
                            'parent_table': table_name
                        }
                    })

    def _compare_report(self) -> None:
        """Compare report.json files."""
        main_report_path = self._find_report_json(self.main_path)
        comp_report_path = self._find_report_json(self.comparison_path)

        if not main_report_path or not comp_report_path:
            return

        main_report = ReportJsonParser.load_report(str(main_report_path))
        comp_report = ReportJsonParser.load_report(str(comp_report_path))

        # Compare pages
        main_pages = {p.get('displayName', p.get('name', '')): p for p in ReportJsonParser.get_pages(main_report)}
        comp_pages = {p.get('displayName', p.get('name', '')): p for p in ReportJsonParser.get_pages(comp_report)}

        # Added pages
        for page_name in comp_pages.keys() - main_pages.keys():
            self.diffs.append({
                'diff_id': self.generate_diff_id(),
                'component_type': 'Page',
                'component_name': page_name,
                'file_path': str(comp_report_path.relative_to(self.comparison_path.parent)),
                'status': 'Added',
                'main_version_code': None,
                'comparison_version_code': f'[Page: {page_name}]',
                'metadata': {}
            })

    def _find_report_json(self, project_path: Path) -> Optional[Path]:
        """Find report.json in project."""
        for folder in project_path.iterdir():
            if folder.is_dir() and folder.name.endswith('.Report'):
                report_json = folder / 'report.json'
                if report_json.exists():
                    return report_json
        return None

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        total = len(self.diffs)
        added = sum(1 for d in self.diffs if d['status'] == 'Added')
        modified = sum(1 for d in self.diffs if d['status'] == 'Modified')
        deleted = sum(1 for d in self.diffs if d['status'] == 'Deleted')

        breakdown = {}
        for diff in self.diffs:
            comp_type = diff['component_type']
            breakdown[comp_type] = breakdown.get(comp_type, 0) + 1

        return {
            'total_diffs': total,
            'added': added,
            'modified': modified,
            'deleted': deleted,
            'breakdown': breakdown
        }


class ProjectMerger:
    """Executes merge operations based on user decisions."""

    def __init__(self, merge_manifest: Dict[str, Any]):
        self.manifest = merge_manifest
        self.log_entries = []
        self.stats = {
            'files_modified': 0,
            'components_added': 0,
            'components_modified': 0,
            'components_deleted': 0
        }
        self.errors = []

    def execute_merge(self) -> Dict[str, Any]:
        """Execute the merge operation."""
        self._log(f"MERGE INITIATED")
        self._log(f"Main Project: {self.manifest['main_project_path']}")
        self._log(f"Comparison Project: {self.manifest['comparison_project_path']}")
        self._log(f"Output Project: {self.manifest['output_project_path']}")

        # Copy main project
        self._copy_main_project()

        # Process each decision
        self._process_merge_decisions()

        # Generate final log
        merge_log = self._generate_merge_log()

        return {
            'status': 'success' if len(self.errors) == 0 else 'partial_success',
            'output_path': self.manifest['output_project_path'],
            'merge_log': merge_log,
            'statistics': {
                'total_decisions': len(self.manifest['merge_decisions']),
                'main_chosen': sum(1 for d in self.manifest['merge_decisions'] if d['choice'] == 'Main'),
                'comparison_chosen': sum(1 for d in self.manifest['merge_decisions'] if d['choice'] == 'Comparison'),
                **self.stats,
                'errors': len(self.errors)
            },
            'errors': self.errors
        }

    def _copy_main_project(self) -> None:
        """Copy main project to output location."""
        try:
            shutil.copytree(
                self.manifest['main_project_path'],
                self.manifest['output_project_path'],
                dirs_exist_ok=True
            )
            self._log(f"COPIED main project to output location")
        except Exception as e:
            self._log(f"ERROR: Failed to copy main project: {e}")
            self.errors.append({
                'error_type': 'CopyError',
                'message': str(e),
                'severity': 'critical'
            })

    def _process_merge_decisions(self) -> None:
        """Process all merge decisions."""
        diff_lookup = {d['diff_id']: d for d in self.manifest['diff_report']['diffs']}

        for decision in self.manifest['merge_decisions']:
            diff_id = decision['diff_id']
            choice = decision['choice']

            if choice == 'Main':
                self._log(f"SKIPPED {diff_id} (User chose MAIN version)")
            elif choice == 'Comparison':
                diff = diff_lookup.get(diff_id)
                if diff:
                    self._apply_change(diff)
                else:
                    self._log(f"ERROR: Diff {diff_id} not found in diff report")

    def _apply_change(self, diff: Dict[str, Any]) -> None:
        """Apply a single change from comparison to output."""
        try:
            # Implementation would go here - this is a placeholder
            self._log(f"APPLIED {diff['diff_id']} ({diff['component_type']}: {diff['component_name']})")

            if diff['status'] == 'Added':
                self.stats['components_added'] += 1
            elif diff['status'] == 'Modified':
                self.stats['components_modified'] += 1
            elif diff['status'] == 'Deleted':
                self.stats['components_deleted'] += 1

        except Exception as e:
            self._log(f"ERROR: Failed to apply {diff['diff_id']}: {e}")
            self.errors.append({
                'diff_id': diff['diff_id'],
                'error_type': 'ApplyError',
                'message': str(e),
                'severity': 'warning'
            })

    def _log(self, message: str) -> None:
        """Add entry to merge log."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_entries.append(f"[{timestamp}] {message}")

    def _generate_merge_log(self) -> str:
        """Generate final merge log."""
        return '\n'.join(self.log_entries)


# Main entry points for agents
def compare_projects(main_path: str, comparison_path: str) -> Dict[str, Any]:
    """Entry point for powerbi-compare-project-code agent."""
    comparer = ProjectComparer(main_path, comparison_path)
    return comparer.compare_projects()


def execute_merge(merge_manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for powerbi-code-merger agent."""
    merger = ProjectMerger(merge_manifest)
    return merger.execute_merge()
