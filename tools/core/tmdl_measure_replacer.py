#!/usr/bin/env python3
"""
Reusable TMDL Measure Replacer for Power BI Projects

This tool provides robust, measure-level replacement for DAX code in TMDL files,
handling tab indentation and whitespace correctly.

Usage:
    python tmdl_measure_replacer.py <tmdl_file> <measure_name> <new_dax_file>

Arguments:
    tmdl_file     : Path to the TMDL file containing the measure
    measure_name  : Exact name of the measure (without quotes)
    new_dax_file  : Path to file containing new DAX body code

Example:
    python tmdl_measure_replacer.py Commissions_Measures.tmdl "Sales Commission GP Actual NEW" new_dax.txt

Author: Power BI Analyst Agent
Version: 1.0
"""

import re
import sys
from pathlib import Path

def read_file_with_tabs(filepath):
    """Read file preserving exact tab characters"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file_with_tabs(filepath, content):
    """Write file preserving exact tab characters"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_measure(content, measure_name):
    """
    Extract a complete measure definition by name
    Returns (start_pos, end_pos, measure_text, indent_level) or None if not found
    """
    # Escape special regex characters in measure name
    escaped_name = re.escape(measure_name)

    # Pattern to find the measure start
    # TMDL format: \tmeasure 'Name' =
    measure_start_pattern = rf"(\t+)measure '{escaped_name}' =\n"

    match = re.search(measure_start_pattern, content)
    if not match:
        print(f"ERROR: Measure '{measure_name}' not found in file", file=sys.stderr)
        return None

    start_pos = match.start()
    indent_level = match.group(1)  # Capture the tab indentation

    # Find the end of the measure
    # A measure ends when we hit another top-level element at the same indent level
    # Look for: formatString:, displayFolder:, lineageTag:, or next measure/column/table

    # Start searching after the measure declaration
    search_start = match.end()

    # Pattern for end markers (properties at same indent level as measure)
    end_pattern = rf"\n{indent_level}(formatString:|displayFolder:|lineageTag:|measure |column |table )"

    end_match = re.search(end_pattern, content[search_start:])
    if not end_match:
        # Measure goes to end of file
        end_pos = len(content)
    else:
        # End position is where the property/next element starts
        end_pos = search_start + end_match.start() + 1  # +1 to include the \n

    measure_text = content[start_pos:end_pos]
    return (start_pos, end_pos, measure_text, indent_level)

def replace_measure_dax(measure_text, new_dax_body, indent_level):
    """
    Replace just the DAX body of a measure, preserving properties

    measure_text: Full measure text including properties
    new_dax_body: Just the DAX code (VARs and RETURN)
    indent_level: The tab indentation level (e.g., '\t')
    """
    # Find where DAX body starts (after the = sign and newline)
    measure_header_pattern = r"(measure '[^']+' =)\n"

    match = re.search(measure_header_pattern, measure_text)
    if not match:
        print("ERROR: Could not find measure header", file=sys.stderr)
        return None

    header_end = match.end()

    # Find where DAX body ends (before formatString/displayFolder/etc)
    properties_pattern = rf"\n{indent_level}(formatString:|displayFolder:|lineageTag:|annotation )"

    prop_match = re.search(properties_pattern, measure_text)
    if prop_match:
        dax_end = prop_match.start() + 1  # +1 to include the \n before property
        properties = measure_text[dax_end:]
    else:
        # No properties found, DAX goes to end
        dax_end = len(measure_text)
        properties = ""

    # Construct new measure
    header = measure_text[:header_end]

    # Ensure new_dax_body has proper indentation
    # The DAX body should be indented with indent_level + one more tab
    dax_indent = indent_level + '\t'

    # Process new_dax_body: ensure each line has proper indentation
    dax_lines = new_dax_body.strip().split('\n')
    indented_dax_lines = [dax_indent + line if line.strip() else line for line in dax_lines]
    formatted_dax = '\n'.join(indented_dax_lines) + '\n'

    new_measure = header + formatted_dax + properties
    return new_measure

def replace_measure_in_file(filepath, measure_name, new_dax_body):
    """
    Replace a specific measure's DAX body in a TMDL file

    Args:
        filepath: Path to the TMDL file
        measure_name: Exact name of the measure (without quotes)
        new_dax_body: New DAX code (VARs and RETURN statements)

    Returns:
        True if successful, False otherwise
    """
    # Read file
    content = read_file_with_tabs(filepath)

    # Extract measure
    result = extract_measure(content, measure_name)
    if not result:
        return False

    start_pos, end_pos, measure_text, indent_level = result

    # Replace DAX body
    new_measure_text = replace_measure_dax(measure_text, new_dax_body, indent_level)
    if not new_measure_text:
        return False

    # Build new file content
    new_content = content[:start_pos] + new_measure_text + content[end_pos:]

    # Create backup
    backup_path = str(filepath) + '.backup'
    write_file_with_tabs(backup_path, content)
    print(f"[BACKUP] Created: {backup_path}")

    # Write new content
    write_file_with_tabs(filepath, new_content)
    print(f"[SUCCESS] Measure '{measure_name}' updated successfully")

    return True

def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) != 4:
        print("Usage: python tmdl_measure_replacer.py <tmdl_file> <measure_name> <new_dax_file>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print('  python tmdl_measure_replacer.py Commissions_Measures.tmdl "Sales Commission GP Actual NEW" new_dax.txt', file=sys.stderr)
        sys.exit(1)

    tmdl_file = Path(sys.argv[1])
    measure_name = sys.argv[2]
    new_dax_file = Path(sys.argv[3])

    # Validate inputs
    if not tmdl_file.exists():
        print(f"ERROR: TMDL file not found: {tmdl_file}", file=sys.stderr)
        sys.exit(1)

    if not new_dax_file.exists():
        print(f"ERROR: DAX file not found: {new_dax_file}", file=sys.stderr)
        sys.exit(1)

    # Read new DAX code
    with open(new_dax_file, 'r', encoding='utf-8') as f:
        new_dax_body = f.read()

    # Perform replacement
    print(f"[INFO] Replacing measure '{measure_name}' in {tmdl_file}")
    success = replace_measure_in_file(str(tmdl_file), measure_name, new_dax_body)

    if success:
        print("[COMPLETE] Measure replacement successful")
        sys.exit(0)
    else:
        print("[ERROR] Measure replacement failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
