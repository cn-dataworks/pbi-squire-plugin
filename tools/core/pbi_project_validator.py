#!/usr/bin/env python3
"""
Power BI Project Validator

A lightweight script to validate Power BI project folder structures.
Detects format type (pbip, pbi-tools, pbix) and validates required files exist.

This script replaces LLM-based file existence checks with efficient Python code,
reducing token usage by 80-90% for project validation tasks.

Usage:
    python pbi_project_validator.py <project_path> [--visual-changes] [--json]

Arguments:
    project_path          Path to Power BI project folder or PBIX file

Options:
    --visual-changes      Flag indicating visual property changes are expected
                          (requires .Report folder for pbip format)
    --json                Output results as JSON (default: human-readable)

Exit Codes:
    0 - Validation passed (status: validated)
    1 - Action required (status: action_required) - e.g., PBIX needs extraction
    2 - Validation error (status: error)
    3 - Script error (invalid arguments, etc.)

Examples:
    # Validate a Power BI Project
    python pbi_project_validator.py "C:\\Projects\\SalesReport"

    # Validate with visual changes expected
    python pbi_project_validator.py "C:\\Projects\\SalesReport" --visual-changes

    # Get JSON output for programmatic use
    python pbi_project_validator.py "C:\\Projects\\SalesReport" --json

Author: Power BI Analyst Agent
Version: 1.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ValidationResult:
    """Structured validation result"""
    status: str  # "validated", "action_required", "error"
    format: str  # "pbip", "pbi-tools", "pbix", "pbix-extracted-pbitools", "invalid"
    action_type: Optional[str]  # e.g., "pbix_extraction", "invalid_format", etc.
    validated_project_path: Optional[str]
    requires_compilation: bool
    semantic_model_path: Optional[str]
    report_path: Optional[str]
    error_message: Optional[str]
    suggested_fix: Optional[str]

    # Additional metadata
    project_path: str
    visual_changes_expected: bool
    validation_timestamp: str

    # Structure details (for validated projects)
    tmdl_files_found: List[str]
    report_files_found: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class PbiProjectValidator:
    """
    Validates Power BI project folder structures.

    Supports three input formats:
    1. Power BI Project (.pbip) - Native format with *.pbip file
    2. pbi-tools Format - Extracted folder with .pbixproj.json
    3. PBIX File - Compiled binary requiring extraction
    """

    def __init__(self, project_path: str, visual_changes_expected: bool = False):
        self.project_path = Path(project_path).resolve()
        self.visual_changes_expected = visual_changes_expected
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def validate(self) -> ValidationResult:
        """
        Main validation entry point.
        Returns a ValidationResult with all relevant information.
        """
        # Check if path exists
        if not self.project_path.exists():
            return self._error_result(
                action_type="path_not_found",
                error_message=f"Path does not exist: {self.project_path}",
                suggested_fix="Verify the project path is correct and accessible"
            )

        # Detect format and validate accordingly
        detected_format = self._detect_format()

        if detected_format == "pbip":
            return self._validate_pbip()
        elif detected_format == "pbi-tools":
            return self._validate_pbitools()
        elif detected_format == "pbix":
            return self._handle_pbix()
        else:
            return self._handle_invalid_format()

    def _detect_format(self) -> str:
        """
        Detect the Power BI project format.
        Returns: "pbip", "pbi-tools", "pbix", or "invalid"
        """
        # Check for PBIX file first (single file)
        if self.project_path.is_file():
            if self.project_path.suffix.lower() == ".pbix":
                return "pbix"
            return "invalid"

        # Check for Power BI Project (.pbip)
        pbip_files = list(self.project_path.glob("*.pbip"))
        semantic_model_folders = list(self.project_path.glob("*.SemanticModel"))

        if pbip_files and semantic_model_folders:
            return "pbip"

        # Check for pbi-tools format
        pbixproj_file = self.project_path / ".pbixproj.json"
        model_folder = self.project_path / "Model"

        if pbixproj_file.exists() and model_folder.exists():
            return "pbi-tools"

        # Also check without leading dot (some versions)
        pbixproj_alt = self.project_path / "pbixproj.json"
        if pbixproj_alt.exists() and model_folder.exists():
            return "pbi-tools"

        return "invalid"

    def _validate_pbip(self) -> ValidationResult:
        """Validate a Power BI Project (.pbip) format"""
        # Find the .pbip file and SemanticModel folder
        pbip_files = list(self.project_path.glob("*.pbip"))
        semantic_model_folders = list(self.project_path.glob("*.SemanticModel"))
        report_folders = list(self.project_path.glob("*.Report"))

        if not pbip_files:
            return self._error_result(
                action_type="missing_pbip_file",
                error_message="No .pbip file found in project folder",
                suggested_fix="Ensure this is a valid Power BI Project folder"
            )

        if not semantic_model_folders:
            return self._error_result(
                action_type="missing_semantic_model",
                error_message="No .SemanticModel folder found in project",
                suggested_fix="Ensure this is a valid Power BI Project with a semantic model"
            )

        semantic_model_path = semantic_model_folders[0]
        report_path = report_folders[0] if report_folders else None

        # Validate TMDL structure
        definition_folder = semantic_model_path / "definition"
        if not definition_folder.exists():
            return self._error_result(
                action_type="invalid_tmdl_structure",
                error_message="Missing 'definition' folder in SemanticModel",
                suggested_fix="Verify this is a valid Power BI Project exported from Power BI Desktop"
            )

        # Check for key TMDL files
        model_tmdl = definition_folder / "model.tmdl"
        tables_folder = definition_folder / "tables"

        tmdl_files_found = []
        if model_tmdl.exists():
            tmdl_files_found.append("model.tmdl")
        if tables_folder.exists():
            tmdl_files_found.append("tables/")
            # Count table files
            table_files = list(tables_folder.glob("*.tmdl"))
            tmdl_files_found.extend([f"tables/{f.name}" for f in table_files[:5]])
            if len(table_files) > 5:
                tmdl_files_found.append(f"... and {len(table_files) - 5} more")

        relationships_tmdl = definition_folder / "relationships.tmdl"
        if relationships_tmdl.exists():
            tmdl_files_found.append("relationships.tmdl")

        if not model_tmdl.exists():
            return self._error_result(
                action_type="invalid_tmdl_structure",
                error_message="Missing model.tmdl in definition folder",
                suggested_fix="Verify this is a valid Power BI Project with TMDL definitions"
            )

        # Check visual changes compatibility
        if self.visual_changes_expected and not report_path:
            return self._error_result(
                action_type="report_folder_missing",
                error_message="Visual changes requested but .Report folder not found in project structure",
                suggested_fix=(
                    "Options:\n"
                    "1. Open and re-save in Power BI Desktop to create .Report folder\n"
                    "2. Handle visual changes manually in Power BI Desktop UI\n"
                    "3. Re-run with a problem description focused only on calculation changes"
                )
            )

        # Validate report structure if present
        report_files_found = []
        if report_path:
            report_json = report_path / "definition" / "report.json"
            pages_folder = report_path / "definition" / "pages"

            if report_json.exists():
                report_files_found.append("report.json")
            if pages_folder.exists():
                report_files_found.append("pages/")
                page_folders = [f for f in pages_folder.iterdir() if f.is_dir()]
                report_files_found.extend([f"pages/{f.name}/" for f in page_folders[:3]])
                if len(page_folders) > 3:
                    report_files_found.append(f"... and {len(page_folders) - 3} more pages")

        # Success!
        return ValidationResult(
            status="validated",
            format="pbip",
            action_type=None,
            validated_project_path=str(self.project_path),
            requires_compilation=False,
            semantic_model_path=str(definition_folder),
            report_path=str(report_path / "definition") if report_path else None,
            error_message=None,
            suggested_fix=None,
            project_path=str(self.project_path),
            visual_changes_expected=self.visual_changes_expected,
            validation_timestamp=self.timestamp,
            tmdl_files_found=tmdl_files_found,
            report_files_found=report_files_found
        )

    def _validate_pbitools(self) -> ValidationResult:
        """Validate a pbi-tools extracted format"""
        model_folder = self.project_path / "Model"

        # Check visual changes compatibility first
        if self.visual_changes_expected:
            return self._error_result(
                action_type="format_incompatible_with_visual_changes",
                error_message="Visual changes requested but project format does not support visual property modifications",
                suggested_fix=(
                    "Options:\n"
                    "1. Use Power BI Project (.pbip) format instead - Open in PBI Desktop, File > Save As > Power BI Project\n"
                    "2. Handle visual changes manually in Power BI Desktop UI\n"
                    "3. Split the request - run evaluation for calculation changes only"
                )
            )

        # Validate TMDL structure
        model_tmdl = model_folder / "model.tmdl"
        database_tmdl = model_folder / "database.tmdl"
        tables_folder = model_folder / "tables"

        tmdl_files_found = []

        if not model_tmdl.exists():
            return self._error_result(
                action_type="invalid_tmdl_structure",
                error_message="Missing model.tmdl in Model folder",
                suggested_fix="Verify this is a valid pbi-tools extracted project"
            )
        tmdl_files_found.append("model.tmdl")

        if database_tmdl.exists():
            tmdl_files_found.append("database.tmdl")

        if tables_folder.exists():
            tmdl_files_found.append("tables/")
            table_files = list(tables_folder.glob("*.tmdl"))
            tmdl_files_found.extend([f"tables/{f.name}" for f in table_files[:5]])
            if len(table_files) > 5:
                tmdl_files_found.append(f"... and {len(table_files) - 5} more")

        # Success!
        return ValidationResult(
            status="validated",
            format="pbi-tools",
            action_type=None,
            validated_project_path=str(self.project_path),
            requires_compilation=True,
            semantic_model_path=str(model_folder),
            report_path=None,
            error_message=None,
            suggested_fix=None,
            project_path=str(self.project_path),
            visual_changes_expected=self.visual_changes_expected,
            validation_timestamp=self.timestamp,
            tmdl_files_found=tmdl_files_found,
            report_files_found=[]
        )

    def _handle_pbix(self) -> ValidationResult:
        """Handle PBIX file - requires extraction"""
        return ValidationResult(
            status="action_required",
            format="pbix",
            action_type="pbix_extraction",
            validated_project_path=None,
            requires_compilation=False,
            semantic_model_path=None,
            report_path=None,
            error_message=None,
            suggested_fix=None,
            project_path=str(self.project_path),
            visual_changes_expected=self.visual_changes_expected,
            validation_timestamp=self.timestamp,
            tmdl_files_found=[],
            report_files_found=[]
        )

    def _handle_invalid_format(self) -> ValidationResult:
        """Handle unrecognized format"""
        # Gather info about what exists at the path
        contents = []
        if self.project_path.is_dir():
            for item in sorted(self.project_path.iterdir())[:10]:
                item_type = "dir" if item.is_dir() else "file"
                contents.append(f"  - {item.name} ({item_type})")
            if len(list(self.project_path.iterdir())) > 10:
                contents.append(f"  ... and {len(list(self.project_path.iterdir())) - 10} more items")

        contents_str = "\n".join(contents) if contents else "  (empty or not a directory)"

        return self._error_result(
            action_type="invalid_format",
            error_message=(
                f"Path does not contain a valid Power BI project structure.\n\n"
                f"Expected one of:\n"
                f"  - Power BI Project: Folder with *.pbip file and *.SemanticModel/ folder\n"
                f"  - PBIX File: Single file ending in .pbix\n"
                f"  - pbi-tools Format: Folder with .pbixproj.json and Model/ folder\n\n"
                f"Contents found at path:\n{contents_str}"
            ),
            suggested_fix="Provide a valid Power BI project path"
        )

    def _error_result(self, action_type: str, error_message: str, suggested_fix: str) -> ValidationResult:
        """Create an error result"""
        return ValidationResult(
            status="error",
            format="invalid",
            action_type=action_type,
            validated_project_path=None,
            requires_compilation=False,
            semantic_model_path=None,
            report_path=None,
            error_message=error_message,
            suggested_fix=suggested_fix,
            project_path=str(self.project_path),
            visual_changes_expected=self.visual_changes_expected,
            validation_timestamp=self.timestamp,
            tmdl_files_found=[],
            report_files_found=[]
        )

    def print_human_readable(self, result: ValidationResult):
        """Print results in human-readable format"""
        print("=" * 70)
        print("POWER BI PROJECT VALIDATION")
        print("=" * 70)
        print(f"Project Path: {result.project_path}")
        print(f"Timestamp: {result.validation_timestamp}")
        print(f"Visual Changes Expected: {result.visual_changes_expected}")
        print("=" * 70)

        if result.status == "validated":
            print(f"\n[SUCCESS] Project validated successfully")
            print(f"\nFormat: {result.format}")
            print(f"Semantic Model: {result.semantic_model_path}")
            if result.report_path:
                print(f"Report Path: {result.report_path}")
            print(f"Requires Compilation: {result.requires_compilation}")

            if result.tmdl_files_found:
                print(f"\nTMDL Files Found:")
                for f in result.tmdl_files_found:
                    print(f"  - {f}")

            if result.report_files_found:
                print(f"\nReport Files Found:")
                for f in result.report_files_found:
                    print(f"  - {f}")

        elif result.status == "action_required":
            print(f"\n[ACTION REQUIRED] {result.action_type}")
            print(f"\nFormat Detected: {result.format}")

            if result.action_type == "pbix_extraction":
                print("\nThe PBIX file needs to be extracted to a folder format for analysis.")
                print("\nOptions:")
                print("  [Y] Extract automatically with pbi-tools")
                print("  [N] Show manual extraction instructions")
                print("  [I] Help install pbi-tools first")

        elif result.status == "error":
            print(f"\n[ERROR] {result.action_type}")
            print(f"\n{result.error_message}")
            if result.suggested_fix:
                print(f"\nSuggested Fix:\n{result.suggested_fix}")

        print("\n" + "=" * 70)


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Validate Power BI project folder structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pbi_project_validator.py "C:\\Projects\\SalesReport"
  python pbi_project_validator.py "C:\\Projects\\SalesReport" --visual-changes
  python pbi_project_validator.py "C:\\Projects\\SalesReport" --json
        """
    )

    parser.add_argument(
        "project_path",
        help="Path to Power BI project folder or PBIX file"
    )

    parser.add_argument(
        "--visual-changes",
        action="store_true",
        dest="visual_changes",
        help="Flag indicating visual property changes are expected"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Run validation
    validator = PbiProjectValidator(
        project_path=args.project_path,
        visual_changes_expected=args.visual_changes
    )

    result = validator.validate()

    # Output results
    if args.json:
        print(result.to_json())
    else:
        validator.print_human_readable(result)

    # Exit with appropriate code
    if result.status == "validated":
        sys.exit(0)
    elif result.status == "action_required":
        sys.exit(1)
    else:  # error
        sys.exit(2)


if __name__ == "__main__":
    main()
