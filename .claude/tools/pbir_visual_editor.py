#!/usr/bin/env python3
"""
PBIR Visual Editor Utility

This module provides functions to execute XML edit plans on Power BI Report (PBIR)
visual.json files. It supports two operation types:

1. replace_property: Modify top-level visual.json properties (x, y, width, height, visualType)
2. config_edit: Modify properties inside the stringified config blob

Usage:
    python pbir_visual_editor.py <edit_plan.xml> <base_path>

Example XML Edit Plan:
    <edit_plan>
      <step
        file_path="definition/pages/ReportSection123/visuals/VisualContainer456/visual.json"
        operation="replace_property"
        json_path="width"
        new_value="500"
      />
      <step
        file_path="definition/pages/ReportSection123/visuals/VisualContainer456/visual.json"
        operation="config_edit"
        json_path="title.text"
        new_value="'Regional Performance'"
      />
    </edit_plan>
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Tuple


class PBIREditError(Exception):
    """Custom exception for PBIR editing errors"""
    pass


def parse_value(value_str: str) -> Any:
    """
    Parse the new_value string into appropriate Python type.

    Handles:
    - Numbers (int/float)
    - Booleans (true/false)
    - Strings (quoted with single or double quotes)
    - null

    Args:
        value_str: String representation of the value

    Returns:
        Parsed value in appropriate Python type

    Examples:
        "500" → 500
        "true" → True
        "'Regional Performance'" → "Regional Performance"
        "null" → None
    """
    value_str = value_str.strip()

    # Handle quoted strings
    if (value_str.startswith("'") and value_str.endswith("'")) or \
       (value_str.startswith('"') and value_str.endswith('"')):
        return value_str[1:-1]  # Remove quotes

    # Handle boolean
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False

    # Handle null
    if value_str.lower() == 'null':
        return None

    # Try to parse as number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        # If all else fails, treat as string
        return value_str


def set_nested_property(obj: Dict, json_path: str, value: Any) -> None:
    """
    Set a nested property in a dictionary using dot notation.

    Args:
        obj: The dictionary to modify
        json_path: Dot-separated path (e.g., "title.text")
        value: Value to set

    Examples:
        set_nested_property(obj, "title.text", "New Title")
        set_nested_property(obj, "visualHeader.titleVisibility", True)
    """
    keys = json_path.split('.')
    current = obj

    # Navigate to the parent of the target property
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Set the final property
    current[keys[-1]] = value


def get_nested_property(obj: Dict, json_path: str) -> Any:
    """
    Get a nested property from a dictionary using dot notation.

    Args:
        obj: The dictionary to read from
        json_path: Dot-separated path

    Returns:
        The value at the path, or None if not found
    """
    keys = json_path.split('.')
    current = obj

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None

    return current


def replace_property(visual_json: Dict, json_path: str, new_value: Any) -> Dict:
    """
    Execute replace_property operation: modify top-level visual.json property.

    Args:
        visual_json: The visual.json object
        json_path: Property name (e.g., "width", "height", "x", "y", "visualType")
        new_value: New value for the property

    Returns:
        Modified visual.json object

    Raises:
        PBIREditError: If the property doesn't exist
    """
    if json_path not in visual_json:
        raise PBIREditError(
            f"Property '{json_path}' not found in visual.json. "
            f"Available properties: {list(visual_json.keys())}"
        )

    visual_json[json_path] = new_value
    return visual_json


def config_edit(visual_json: Dict, json_path: str, new_value: Any) -> Dict:
    """
    Execute config_edit operation: modify property inside stringified config blob.

    The 'config' property in visual.json is a stringified JSON. This function:
    1. Parses the config string to JSON object
    2. Modifies the nested property
    3. Re-stringifies the config

    Args:
        visual_json: The visual.json object
        json_path: Dot-separated path to property (e.g., "title.text")
        new_value: New value for the property

    Returns:
        Modified visual.json object

    Raises:
        PBIREditError: If config is invalid or property doesn't exist
    """
    if 'config' not in visual_json:
        raise PBIREditError("Visual does not have a 'config' property")

    config_str = visual_json['config']

    # Parse stringified config
    try:
        config_obj = json.loads(config_str)
    except json.JSONDecodeError as e:
        raise PBIREditError(f"Failed to parse config string: {e}")

    # Modify nested property
    set_nested_property(config_obj, json_path, new_value)

    # Re-stringify config (compact format, no extra whitespace)
    visual_json['config'] = json.dumps(config_obj, separators=(',', ':'))

    return visual_json


def execute_edit_step(
    visual_json: Dict,
    operation: str,
    json_path: str,
    new_value: str
) -> Dict:
    """
    Execute a single edit step on a visual.json object.

    Args:
        visual_json: The visual.json object to modify
        operation: Either "replace_property" or "config_edit"
        json_path: Path to the property to modify
        new_value: String representation of the new value

    Returns:
        Modified visual.json object

    Raises:
        PBIREditError: If operation is invalid or edit fails
    """
    parsed_value = parse_value(new_value)

    if operation == "replace_property":
        return replace_property(visual_json, json_path, parsed_value)
    elif operation == "config_edit":
        return config_edit(visual_json, json_path, parsed_value)
    else:
        raise PBIREditError(
            f"Invalid operation: '{operation}'. "
            f"Must be 'replace_property' or 'config_edit'"
        )


def execute_xml_edit_plan(
    xml_content: str,
    base_path: Path
) -> List[Tuple[str, bool, str]]:
    """
    Parse and execute an XML edit plan on PBIR visual.json files.

    Args:
        xml_content: XML string containing the edit plan
        base_path: Base path for resolving relative file paths (usually .Report folder)

    Returns:
        List of (file_path, success, message) tuples

    Example:
        results = execute_xml_edit_plan(xml_string, Path("C:/project/.Report"))
        for file_path, success, message in results:
            if success:
                print(f"✅ {file_path}: {message}")
            else:
                print(f"❌ {file_path}: {message}")
    """
    results = []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return [("XML Parse Error", False, f"Invalid XML: {e}")]

    if root.tag != "edit_plan":
        return [("XML Structure Error", False, "Root element must be <edit_plan>")]

    # Group steps by file_path to minimize file I/O
    steps_by_file: Dict[str, List[ET.Element]] = {}
    for step in root.findall('step'):
        file_path = step.get('file_path')
        if not file_path:
            results.append(("Missing Attribute", False, "Step missing 'file_path' attribute"))
            continue

        if file_path not in steps_by_file:
            steps_by_file[file_path] = []
        steps_by_file[file_path].append(step)

    # Process each file
    for rel_file_path, steps in steps_by_file.items():
        full_path = base_path / rel_file_path

        if not full_path.exists():
            results.append((rel_file_path, False, f"File not found: {full_path}"))
            continue

        try:
            # Read visual.json
            with open(full_path, 'r', encoding='utf-8') as f:
                visual_json = json.load(f)

            # Apply all steps for this file
            for step in steps:
                operation = step.get('operation')
                json_path = step.get('json_path')
                new_value = step.get('new_value')

                if not all([operation, json_path, new_value is not None]):
                    results.append((
                        rel_file_path,
                        False,
                        "Step missing required attributes (operation, json_path, new_value)"
                    ))
                    continue

                # Execute the edit
                visual_json = execute_edit_step(visual_json, operation, json_path, new_value)

            # Write modified visual.json back (pretty-printed with 2-space indent)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(visual_json, f, indent=2, ensure_ascii=False)

            results.append((
                rel_file_path,
                True,
                f"Applied {len(steps)} edit(s) successfully"
            ))

        except json.JSONDecodeError as e:
            results.append((rel_file_path, False, f"Invalid JSON in file: {e}"))
        except PBIREditError as e:
            results.append((rel_file_path, False, str(e)))
        except Exception as e:
            results.append((rel_file_path, False, f"Unexpected error: {e}"))

    return results


def validate_json_structure(visual_json: Dict) -> List[str]:
    """
    Validate basic structure of a visual.json object.

    Args:
        visual_json: The visual.json object to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required top-level properties
    required_props = ['name', 'position']
    for prop in required_props:
        if prop not in visual_json:
            errors.append(f"Missing required property: '{prop}'")

    # Validate position structure
    if 'position' in visual_json:
        pos = visual_json['position']
        required_pos_props = ['x', 'y', 'z', 'width', 'height']
        for prop in required_pos_props:
            if prop not in pos:
                errors.append(f"Missing position property: '{prop}'")

    # Validate config if present
    if 'config' in visual_json:
        try:
            config_obj = json.loads(visual_json['config'])
            # Config successfully parsed
        except json.JSONDecodeError as e:
            errors.append(f"Invalid config JSON: {e}")

    return errors


def main():
    """Command-line interface for PBIR visual editor"""
    if len(sys.argv) < 3:
        print("Usage: python pbir_visual_editor.py <edit_plan.xml> <base_path>")
        print()
        print("  edit_plan.xml: Path to XML file containing edit plan")
        print("  base_path:     Base path for resolving visual.json file paths (.Report folder)")
        sys.exit(1)

    xml_file_path = Path(sys.argv[1])
    base_path = Path(sys.argv[2])

    if not xml_file_path.exists():
        print(f"❌ Error: XML file not found: {xml_file_path}")
        sys.exit(1)

    if not base_path.exists():
        print(f"❌ Error: Base path not found: {base_path}")
        sys.exit(1)

    # Read XML edit plan
    with open(xml_file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    # Execute edit plan
    print(f"Executing edit plan from: {xml_file_path}")
    print(f"Base path: {base_path}")
    print()

    results = execute_xml_edit_plan(xml_content, base_path)

    # Display results
    success_count = sum(1 for _, success, _ in results if success)
    fail_count = len(results) - success_count

    for file_path, success, message in results:
        status = "✅" if success else "❌"
        print(f"{status} {file_path}")
        print(f"   {message}")

    print()
    print(f"Summary: {success_count} succeeded, {fail_count} failed")

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
