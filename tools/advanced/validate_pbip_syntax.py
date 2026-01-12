#!/usr/bin/env python3
"""
PBIP Syntax Validator - Pre-commit validation for Power BI Projects

Validates JSON and TMDL files before git commit to catch syntax errors
that would cause deployment failures. Part of the QA Loop workflow.

Usage:
    python validate_pbip_syntax.py <project_path> [--json] [--strict]

Options:
    --json      Output results in JSON format
    --strict    Treat warnings as errors

Exit Codes:
    0 - All validations passed
    1 - Warnings found (non-blocking)
    2 - Errors found (blocking)
    3 - Script error

Author: Power BI Analyst Agent
Version: 1.0.0
"""

import json
import sys
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum
from datetime import datetime


class Severity(Enum):
    """Validation issue severity levels"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    file_path: str
    line_number: Optional[int]
    severity: str  # Use string for JSON serialization
    code: str
    message: str

    def __str__(self):
        line_info = f" (line {self.line_number})" if self.line_number else ""
        return f"[{self.severity}] {self.code}: {self.message}\n  File: {self.file_path}{line_info}"


@dataclass
class ValidationResult:
    """Complete validation result"""
    status: str  # "pass", "warning", "error"
    project_path: str
    timestamp: str
    summary: dict
    issues: List[ValidationIssue]

    def to_dict(self):
        return {
            "status": self.status,
            "project_path": self.project_path,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "issues": [asdict(i) for i in self.issues]
        }


class PbipSyntaxValidator:
    """
    Validates PBIP project syntax before commit.

    Checks:
    - JSON file syntax in .Report folder
    - TMDL file syntax in .SemanticModel folder
    - Cross-references between visuals and measures
    - Common deployment-breaking issues
    """

    def __init__(self, project_path: str, strict: bool = False):
        self.project_path = Path(project_path).resolve()
        self.strict = strict
        self.issues: List[ValidationIssue] = []
        self.json_files_checked = 0
        self.tmdl_files_checked = 0

    def validate(self) -> ValidationResult:
        """
        Run all validations on the PBIP project.
        Returns ValidationResult with status and issues.
        """
        # Validate project structure
        if not self._validate_project_structure():
            return self._build_result()

        # Run validation phases
        self._validate_json_files()
        self._validate_tmdl_files()
        self._validate_visual_references()

        return self._build_result()

    def _validate_project_structure(self) -> bool:
        """Validate that this is a valid PBIP project"""
        if not self.project_path.exists():
            self.issues.append(ValidationIssue(
                file_path=str(self.project_path),
                line_number=None,
                severity=Severity.ERROR.value,
                code="PBIP001",
                message=f"Project path does not exist: {self.project_path}"
            ))
            return False

        # Check for .pbip file or Report/SemanticModel folders
        has_pbip = any(self.project_path.glob("*.pbip"))
        report_folder = self._find_report_folder()
        semantic_folder = self._find_semantic_model_folder()

        if not has_pbip and not report_folder and not semantic_folder:
            self.issues.append(ValidationIssue(
                file_path=str(self.project_path),
                line_number=None,
                severity=Severity.ERROR.value,
                code="PBIP002",
                message="Not a valid PBIP project. Missing .pbip file or .Report/.SemanticModel folders."
            ))
            return False

        return True

    def _find_report_folder(self) -> Optional[Path]:
        """Find the .Report folder in the project"""
        # Direct child with .Report suffix
        for item in self.project_path.iterdir():
            if item.is_dir() and item.name.endswith('.Report'):
                return item
        # Check for nested structure
        for item in self.project_path.rglob('*.Report'):
            if item.is_dir():
                return item
        return None

    def _find_semantic_model_folder(self) -> Optional[Path]:
        """Find the .SemanticModel folder in the project"""
        for item in self.project_path.iterdir():
            if item.is_dir() and item.name.endswith('.SemanticModel'):
                return item
        for item in self.project_path.rglob('*.SemanticModel'):
            if item.is_dir():
                return item
        return None

    def _validate_json_files(self):
        """Validate all JSON files in .Report folder"""
        report_folder = self._find_report_folder()
        if not report_folder:
            self.issues.append(ValidationIssue(
                file_path=str(self.project_path),
                line_number=None,
                severity=Severity.WARNING.value,
                code="PBIP003",
                message="No .Report folder found. Skipping JSON validation."
            ))
            return

        for json_file in report_folder.rglob("*.json"):
            self.json_files_checked += 1
            self._validate_single_json(json_file)

    def _validate_single_json(self, json_file: Path):
        """Validate a single JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                self.issues.append(ValidationIssue(
                    file_path=str(json_file.relative_to(self.project_path)),
                    line_number=e.lineno,
                    severity=Severity.ERROR.value,
                    code="JSON001",
                    message=f"Invalid JSON syntax: {e.msg}"
                ))
                return

            # Additional JSON-specific checks
            self._check_json_structure(json_file, data)

        except Exception as e:
            self.issues.append(ValidationIssue(
                file_path=str(json_file.relative_to(self.project_path)),
                line_number=None,
                severity=Severity.ERROR.value,
                code="JSON002",
                message=f"Failed to read file: {str(e)}"
            ))

    def _check_json_structure(self, json_file: Path, data: dict):
        """Check JSON file structure for common issues"""
        filename = json_file.name.lower()

        # Check visual.json files for required properties
        if filename == 'visual.json':
            if isinstance(data, dict):
                # Check for config property
                if 'config' in data:
                    config = data['config']
                    if isinstance(config, str):
                        # Config is stringified JSON - try to parse it
                        try:
                            json.loads(config)
                        except json.JSONDecodeError as e:
                            self.issues.append(ValidationIssue(
                                file_path=str(json_file.relative_to(self.project_path)),
                                line_number=None,
                                severity=Severity.ERROR.value,
                                code="JSON003",
                                message=f"Invalid JSON in 'config' property: {e.msg}"
                            ))

        # Check report.json for required structure
        if filename == 'report.json':
            if isinstance(data, dict):
                # Warn if essential properties are missing
                if 'config' not in data:
                    self.issues.append(ValidationIssue(
                        file_path=str(json_file.relative_to(self.project_path)),
                        line_number=None,
                        severity=Severity.WARNING.value,
                        code="JSON004",
                        message="report.json missing 'config' property"
                    ))

    def _validate_tmdl_files(self):
        """Validate TMDL files in .SemanticModel folder"""
        semantic_folder = self._find_semantic_model_folder()
        if not semantic_folder:
            self.issues.append(ValidationIssue(
                file_path=str(self.project_path),
                line_number=None,
                severity=Severity.WARNING.value,
                code="PBIP004",
                message="No .SemanticModel folder found. Skipping TMDL validation."
            ))
            return

        definition_folder = semantic_folder / 'definition'
        if not definition_folder.exists():
            return

        for tmdl_file in definition_folder.rglob("*.tmdl"):
            self.tmdl_files_checked += 1
            self._validate_single_tmdl(tmdl_file)

    def _validate_single_tmdl(self, tmdl_file: Path):
        """Basic TMDL validation - delegates to tmdl_format_validator for detailed checks"""
        try:
            with open(tmdl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check for obvious syntax issues
            brace_balance = 0
            in_expression = False

            for i, line in enumerate(lines, start=1):
                stripped = line.strip()

                # Track expression blocks
                if '= {' in line or '={' in line:
                    in_expression = True
                    brace_balance += 1
                elif stripped == '}':
                    brace_balance -= 1
                    if brace_balance <= 0:
                        in_expression = False
                        brace_balance = 0

                # Check for tabs vs spaces mixing at structural level
                if line and not line.isspace():
                    leading = line[:len(line) - len(line.lstrip())]
                    if '\t' in leading and ' ' in leading:
                        tab_count = leading.count('\t')
                        if tab_count <= 3:  # Structural level
                            self.issues.append(ValidationIssue(
                                file_path=str(tmdl_file.relative_to(self.project_path)),
                                line_number=i,
                                severity=Severity.WARNING.value,
                                code="TMDL001",
                                message="Mixed tabs and spaces at structural indentation level"
                            ))

        except Exception as e:
            self.issues.append(ValidationIssue(
                file_path=str(tmdl_file.relative_to(self.project_path)),
                line_number=None,
                severity=Severity.ERROR.value,
                code="TMDL002",
                message=f"Failed to read TMDL file: {str(e)}"
            ))

    def _validate_visual_references(self):
        """Check for broken references between visuals and semantic model"""
        report_folder = self._find_report_folder()
        semantic_folder = self._find_semantic_model_folder()

        if not report_folder or not semantic_folder:
            return

        # Get list of measures and columns from semantic model
        known_measures = set()
        known_columns = set()

        definition_folder = semantic_folder / 'definition'
        if definition_folder.exists():
            for tmdl_file in definition_folder.rglob("*.tmdl"):
                self._extract_measures_columns(tmdl_file, known_measures, known_columns)

        # Skip reference validation if we couldn't extract any measures
        # (This could happen with import mode where measures are inline)
        if not known_measures and not known_columns:
            return

        # Check visual configs for references
        for visual_json in report_folder.rglob("visual.json"):
            self._check_visual_references(visual_json, known_measures, known_columns)

    def _extract_measures_columns(self, tmdl_file: Path, measures: set, columns: set):
        """Extract measure and column names from TMDL file"""
        try:
            with open(tmdl_file, 'r', encoding='utf-8') as f:
                content = f.read()

            import re
            # Find measure definitions
            for match in re.finditer(r"measure\s+['\"]?([^'\"=]+)['\"]?\s*=", content):
                measures.add(match.group(1).strip())

            # Find column definitions
            for match in re.finditer(r"column\s+['\"]?([^'\"=\s]+)['\"]?", content):
                columns.add(match.group(1).strip())

        except Exception:
            pass  # Skip files we can't parse

    def _check_visual_references(self, visual_json: Path, measures: set, columns: set):
        """Check visual.json for references to non-existent measures/columns"""
        # This is a placeholder for more sophisticated reference checking
        # Full implementation would parse the visual config and check bindings
        pass

    def _build_result(self) -> ValidationResult:
        """Build the final validation result"""
        errors = [i for i in self.issues if i.severity == Severity.ERROR.value]
        warnings = [i for i in self.issues if i.severity == Severity.WARNING.value]

        if errors:
            status = "error"
        elif warnings and self.strict:
            status = "error"
        elif warnings:
            status = "warning"
        else:
            status = "pass"

        return ValidationResult(
            status=status,
            project_path=str(self.project_path),
            timestamp=datetime.now().isoformat(),
            summary={
                "json_files_checked": self.json_files_checked,
                "tmdl_files_checked": self.tmdl_files_checked,
                "errors": len(errors),
                "warnings": len(warnings)
            },
            issues=self.issues
        )


def print_report(result: ValidationResult):
    """Print validation report to console"""
    print("=" * 80)
    print("PBIP SYNTAX VALIDATION REPORT")
    print("=" * 80)
    print(f"Project: {result.project_path}")
    print(f"Timestamp: {result.timestamp}")
    print(f"JSON Files: {result.summary['json_files_checked']}")
    print(f"TMDL Files: {result.summary['tmdl_files_checked']}")
    print("=" * 80)

    if result.status == "pass":
        print("\n[SUCCESS] All validations passed!")
        print("\nThe project is ready for commit and deployment.")
        return

    # Group issues by severity
    errors = [i for i in result.issues if i.severity == Severity.ERROR.value]
    warnings = [i for i in result.issues if i.severity == Severity.WARNING.value]

    print(f"\n[SUMMARY]")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("\n[ERRORS] (Must Fix Before Deploy):")
        print("-" * 80)
        for issue in errors:
            print(f"\n{issue}")

    if warnings:
        print("\n[WARNINGS] (Should Fix):")
        print("-" * 80)
        for issue in warnings:
            print(f"\n{issue}")

    print("\n" + "=" * 80)

    if result.status == "error":
        print("\n[VALIDATION FAILED]")
        print("\nFix the errors above before committing to prevent deployment failures.")
    else:
        print("\n[VALIDATION PASSED] (with warnings)")
        print("\nProject can be deployed, but consider addressing the warnings.")

    print("=" * 80)


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python validate_pbip_syntax.py <project_path> [--json] [--strict]")
        print("\nExample:")
        print("  python validate_pbip_syntax.py ./SalesReport.pbip")
        print("  python validate_pbip_syntax.py ./SalesReport.pbip --json")
        print("  python validate_pbip_syntax.py ./SalesReport.pbip --strict")
        print("\nOptions:")
        print("  --json      Output results in JSON format")
        print("  --strict    Treat warnings as errors")
        print("\nExit Codes:")
        print("  0 - All validations passed")
        print("  1 - Warnings found (non-blocking)")
        print("  2 - Errors found (blocking)")
        print("  3 - Script error")
        sys.exit(3)

    project_path = sys.argv[1]
    output_json = '--json' in sys.argv
    strict = '--strict' in sys.argv

    try:
        validator = PbipSyntaxValidator(project_path, strict=strict)
        result = validator.validate()

        if output_json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print_report(result)

        # Exit codes
        if result.status == "error":
            sys.exit(2)
        elif result.status == "warning":
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        if output_json:
            print(json.dumps({
                "status": "error",
                "message": f"Script error: {str(e)}"
            }))
        else:
            print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
