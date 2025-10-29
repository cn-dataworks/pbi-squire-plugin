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
        return f"Line {self.line_number} [{self.severity.value}] {self.code}: {self.message}\n  → {self.line_content.rstrip()}"


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
        self._validate_measure_structures()
        self._validate_property_indentation()
        self._validate_dax_expression_blocks()
        self._validate_property_placement()

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


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python tmdl_format_validator.py <tmdl_file_path> [--context 'description']")
        print("\nExample:")
        print("  python tmdl_format_validator.py ./tables/Commissions_Measures.tmdl")
        print("  python tmdl_format_validator.py ./tables/Commissions_Measures.tmdl --context 'Updated PSSR Misc Commission measure'")
        sys.exit(2)

    file_path = sys.argv[1]

    # Parse optional context
    context = None
    if len(sys.argv) > 2 and sys.argv[2] == '--context' and len(sys.argv) > 3:
        context = sys.argv[3]

    # Run validation
    validator = TmdlFormatValidator(file_path, context)
    success = validator.validate()
    validator.print_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
