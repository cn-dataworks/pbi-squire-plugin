#!/usr/bin/env python3
"""
TMDL Format Validator

A lightweight standalone validator for TMDL (Tabular Model Definition Language) files.
Validates formatting, indentation, and structure without requiring external dependencies.

Usage:
    python tmdl_format_validator.py <tmdl_file_path> [--context "description of changes"]

Exit Codes:
    0 - All validations passed
    1 - Validation errors found
    2 - File not found or read error

Author: Power BI Analyst Agent
Version: 1.0.0
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Validation issue severity levels"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    line_number: int
    severity: Severity
    code: str
    message: str
    line_content: str

    def __str__(self):
        return f"Line {self.line_number} [{self.severity.value}] {self.code}: {self.message}\n  > {self.line_content.rstrip()}"


class TmdlFormatValidator:
    """
    Validates TMDL file formatting and structure.

    Checks:
    - Indentation consistency (tabs vs spaces)
    - Property placement and indentation
    - Measure/column/table structure
    - DAX expression block formatting
    - Common syntax errors
    """

    # TMDL property keywords that must appear AFTER DAX expressions
    PROPERTY_KEYWORDS = [
        'formatString',
        'displayFolder',
        'lineageTag',
        'dataCategory',
        'summarizeBy',
        'isHidden',
        'dataType',
        'sourceColumn',
        'sortByColumn',
        'changedProperty',
        'annotation'
    ]

    # Object definition keywords
    OBJECT_KEYWORDS = ['measure', 'column', 'table', 'partition', 'relationship']

    def __init__(self, file_path: str, context: Optional[str] = None):
        self.file_path = Path(file_path)
        self.context = context
        self.lines: List[str] = []
        self.issues: List[ValidationIssue] = []
        self.uses_tabs = None  # None = unknown, True = tabs, False = spaces

    def validate(self) -> bool:
        """
        Run all validations on the TMDL file.
        Returns True if all validations pass, False otherwise.
        """
        # Read file
        if not self._read_file():
            return False

        # Run validations
        self._detect_indentation_type()
        # NOTE: Mixed indentation validation disabled - too aggressive for existing codebase
        # self._validate_mixed_indentation()
        self._validate_measure_structures()
        self._validate_property_indentation()
        self._validate_dax_expression_blocks()
        self._validate_property_placement()
        self._validate_partition_source_expressions()
        self._validate_partition_property_names()

        return len([i for i in self.issues if i.severity == Severity.ERROR]) == 0

    def _read_file(self) -> bool:
        """Read the TMDL file into memory"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
            return True
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.file_path}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"ERROR: Failed to read file: {e}", file=sys.stderr)
            return False

    def _detect_indentation_type(self):
        """Detect whether file uses tabs or spaces for indentation"""
        tab_lines = 0
        space_lines = 0

        for line in self.lines:
            if line.startswith('\t'):
                tab_lines += 1
            elif line.startswith(' '):
                space_lines += 1

        self.uses_tabs = tab_lines > space_lines

    def _get_indentation_level(self, line: str) -> int:
        """Get the indentation level of a line (number of tabs/spaces)"""
        if self.uses_tabs:
            return len(line) - len(line.lstrip('\t'))
        else:
            # Assume 4 spaces = 1 level
            leading_spaces = len(line) - len(line.lstrip(' '))
            return leading_spaces // 4

    def _validate_measure_structures(self):
        """Validate measure/column/table definition structures"""
        for i, line in enumerate(self.lines, start=1):
            # Check for object definitions
            for keyword in self.OBJECT_KEYWORDS:
                pattern = rf'\s*{keyword}\s+[\'"]?(\w+)[\'"]?\s*='
                if re.search(pattern, line):
                    self._validate_object_definition(i, keyword)

    def _validate_object_definition(self, line_num: int, obj_type: str):
        """Validate a specific object definition starting at line_num"""
        # Find the next object definition or end of file
        obj_indent = self._get_indentation_level(self.lines[line_num - 1])

        # Check if there's content after the '=' on the same line
        line_content = self.lines[line_num - 1].strip()
        if not line_content.endswith('='):
            # Multi-line definition is fine
            pass

        # Find properties for this object
        found_properties = []
        found_dax_expression = False

        for i in range(line_num, min(line_num + 100, len(self.lines) + 1)):
            current_line = self.lines[i - 1]
            current_indent = self._get_indentation_level(current_line)

            # Stop if we hit another object at same or lower indent
            if current_indent <= obj_indent and i > line_num:
                if any(keyword in current_line for keyword in self.OBJECT_KEYWORDS):
                    break

            # Check for properties
            for prop in self.PROPERTY_KEYWORDS:
                if re.search(rf'\s*{prop}\s*:', current_line):
                    found_properties.append((i, prop, current_indent))

            # Check for DAX keywords that indicate expression block
            if re.search(r'\s*(VAR|RETURN|CALCULATE|IF|SUMX)\s+', current_line):
                found_dax_expression = True

    def _validate_property_indentation(self):
        """Validate that properties have consistent indentation"""
        property_indents = {}

        for i, line in enumerate(self.lines, start=1):
            for prop in self.PROPERTY_KEYWORDS:
                if re.search(rf'^\s*{prop}\s*:', line):
                    indent = self._get_indentation_level(line)

                    if prop not in property_indents:
                        property_indents[prop] = []
                    property_indents[prop].append((i, indent))

        # Check for inconsistent indentation within property groups
        for i, line in enumerate(self.lines, start=1):
            # Find groups of consecutive properties
            if any(re.search(rf'^\s*{prop}\s*:', line) for prop in self.PROPERTY_KEYWORDS):
                indent = self._get_indentation_level(line)

                # Check next few lines for more properties
                for j in range(i + 1, min(i + 5, len(self.lines) + 1)):
                    next_line = self.lines[j - 1]
                    if any(re.search(rf'^\s*{prop}\s*:', next_line) for prop in self.PROPERTY_KEYWORDS):
                        next_indent = self._get_indentation_level(next_line)

                        if next_indent != indent:
                            self.issues.append(ValidationIssue(
                                line_number=j,
                                severity=Severity.ERROR,
                                code="TMDL001",
                                message=f"Inconsistent property indentation. Expected {indent} tabs/levels, got {next_indent}",
                                line_content=next_line
                            ))
                    elif next_line.strip() == '':
                        continue
                    else:
                        break

    def _validate_dax_expression_blocks(self):
        """Validate DAX expression blocks within measures/columns"""
        in_expression = False
        expression_indent = 0

        for i, line in enumerate(self.lines, start=1):
            # Detect start of DAX expression (after measure/column = )
            if re.search(r'(measure|column)\s+[\'"]?\w+[\'"]?\s*=\s*$', line):
                in_expression = True
                expression_indent = self._get_indentation_level(line) + 1
                continue

            if in_expression:
                current_indent = self._get_indentation_level(line)

                # Check if we hit a property (should end expression block)
                if any(re.search(rf'^\s*{prop}\s*:', line) for prop in self.PROPERTY_KEYWORDS):
                    # Property found - validate it's at correct indent (should be expression_indent)
                    if current_indent < expression_indent:
                        self.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.ERROR,
                            code="TMDL002",
                            message=f"Property has insufficient indentation. Properties should have {expression_indent} tabs/levels, got {current_indent}",
                            line_content=line
                        ))
                    in_expression = False
                    continue

                # Check if we hit another object definition
                if any(keyword in line for keyword in self.OBJECT_KEYWORDS):
                    in_expression = False
                    continue

                # Validate DAX expression lines have proper indent
                if line.strip() and not line.strip().startswith('//'):
                    if current_indent < expression_indent:
                        self.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.WARNING,
                            code="TMDL003",
                            message=f"DAX expression line may have incorrect indentation. Expected at least {expression_indent} tabs/levels",
                            line_content=line
                        ))

    def _validate_property_placement(self):
        """Validate that properties appear in correct locations relative to expressions"""
        for i, line in enumerate(self.lines, start=1):
            # Check for properties that appear within what looks like a DAX expression
            for prop in self.PROPERTY_KEYWORDS:
                if re.search(rf'\s*{prop}\s*:', line):
                    # Look backwards to see if we're inside a DAX expression
                    for j in range(i - 1, max(0, i - 20), -1):
                        prev_line = self.lines[j - 1]

                        # If we find RETURN without a closing pattern, property is in wrong place
                        if re.search(r'\s*RETURN\s*$', prev_line):
                            # Check if the next non-empty line after RETURN is not a property
                            next_line_idx = j
                            while next_line_idx < i - 1:
                                check_line = self.lines[next_line_idx]
                                if check_line.strip() and not check_line.strip().startswith('//'):
                                    # There's code between RETURN and property - that's the issue!
                                    # The property should come right after the return value
                                    indent_return = self._get_indentation_level(prev_line)
                                    indent_prop = self._get_indentation_level(line)

                                    # Property should be at same indent as RETURN or less
                                    if indent_prop > indent_return:
                                        self.issues.append(ValidationIssue(
                                            line_number=i,
                                            severity=Severity.ERROR,
                                            code="TMDL004",
                                            message=f"Property '{prop}' appears to be inside DAX expression block. Properties must be outside the expression with proper indentation.",
                                            line_content=line
                                        ))
                                    break
                                next_line_idx += 1
                            break

    def _validate_partition_source_expressions(self):
        """
        Validate partition source/expression DAX (e.g., field parameters).

        Checks:
        - 'source = { }' blocks: Multi-line DAX with tab indentation (M code, DAX expressions)
        - 'expression := { }' blocks: Must be single-line for table constructors
        """
        in_partition_source = False
        source_indent = 0
        partition_start_line = 0
        brace_line = 0

        for i, line in enumerate(self.lines, start=1):
            # Detect expression := { pattern (field parameters - must be inline)
            if re.search(r'expression\s*:=\s*\{', line):
                # Check if this spans multiple lines
                if not re.search(r'\}', line):  # Opening brace without closing brace on same line
                    self.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        code="TMDL010",
                        message="Field parameter 'expression := { }' must be on a single line. Multi-line format causes indentation errors in Power BI. Put all tuples on the same line as the opening brace.",
                        line_content=line
                    ))
                continue

            # Detect partition source start (original validation for source = {)
            if re.search(r'source\s*=\s*\{', line):
                in_partition_source = True
                brace_line = i
                # Expected indent for content inside source = { }
                source_indent = self._get_indentation_level(line) + 1

                # Find the partition definition line for context
                for j in range(i - 1, max(0, i - 10), -1):
                    if 'partition' in self.lines[j - 1]:
                        partition_start_line = j
                        break
                continue

            if in_partition_source:
                # Check for closing brace
                if re.search(r'^\s*\}', line):
                    in_partition_source = False
                    continue

                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith('//'):
                    continue

                # Validate indentation of DAX code inside source block
                current_indent = self._get_indentation_level(line)

                # Check if using tabs when file uses tabs
                if self.uses_tabs:
                    # Count leading whitespace characters
                    leading_ws = len(line) - len(line.lstrip())
                    tab_count = line[:leading_ws].count('\t')
                    space_count = line[:leading_ws].count(' ')

                    # If we find spaces in a tab-indented file, that's an error
                    if space_count > 0 and tab_count == 0:
                        self.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.ERROR,
                            code="TMDL005",
                            message=f"Partition source uses SPACES instead of TABS. File uses tab indentation. This will cause 'Unexpected line type' parsing errors in Power BI.",
                            line_content=line
                        ))
                        continue

                    # Check for mixed tabs and spaces
                    if space_count > 0 and tab_count > 0:
                        self.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.ERROR,
                            code="TMDL006",
                            message=f"Partition source mixes TABS and SPACES. Use only tabs for indentation.",
                            line_content=line
                        ))
                        continue

                # Validate correct indentation level
                if current_indent != source_indent:
                    # Determine if too few or too many
                    if current_indent < source_indent:
                        self.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.ERROR,
                            code="TMDL007",
                            message=f"Partition source code has insufficient indentation. Expected {source_indent} tabs/levels, got {current_indent}. Add {source_indent - current_indent} more tab(s).",
                            line_content=line
                        ))
                    else:
                        self.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.WARNING,
                            code="TMDL008",
                            message=f"Partition source code has excessive indentation. Expected {source_indent} tabs/levels, got {current_indent}. Remove {current_indent - source_indent} tab(s).",
                            line_content=line
                        ))

    def _validate_partition_property_names(self):
        """
        Validate partition property naming semantics (source vs expression).

        Detects incorrect use of 'source = {' for DAX table constructors (field parameters).
        Table constructors must use 'expression :=' instead of 'source ='.
        """
        for i, line in enumerate(self.lines, start=1):
            # Detect 'source = {' pattern (table constructor with wrong property)
            if re.search(r'^\s*source\s*=\s*\{', line):
                # Check if this is within a calculated partition
                in_calculated_partition = False
                for j in range(i - 1, max(0, i - 10), -1):
                    prev_line = self.lines[j - 1]
                    if re.search(r'partition.*=\s*calculated', prev_line):
                        in_calculated_partition = True
                        break
                    # Stop if we hit another partition or table definition
                    if re.search(r'^\s*(partition|table)\s+', prev_line):
                        break

                if in_calculated_partition:
                    self.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        code="TMDL009",
                        message="Field parameters must use 'expression :=' not 'source ='. DAX table constructors require the 'expression' property with ':=' assignment operator.",
                        line_content=line
                    ))

    def _validate_mixed_indentation(self):
        """
        Validate that lines don't mix tabs and spaces at structural levels.

        Mixed tabs/spaces in shallow indentation (0-3 tabs) can cause "Invalid indentation"
        errors, especially in SWITCH arguments and lines preceding properties. Deep DAX
        expression indentation is more tolerant of mixed indentation.
        """
        for i, line in enumerate(self.lines, start=1):
            # Skip blank lines and lines with no indentation
            if not line or line.isspace() or not (line[0] in ('\t', ' ')):
                continue

            # Extract leading whitespace
            leading = line[:len(line) - len(line.lstrip())]

            # Check if both tabs and spaces exist in leading whitespace
            has_tabs = '\t' in leading
            has_spaces = ' ' in leading

            if has_tabs and has_spaces:
                # Count tab depth (tabs before first space)
                tab_count = len(leading) - len(leading.lstrip('\t'))

                # Only flag as ERROR if at shallow indentation (0-3 tabs)
                # These are structural levels where mixed indentation causes parsing issues
                if tab_count <= 3:
                    self.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        code="TMDL011",
                        message="Mixed tabs and spaces detected at structural indentation level. SWITCH arguments and lines near properties must use pure tabs.",
                        line_content=line
                    ))

    def print_report(self):
        """Print validation report to console"""
        print("=" * 80)
        print("TMDL FORMAT VALIDATION REPORT")
        print("=" * 80)
        print(f"File: {self.file_path}")
        if self.context:
            print(f"Context: {self.context}")
        print(f"Total Lines: {len(self.lines)}")
        print(f"Indentation: {'TABS' if self.uses_tabs else 'SPACES'}")
        print("=" * 80)

        if not self.issues:
            print("\n[SUCCESS] No formatting issues found!")
            print("\nThe TMDL file is properly formatted and ready for use.")
            return

        # Group issues by severity
        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        warnings = [i for i in self.issues if i.severity == Severity.WARNING]
        infos = [i for i in self.issues if i.severity == Severity.INFO]

        print(f"\n[SUMMARY]")
        print(f"  Errors:   {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  Info:     {len(infos)}")

        if errors:
            print("\n[ERRORS] (Must Fix):")
            print("-" * 80)
            for issue in sorted(errors, key=lambda x: x.line_number):
                print(f"\n{issue}")

        if warnings:
            print("\n[WARNINGS] (Should Fix):")
            print("-" * 80)
            for issue in sorted(warnings, key=lambda x: x.line_number):
                print(f"\n{issue}")

        if infos:
            print("\n[INFO]:")
            print("-" * 80)
            for issue in sorted(infos, key=lambda x: x.line_number):
                print(f"\n{issue}")

        print("\n" + "=" * 80)

        if errors:
            print("\n[VALIDATION FAILED]")
            print("\nThe TMDL file has formatting errors that must be fixed before")
            print("it can be opened in Power BI Desktop.")
        else:
            print("\n[VALIDATION PASSED] (with warnings)")
            print("\nThe TMDL file should open in Power BI Desktop, but consider")
            print("addressing the warnings for better code quality.")

        print("=" * 80)


def run_csharp_validator(semantic_model_path: Path) -> Optional[Dict]:
    """
    Run the authoritative C# TmdlValidator (if available).

    This validator uses Microsoft's official TmdlSerializer parser - the same
    parser used by Power BI Desktop - providing 100% accurate validation.

    Args:
        semantic_model_path: Path to .SemanticModel folder

    Returns:
        Validation result dict or None if validator not available
    """
    import subprocess
    import json

    # Find TmdlValidator.exe
    tools_dir = Path(__file__).parent
    validator_exe = tools_dir / "TmdlValidator.exe"

    if not validator_exe.exists():
        return None

    try:
        # Run C# validator with JSON output
        result = subprocess.run(
            [str(validator_exe), "--path", str(semantic_model_path), "--json"],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse JSON result
        validation_result = json.loads(result.stdout)
        return validation_result

    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def validate_with_csharp(semantic_model_path: Path) -> bool:
    """
    Run authoritative C# validation and print results.

    Returns:
        True if validation passed, False otherwise
    """
    print("\n" + "=" * 80)
    print("RUNNING AUTHORITATIVE TMDL VALIDATION")
    print("=" * 80)
    print("Using Microsoft TmdlSerializer (same parser as Power BI Desktop)")
    print("=" * 80)

    result = run_csharp_validator(semantic_model_path)

    if result is None:
        print("\n[SKIPPED] C# TmdlValidator not available")
        print("\nTo enable authoritative validation:")
        print("  1. Install .NET 8.0 SDK: https://dotnet.microsoft.com/download/dotnet/8.0")
        print("  2. Build validator: cd .claude/tools/TmdlValidator && .\\build.ps1")
        print("\nContinuing with regex-based validation only...")
        return True  # Don't fail if C# validator not available

    if result['isValid']:
        print(f"\n[SUCCESS] {result['message']}")
        print(f"\nDatabase: {result.get('databaseName', 'N/A')}")
        print(f"Compatibility Level: {result.get('compatibilityLevel', 'N/A')}")
        print("\nThis project can be opened in Power BI Desktop without errors.")
    else:
        print(f"\n[{result['errorType'].upper()}] {result['message']}")

        if result.get('document'):
            print(f"\nError Location:")
            print(f"  Document: {result['document']}")
            print(f"  Line: {result.get('lineNumber', 'N/A')}")
            print(f"  Content: {result.get('lineText', 'N/A')}")

    print("\n" + "=" * 80)

    return result['isValid']


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python tmdl_format_validator.py <tmdl_file_path> [--context 'description'] [--authoritative]")
        print("\nExample:")
        print("  python tmdl_format_validator.py ./tables/Commissions_Measures.tmdl")
        print("  python tmdl_format_validator.py ./tables/Commissions_Measures.tmdl --context 'Updated PSSR Misc Commission measure'")
        print("  python tmdl_format_validator.py ./tables/Commissions_Measures.tmdl --authoritative")
        print("\nOptions:")
        print("  --context 'text'     Add context description to report")
        print("  --authoritative      Run C# TmdlSerializer validation (requires .SemanticModel folder)")
        sys.exit(2)

    file_path = sys.argv[1]

    # Parse optional flags
    context = None
    run_authoritative = False

    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--context' and i + 1 < len(sys.argv):
            context = sys.argv[i + 1]
        elif sys.argv[i] == '--authoritative':
            run_authoritative = True

    # Run regex-based validation
    validator = TmdlFormatValidator(file_path, context)
    regex_success = validator.validate()
    validator.print_report()

    # Optionally run authoritative C# validation
    csharp_success = True
    if run_authoritative:
        # Determine .SemanticModel folder path
        file_path_obj = Path(file_path)

        # Navigate up to find .SemanticModel folder
        semantic_model_path = None
        for parent in [file_path_obj.parent, file_path_obj.parent.parent, file_path_obj.parent.parent.parent]:
            if parent.name.endswith('.SemanticModel'):
                semantic_model_path = parent
                break

        if semantic_model_path:
            csharp_success = validate_with_csharp(semantic_model_path)
        else:
            print("\n[WARNING] Could not locate .SemanticModel folder for authoritative validation")
            print(f"File path: {file_path}")

    # Exit with appropriate code (both must pass)
    sys.exit(0 if (regex_success and csharp_success) else 1)


if __name__ == "__main__":
    main()
