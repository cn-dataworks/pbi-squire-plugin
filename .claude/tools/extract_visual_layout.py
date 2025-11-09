"""
Extract and analyze visual layout from Power BI Report (.Report) pages.

This tool reads visual.json files from a Power BI project page and generates
a detailed layout report showing visual positions, sizes, types, and data fields.

Usage:
    python extract_visual_layout.py <report_path> <page_id> [options]

Arguments:
    report_path: Path to .Report folder (e.g., "project.Report")
    page_id: Page folder name (e.g., "feaad185bc0ca0d442fb")
             Use --list-pages to see available pages

Options:
    --list-pages: List all available page IDs in the report
    --output <file>: Write report to file instead of stdout
    --json: Output as JSON instead of formatted report

Examples:
    # List available pages
    python extract_visual_layout.py "PSSR Commissions.Report" --list-pages

    # Analyze specific page
    python extract_visual_layout.py "PSSR Commissions.Report" "feaad185bc0ca0d442fb"

    # Save to file
    python extract_visual_layout.py "PSSR Commissions.Report" "feaad185bc0ca0d442fb" --output layout.txt

    # Get JSON output
    python extract_visual_layout.py "PSSR Commissions.Report" "feaad185bc0ca0d442fb" --json
"""

import json
import sys
import argparse
from pathlib import Path


def list_pages(report_path):
    """List all available pages in the report."""
    pages_path = Path(report_path) / "definition" / "pages"

    if not pages_path.exists():
        print(f"Error: Pages directory not found at {pages_path}", file=sys.stderr)
        return []

    pages = []
    for page_dir in sorted(pages_path.iterdir()):
        if page_dir.is_dir():
            # Try to get page display name from page.json
            page_json = page_dir / "page.json"
            display_name = page_dir.name

            if page_json.exists():
                try:
                    with open(page_json, 'r', encoding='utf-8') as f:
                        page_data = json.load(f)
                        display_name = page_data.get('displayName', page_dir.name)
                except:
                    pass

            pages.append({
                'id': page_dir.name,
                'name': display_name
            })

    return pages


def extract_visual_layout(report_path, page_id):
    """Extract visual layout data from a specific page."""
    visuals_path = Path(report_path) / "definition" / "pages" / page_id / "visuals"

    if not visuals_path.exists():
        raise FileNotFoundError(f"Visuals directory not found: {visuals_path}")

    visual_data = []

    # Iterate through all visual containers
    for visual_dir in sorted(visuals_path.iterdir()):
        if visual_dir.is_dir():
            visual_json_path = visual_dir / "visual.json"
            if visual_json_path.exists():
                with open(visual_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                container_id = data.get("name", "unknown")
                position = data.get("position", {})
                visual = data.get("visual", {})

                # Extract basic properties
                visual_type = visual.get("visualType", "unknown")
                x = position.get("x", 0)
                y = position.get("y", 0)
                width = position.get("width", 0)
                height = position.get("height", 0)
                z = position.get("z", 0)
                tab_order = position.get("tabOrder", 0)

                # Extract title from visualContainerObjects
                title = "No title"
                vc_objects = visual.get("visualContainerObjects", {})
                if "title" in vc_objects:
                    title_obj = vc_objects["title"]
                    if isinstance(title_obj, list) and len(title_obj) > 0:
                        title_props = title_obj[0].get("properties", {})
                        text_expr = title_props.get("text", {}).get("expr", {})
                        if "Literal" in text_expr:
                            title = text_expr["Literal"].get("Value", "No title").strip("'")

                # Extract data fields
                query = visual.get("query", {})
                query_state = query.get("queryState", {})
                fields = []

                for role, role_data in query_state.items():
                    if isinstance(role_data, dict) and "projections" in role_data:
                        for projection in role_data["projections"]:
                            field_info = projection.get("field", {})
                            display_name = projection.get("displayName") or projection.get("nativeQueryRef", "")

                            # Determine if it's a measure or column
                            if "Measure" in field_info:
                                measure_prop = field_info["Measure"].get("Property", "")
                                fields.append(f"[Measure] {measure_prop}" + (f" as '{display_name}'" if display_name else ""))
                            elif "Column" in field_info:
                                col_prop = field_info["Column"].get("Property", "")
                                entity = field_info["Column"].get("Expression", {}).get("SourceRef", {}).get("Entity", "")
                                fields.append(f"[Column] {entity}.{col_prop}" + (f" as '{display_name}'" if display_name else ""))

                # Check if it's a slicer
                is_slicer = visual_type == "slicer"

                # Parent group
                parent_group = data.get("parentGroupName", "None")

                visual_data.append({
                    "container_id": container_id,
                    "visual_type": visual_type,
                    "title": title,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "z_index": z,
                    "tab_order": tab_order,
                    "fields": fields,
                    "is_slicer": is_slicer,
                    "parent_group": parent_group
                })

    # Sort by y coordinate (top to bottom), then x (left to right)
    visual_data.sort(key=lambda v: (v["y"], v["x"]))

    return visual_data


def format_report(visual_data, page_id):
    """Generate formatted text report."""
    lines = []

    lines.append("=" * 100)
    lines.append(f"Visual Layout Report - Page ID: {page_id}")
    lines.append(f"Total Visuals: {len(visual_data)}")
    lines.append("=" * 100)
    lines.append("")

    lines.append("CANVAS DIMENSIONS: 1280px (width) x 720px (height)")
    lines.append("")

    # Find existing slicers
    slicers = [v for v in visual_data if v["is_slicer"]]
    if slicers:
        lines.append(f"EXISTING SLICERS ({len(slicers)}):")
        for slicer in slicers:
            lines.append(f"  - {slicer['title']} at ({slicer['x']}, {slicer['y']}) - {slicer['width']}x{slicer['height']}")
    else:
        lines.append("NO EXISTING SLICERS FOUND")

    lines.append("")
    lines.append("=" * 100)
    lines.append("VISUAL INVENTORY (sorted top-to-bottom, left-to-right)")
    lines.append("=" * 100)
    lines.append("")

    for idx, v in enumerate(visual_data, 1):
        lines.append(f"{idx}. {v['visual_type'].upper()} - {v['title']}")
        lines.append(f"   Container ID: {v['container_id']}")
        lines.append(f"   Position: ({v['x']:.1f}, {v['y']:.1f})")
        lines.append(f"   Size: {v['width']:.1f}px × {v['height']:.1f}px")
        lines.append(f"   Z-index: {v['z_index']} | Tab Order: {v['tab_order']}")
        if v['parent_group'] != "None":
            lines.append(f"   Parent Group: {v['parent_group']}")
        if v['fields']:
            lines.append(f"   Data Fields ({len(v['fields'])}):")
            for field in v['fields'][:5]:  # Show first 5 fields
                lines.append(f"      - {field}")
            if len(v['fields']) > 5:
                lines.append(f"      ... and {len(v['fields']) - 5} more fields")
        lines.append("")

    # Identify available space at the top
    lines.append("=" * 100)
    lines.append("AVAILABLE SPACE ANALYSIS FOR NEW SLICER")
    lines.append("=" * 100)
    lines.append("")

    # Find the minimum Y coordinate of actual content (excluding full-width backgrounds)
    content_visuals = [v for v in visual_data if v['visual_type'] not in ['shape'] or v['width'] < 1280]
    if content_visuals:
        min_y = min(v['y'] for v in content_visuals)
        lines.append(f"Top content starts at Y = {min_y:.1f}px")
        lines.append(f"Available space at top: 0 to {min_y:.1f}px (Height: {min_y:.1f}px)")
        lines.append("")
        lines.append("RECOMMENDATION:")
        lines.append(f"  Place new slicer at: X=10, Y=10")
        lines.append(f"  Suggested size: 300px (width) × 60px (height)")
        lines.append(f"  This leaves margin and aligns with typical Power BI slicer dimensions")
    else:
        lines.append("Unable to determine available space")

    lines.append("")
    lines.append("=" * 100)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract and analyze visual layout from Power BI Report pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("report_path", nargs='?', help="Path to .Report folder")
    parser.add_argument("page_id", nargs='?', help="Page folder name/ID")
    parser.add_argument("--list-pages", action="store_true", help="List all available pages")
    parser.add_argument("--output", help="Write report to file instead of stdout")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Handle list pages command
    if args.list_pages:
        if not args.report_path:
            print("Error: report_path required with --list-pages", file=sys.stderr)
            sys.exit(1)

        pages = list_pages(args.report_path)

        if not pages:
            print("No pages found", file=sys.stderr)
            sys.exit(1)

        print(f"\nAvailable pages in {args.report_path}:")
        print("=" * 80)
        for page in pages:
            print(f"  ID: {page['id']}")
            print(f"  Name: {page['name']}")
            print("-" * 80)

        sys.exit(0)

    # Validate required arguments
    if not args.report_path or not args.page_id:
        parser.print_help()
        sys.exit(1)

    try:
        # Extract visual data
        visual_data = extract_visual_layout(args.report_path, args.page_id)

        # Generate output
        if args.json:
            output = json.dumps(visual_data, indent=2)
        else:
            output = format_report(visual_data, args.page_id)

        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report written to {args.output}")
        else:
            print(output)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
