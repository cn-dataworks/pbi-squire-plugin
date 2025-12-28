"""
Extract measure definitions and dependencies from TMDL files.

This script parses TMDL files in the .SemanticModel/definition folder to extract:
- Measure names and DAX expressions
- Calculated columns
- Measure dependencies (which measures reference other measures)
- Tables and relationships

Usage:
    python extract_measure_info.py <path_to_.SemanticModel_folder>

Example:
    python extract_measure_info.py "C:/Projects/SalesReport/.SemanticModel"
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any


def parse_tmdl_file(file_path: Path) -> Dict[str, Any]:
    """Parse a single TMDL file and extract measures and columns."""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    table_name = file_path.stem  # File name without extension
    measures = []
    columns = []

    # Parse measures
    # Pattern: measure MeasureName = DAX expression
    measure_pattern = r'measure\s+([^\s=]+)\s*=\s*\n?(.*?)(?=\n\s*(?:measure|column|partition|annotation|\Z))'
    measure_matches = re.finditer(measure_pattern, content, re.DOTALL | re.MULTILINE)

    for match in measure_matches:
        measure_name = match.group(1).strip()
        dax_expression = match.group(2).strip()

        # Extract referenced measures from the DAX
        referenced_measures = extract_measure_references(dax_expression)

        measures.append({
            "name": measure_name,
            "table": table_name,
            "expression": dax_expression,
            "dependencies": list(referenced_measures)
        })

    # Parse calculated columns
    # Pattern: column ColumnName = DAX expression
    column_pattern = r'column\s+([^\s=]+)\s*=\s*\n?(.*?)(?=\n\s*(?:measure|column|partition|annotation|\Z))'
    column_matches = re.finditer(column_pattern, content, re.DOTALL | re.MULTILINE)

    for match in column_matches:
        column_name = match.group(1).strip()
        dax_expression = match.group(2).strip()

        columns.append({
            "name": column_name,
            "table": table_name,
            "expression": dax_expression
        })

    return {
        "table": table_name,
        "measures": measures,
        "columns": columns
    }


def extract_measure_references(dax_expression: str) -> Set[str]:
    """Extract measure names referenced in a DAX expression."""
    references = set()

    # Pattern: [MeasureName] or [Table Name[Measure Name]]
    # Also catches CALCULATE([Measure], ...) patterns
    bracket_pattern = r'\[([^\]]+)\]'
    matches = re.findall(bracket_pattern, dax_expression)

    for match in matches:
        # Check if it's a table[column] reference
        if '[' in match:
            # It's a nested reference like Table[Column]
            # Extract just the column/measure name
            inner_match = re.search(r'\[([^\]]+)\]', match)
            if inner_match:
                references.add(inner_match.group(1))
        else:
            # Simple measure reference
            # Filter out likely column references (often have spaces or special chars)
            # Measures typically don't have spaces in names
            if not any(char in match for char in ['(', ')', '@']):
                references.add(match)

    return references


def get_all_measures_from_folder(semantic_model_folder: Path) -> List[Dict[str, Any]]:
    """Extract all measures from all TMDL files in the definition folder."""
    all_measures = []
    all_columns = []
    tables = []

    definition_folder = semantic_model_folder / "definition"

    if not definition_folder.exists():
        print(f"Warning: definition folder not found at {definition_folder}")
        return []

    tables_folder = definition_folder / "tables"

    if not tables_folder.exists():
        print(f"Warning: tables folder not found at {tables_folder}")
        return []

    # Parse each .tmdl file
    for tmdl_file in tables_folder.glob("*.tmdl"):
        try:
            parsed_data = parse_tmdl_file(tmdl_file)
            tables.append(parsed_data["table"])

            for measure in parsed_data["measures"]:
                all_measures.append(measure)

            for column in parsed_data["columns"]:
                all_columns.append(column)

        except Exception as e:
            print(f"Warning: Could not parse {tmdl_file.name}: {e}", file=sys.stderr)

    return {
        "tables": tables,
        "measures": all_measures,
        "calculated_columns": all_columns
    }


def build_dependency_graph(measures: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Build a dependency graph showing which measures depend on which."""
    # Create a map of measure name -> full measure info
    measure_map = {m["name"]: m for m in measures}

    dependency_graph = {}

    for measure in measures:
        measure_name = measure["name"]
        dependencies = []

        # Check which of the referenced names are actual measures
        for ref in measure["dependencies"]:
            if ref in measure_map:
                dependencies.append(ref)

        if dependencies:
            dependency_graph[measure_name] = dependencies

    return dependency_graph


def format_output(data: Dict[str, Any]) -> str:
    """Format extracted measure data as human-readable text."""
    output_lines = []

    output_lines.append("=" * 80)
    output_lines.append("POWER BI DATA MODEL - MEASURES AND COLUMNS")
    output_lines.append("=" * 80)
    output_lines.append("")

    # Summary
    output_lines.append(f"Tables: {len(data['tables'])}")
    output_lines.append(f"Measures: {len(data['measures'])}")
    output_lines.append(f"Calculated Columns: {len(data['calculated_columns'])}")
    output_lines.append("")

    # Group measures by table
    measures_by_table = {}
    for measure in data["measures"]:
        table = measure["table"]
        if table not in measures_by_table:
            measures_by_table[table] = []
        measures_by_table[table].append(measure)

    # Output measures by table
    output_lines.append("-" * 80)
    output_lines.append("MEASURES BY TABLE")
    output_lines.append("-" * 80)

    for table in sorted(measures_by_table.keys()):
        measures = measures_by_table[table]
        output_lines.append(f"\nTable: {table} ({len(measures)} measures)")
        output_lines.append("")

        for measure in measures:
            output_lines.append(f"  [{measure['name']}]")

            # Show first 200 chars of expression
            expr = measure["expression"]
            if len(expr) > 200:
                expr = expr[:200] + "..."

            output_lines.append(f"    Expression: {expr}")

            if measure["dependencies"]:
                output_lines.append(f"    Dependencies: {', '.join(measure['dependencies'])}")

            output_lines.append("")

    # Build and show dependency graph
    dependency_graph = build_dependency_graph(data["measures"])

    if dependency_graph:
        output_lines.append("-" * 80)
        output_lines.append("MEASURE DEPENDENCIES")
        output_lines.append("-" * 80)
        output_lines.append("")

        for measure, deps in sorted(dependency_graph.items()):
            output_lines.append(f"[{measure}] depends on:")
            for dep in deps:
                output_lines.append(f"  - [{dep}]")
            output_lines.append("")

    # Show calculated columns
    if data["calculated_columns"]:
        output_lines.append("-" * 80)
        output_lines.append("CALCULATED COLUMNS")
        output_lines.append("-" * 80)
        output_lines.append("")

        for column in data["calculated_columns"]:
            output_lines.append(f"Table: {column['table']}")
            output_lines.append(f"  Column: {column['name']}")

            expr = column["expression"]
            if len(expr) > 200:
                expr = expr[:200] + "..."

            output_lines.append(f"    Expression: {expr}")
            output_lines.append("")

    return "\n".join(output_lines)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python extract_measure_info.py <path_to_.SemanticModel_folder>")
        print("Example: python extract_measure_info.py 'C:/Projects/SalesReport/.SemanticModel'")
        sys.exit(1)

    semantic_model_folder = Path(sys.argv[1])

    if not semantic_model_folder.exists():
        print(f"Error: SemanticModel folder not found: {semantic_model_folder}")
        sys.exit(1)

    if not semantic_model_folder.is_dir():
        print(f"Error: Path is not a directory: {semantic_model_folder}")
        sys.exit(1)

    try:
        # Extract measures and columns
        data = get_all_measures_from_folder(semantic_model_folder)

        if not data["measures"] and not data["calculated_columns"]:
            print("No measures or calculated columns found in the semantic model.")
            sys.exit(0)

        # Output results
        output = format_output(data)
        print(output)

        # Also save as JSON
        import json
        json_output_path = semantic_model_folder.parent / "parsed_measures.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"\nJSON output saved to: {json_output_path}")

    except Exception as e:
        print(f"Error extracting measures: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
