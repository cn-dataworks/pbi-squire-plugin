"""
Parse Power BI Report (.Report) folder structure to extract pages, visuals, and layouts.

This script extracts:
- Page names and order
- Visual types and positions
- Data bindings (fields/measures used)
- Filters (page-level and visual-level)

Usage:
    python parse_pbir_pages.py <path_to_.Report_folder>

Example:
    python parse_pbir_pages.py "C:/Projects/SalesReport/.Report"
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any


def parse_report_json(report_folder: Path) -> Dict[str, Any]:
    """Parse the main report.json file to get high-level report structure."""
    report_json_path = report_folder / "report.json"

    if not report_json_path.exists():
        raise FileNotFoundError(f"report.json not found at {report_json_path}")

    with open(report_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_page_structure(page_folder: Path) -> Dict[str, Any]:
    """Parse a single page folder to extract visuals and layout."""
    page_data = {
        "page_name": page_folder.name,
        "visuals": [],
        "filters": []
    }

    # Parse each visual in the page
    for visual_folder in page_folder.iterdir():
        if visual_folder.is_dir():
            visual_json_path = visual_folder / "visual.json"

            if visual_json_path.exists():
                with open(visual_json_path, 'r', encoding='utf-8') as f:
                    visual_data = json.load(f)

                    visual_info = extract_visual_info(visual_data, visual_folder.name)
                    page_data["visuals"].append(visual_info)

    return page_data


def extract_visual_info(visual_json: Dict, visual_name: str) -> Dict[str, Any]:
    """Extract key information from a visual.json file."""
    visual_info = {
        "name": visual_name,
        "visual_type": "unknown",
        "position": {},
        "size": {},
        "data_bindings": [],
        "filters": [],
        "title": ""
    }

    # Extract visual type
    if "visualType" in visual_json:
        visual_info["visual_type"] = visual_json["visualType"]

    # Extract position and size
    if "position" in visual_json:
        visual_info["position"] = {
            "x": visual_json["position"].get("x", 0),
            "y": visual_json["position"].get("y", 0)
        }
        visual_info["size"] = {
            "width": visual_json["position"].get("width", 0),
            "height": visual_json["position"].get("height", 0)
        }

    # Extract title from config
    if "config" in visual_json:
        try:
            config = json.loads(visual_json["config"]) if isinstance(visual_json["config"], str) else visual_json["config"]

            # Try to find title in various config locations
            if "singleVisual" in config:
                title = config["singleVisual"].get("visualTitle", {})
                if "text" in title:
                    visual_info["title"] = title["text"]

            # Extract data bindings (fields/measures used)
            if "singleVisual" in config:
                visual_info["data_bindings"] = extract_data_bindings(config["singleVisual"])

        except (json.JSONDecodeError, KeyError):
            pass

    # Extract filters
    if "filters" in visual_json:
        visual_info["filters"] = visual_json["filters"]

    return visual_info


def extract_data_bindings(visual_config: Dict) -> List[Dict[str, str]]:
    """Extract data role bindings (fields/measures used in the visual)."""
    bindings = []

    # Look for data roles in various config structures
    if "prototypeQuery" in visual_config:
        prototype = visual_config["prototypeQuery"]

        # Extract from Select clause
        if "Select" in prototype:
            for select_item in prototype["Select"]:
                if "Column" in select_item:
                    column = select_item["Column"]
                    bindings.append({
                        "type": "column",
                        "expression": f"{column.get('Entity', '')}.{column.get('Property', '')}"
                    })
                elif "Measure" in select_item:
                    measure = select_item["Measure"]
                    bindings.append({
                        "type": "measure",
                        "expression": f"{measure.get('Expression', '')}"
                    })

    # Alternative: vcObjects structure
    if "vcObjects" in visual_config:
        vc_objects = visual_config["vcObjects"]

        for key, obj in vc_objects.items():
            if isinstance(obj, dict) and "properties" in obj:
                props = obj["properties"]

                # Look for dataRoles
                if "dataRoles" in props:
                    for role in props["dataRoles"]:
                        bindings.append({
                            "role": key,
                            "type": role.get("type", "unknown"),
                            "expression": role.get("displayName", "")
                        })

    return bindings


def get_all_pages(report_folder: Path) -> List[Dict[str, Any]]:
    """Get all pages from the .Report folder."""
    pages = []

    # Check if definition folder exists
    definition_folder = report_folder / "definition"

    if not definition_folder.exists():
        return pages

    # Look for pages folder
    pages_folder = definition_folder / "pages"

    if not pages_folder.exists():
        return pages

    # Parse each page folder
    for page_folder in sorted(pages_folder.iterdir()):
        if page_folder.is_dir():
            try:
                page_data = parse_page_structure(page_folder)
                pages.append(page_data)
            except Exception as e:
                print(f"Warning: Could not parse page {page_folder.name}: {e}", file=sys.stderr)

    return pages


def format_output(pages: List[Dict[str, Any]]) -> str:
    """Format the extracted page data as human-readable text."""
    output_lines = []

    output_lines.append("=" * 80)
    output_lines.append("POWER BI DASHBOARD STRUCTURE")
    output_lines.append("=" * 80)
    output_lines.append("")

    for i, page in enumerate(pages, 1):
        output_lines.append(f"PAGE {i}: {page['page_name']}")
        output_lines.append("-" * 80)
        output_lines.append(f"Visuals: {len(page['visuals'])}")
        output_lines.append("")

        for j, visual in enumerate(page['visuals'], 1):
            output_lines.append(f"  Visual {j}: {visual['name']}")
            output_lines.append(f"    Type: {visual['visual_type']}")

            if visual['title']:
                output_lines.append(f"    Title: {visual['title']}")

            output_lines.append(f"    Position: x={visual['position'].get('x', 0)}, y={visual['position'].get('y', 0)}")
            output_lines.append(f"    Size: {visual['size'].get('width', 0)} x {visual['size'].get('height', 0)}")

            if visual['data_bindings']:
                output_lines.append(f"    Data Bindings:")
                for binding in visual['data_bindings']:
                    output_lines.append(f"      - {binding.get('type', 'field')}: {binding.get('expression', '')}")

            if visual['filters']:
                output_lines.append(f"    Filters: {len(visual['filters'])} applied")

            output_lines.append("")

        output_lines.append("")

    return "\n".join(output_lines)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python parse_pbir_pages.py <path_to_.Report_folder>")
        print("Example: python parse_pbir_pages.py 'C:/Projects/SalesReport/.Report'")
        sys.exit(1)

    report_folder = Path(sys.argv[1])

    if not report_folder.exists():
        print(f"Error: Report folder not found: {report_folder}")
        sys.exit(1)

    if not report_folder.is_dir():
        print(f"Error: Path is not a directory: {report_folder}")
        sys.exit(1)

    try:
        # Parse all pages
        pages = get_all_pages(report_folder)

        if not pages:
            print("No pages found in the report. Check that the .Report/definition/pages folder exists.")
            sys.exit(0)

        # Output results
        output = format_output(pages)
        print(output)

        # Also output as JSON for programmatic use
        json_output_path = report_folder.parent / "parsed_pages.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent=2)

        print(f"\nJSON output saved to: {json_output_path}")

    except Exception as e:
        print(f"Error parsing report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
