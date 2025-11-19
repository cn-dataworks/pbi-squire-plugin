"""
Comprehensive documentation script for all Power BI report pages and visuals - Version 2.
Correctly extracts visual metadata, configurations, and data bindings from PBIR structure.
"""

import json
import os
from typing import Dict, List, Any, Set

# Page mapping from pages.json
PAGE_ORDER = [
    ("4ab136f25e808ce3a371", "Overview"),
    ("08b3c88d020c5baa6c65", "Customer Details"),
    ("2ec619e5e311cee3581c", "YOY Retention"),
    ("978e18d9eba5d131907d", "Customer Details"),
    ("77dabfc828ab083de413", "Retention by Line of Business"),
    ("713e4fedb098b23b400b", "Retention by Line of Business Details"),
    ("2313a1ac604f76a1888a", "Rep View"),
    ("ReportSectionab79a008045483851584", "Glossary"),
    ("35a1f0897cd1110b7c8a", "Validation - Customers")
]

REPORT_PATH = r"C:\Users\anorthrup\Desktop\Power BI Projects\customer retention report\Customer Retention Report.Report\definition"

def extract_title_from_visual_container(visual_container_objects: Dict) -> str:
    """Extract title from visualContainerObjects."""
    if not visual_container_objects or "title" not in visual_container_objects:
        return ""

    title_list = visual_container_objects["title"]
    if title_list and len(title_list) > 0:
        title_props = title_list[0].get("properties", {})
        if "text" in title_props:
            text_expr = title_props.get("text", {})
            if "expr" in text_expr:
                if "Literal" in text_expr["expr"]:
                    return text_expr["expr"]["Literal"].get("Value", "").strip("'\"")
    return ""

def extract_textbox_content(visual_objects: Dict) -> str:
    """Extract text content from textbox visuals."""
    if not visual_objects or "general" not in visual_objects:
        return ""

    general_list = visual_objects["general"]
    if general_list and len(general_list) > 0:
        props = general_list[0].get("properties", {})
        if "paragraphs" in props:
            paragraphs = props["paragraphs"]
            text_parts = []
            for para in paragraphs:
                if "textRuns" in para:
                    for run in para["textRuns"]:
                        if "value" in run:
                            text_parts.append(run["value"])
            return " ".join(text_parts)[:200]  # Limit to 200 chars
    return ""

def extract_fields_from_projection(projection: Dict, fields: Set[str], tables: Set[str]):
    """Recursively extract field names from projection structure."""
    if isinstance(projection, dict):
        # Check for direct Column reference
        if "Column" in projection:
            col_data = projection["Column"]
            if "Property" in col_data:
                fields.add(col_data["Property"])
            if "Expression" in col_data and "SourceRef" in col_data["Expression"]:
                tables.add(col_data["Expression"]["SourceRef"].get("Entity", ""))

        # Check for Measure reference
        if "Measure" in projection:
            measure_data = projection["Measure"]
            if "Property" in measure_data:
                fields.add(measure_data["Property"])
            if "Expression" in measure_data and "SourceRef" in measure_data["Expression"]:
                tables.add(measure_data["Expression"]["SourceRef"].get("Entity", ""))

        # Check for Aggregation wrapper
        if "Aggregation" in projection:
            extract_fields_from_projection(projection["Aggregation"], fields, tables)

        # Check for field references
        if "field" in projection:
            extract_fields_from_projection(projection["field"], fields, tables)

        # Recursively check Expression
        if "Expression" in projection:
            extract_fields_from_projection(projection["Expression"], fields, tables)

def extract_data_bindings(visual_data: Dict) -> Dict[str, Any]:
    """Extract comprehensive data bindings from visual query structure."""
    fields = set()
    tables = set()

    visual_obj = visual_data.get("visual", {})
    query = visual_obj.get("query", {})

    # Extract from queryState projections
    if "queryState" in query:
        query_state = query["queryState"]
        for role_name, role_data in query_state.items():
            if "projections" in role_data:
                for projection in role_data["projections"]:
                    extract_fields_from_projection(projection, fields, tables)

    # Extract from dataTransforms if present
    if "dataTransforms" in visual_obj:
        dt = visual_obj["dataTransforms"]
        if "projections" in dt:
            for role, projection_list in dt["projections"].items():
                for proj in projection_list:
                    extract_fields_from_projection(proj, fields, tables)

    return {
        "fields": sorted(list(fields)),
        "tables": sorted(list(tables))
    }

def document_visual(page_folder: str, page_name: str, visual_folder: str) -> Dict:
    """Extract comprehensive visual documentation."""
    visual_path = os.path.join(REPORT_PATH, "pages", page_folder, "visuals", visual_folder, "visual.json")

    with open(visual_path, 'r', encoding='utf-8') as f:
        visual_container = json.load(f)

    # Extract position properties
    position = visual_container.get("position", {})
    x = position.get("x", 0)
    y = position.get("y", 0)
    width = position.get("width", 0)
    height = position.get("height", 0)
    tab_order = position.get("tabOrder", 0)

    # Extract visual properties
    visual_obj = visual_container.get("visual", {})
    visual_type = visual_obj.get("visualType", "unknown")

    # Extract title from visualContainerObjects
    visual_container_objects = visual_obj.get("visualContainerObjects", {})
    title = extract_title_from_visual_container(visual_container_objects)

    # For textboxes, extract content as title if no title set
    text_content = ""
    if visual_type == "textbox":
        visual_objects = visual_obj.get("objects", {})
        text_content = extract_textbox_content(visual_objects)
        if not title and text_content:
            title = text_content[:50] + ("..." if len(text_content) > 50 else "")

    # Extract data bindings
    data_bindings = extract_data_bindings(visual_container)

    return {
        "visual_folder": visual_folder,
        "visual_type": visual_type,
        "title": title,
        "text_content": text_content if visual_type == "textbox" else "",
        "position": {"x": round(x, 2), "y": round(y, 2)},
        "size": {"width": round(width, 2), "height": round(height, 2)},
        "tab_order": tab_order,
        "fields": data_bindings["fields"],
        "tables": data_bindings["tables"],
        "file_path": f"Customer Retention Report.Report/definition/pages/{page_folder}/visuals/{visual_folder}/visual.json"
    }

def document_page(page_folder: str, page_name: str) -> Dict:
    """Document all visuals on a page."""
    visuals_path = os.path.join(REPORT_PATH, "pages", page_folder, "visuals")

    if not os.path.exists(visuals_path):
        return {
            "page_name": page_name,
            "page_folder": page_folder,
            "visuals": []
        }

    visual_folders = [f for f in os.listdir(visuals_path) if os.path.isdir(os.path.join(visuals_path, f))]

    visuals = []
    for visual_folder in visual_folders:
        try:
            visual_doc = document_visual(page_folder, page_name, visual_folder)
            visuals.append(visual_doc)
        except Exception as e:
            print(f"Error documenting visual {visual_folder} on page {page_name}: {e}")

    # Sort by tab order
    visuals.sort(key=lambda v: v.get("tab_order", 999))

    return {
        "page_name": page_name,
        "page_folder": page_folder,
        "visuals": visuals
    }

def generate_markdown_documentation(pages_data: List[Dict]) -> str:
    """Generate comprehensive markdown documentation."""
    md = []

    total_visuals = sum(len(p["visuals"]) for p in pages_data)
    total_data_visuals = sum(1 for p in pages_data for v in p["visuals"] if v["fields"])

    md.append("### B. Visual Current State Investigation")
    md.append("")
    md.append("**Status**: Documented - Comprehensive Inventory")
    md.append("")
    md.append(f"**Report Structure**: This Power BI report contains {len(pages_data)} pages with a total of {total_visuals} visuals ({total_data_visuals} data-bound visuals, {total_visuals - total_data_visuals} static elements).")
    md.append("")
    md.append("---")
    md.append("")

    for page_data in pages_data:
        page_name = page_data["page_name"]
        page_folder = page_data["page_folder"]
        visuals = page_data["visuals"]

        md.append(f"## Page: {page_name}")
        md.append("")
        md.append(f"**Page ID**: `{page_folder}`  ")
        md.append(f"**Total Visuals**: {len(visuals)} ({sum(1 for v in visuals if v['fields'])} data-bound)")
        md.append("")

        if len(visuals) == 0:
            md.append("*No visuals found on this page.*")
            md.append("")
            md.append("---")
            md.append("")
            continue

        for idx, visual in enumerate(visuals, 1):
            # Determine display name
            display_name = visual['title'] if visual['title'] else f"({visual['visual_type']})"

            md.append(f"### Visual {idx}: {display_name}")
            md.append("")
            md.append(f"**Visual Type**: `{visual['visual_type']}`  ")
            md.append(f"**File Path**: [{visual['visual_folder']}/visual.json]({visual['file_path']})")
            md.append("")

            # Add textbox content if applicable
            if visual['text_content'] and len(visual['text_content']) > 50:
                md.append(f"**Content**: {visual['text_content'][:150]}...")
                md.append("")

            md.append("**Layout Properties**:")
            md.append(f"- **Position**: (x: {visual['position']['x']}, y: {visual['position']['y']})")
            md.append(f"- **Size**: {visual['size']['width']}px × {visual['size']['height']}px")
            md.append(f"- **Tab Order**: {visual['tab_order']}")
            md.append("")

            if visual['fields'] or visual['tables']:
                md.append("**Data Bindings**:")
                if visual['tables']:
                    md.append(f"- **Tables**: {', '.join([f'`{t}`' for t in visual['tables']])}")
                if visual['fields']:
                    md.append(f"- **Fields/Measures**: {', '.join([f'`{f}`' for f in visual['fields']])}")
                md.append("")
            else:
                if visual['visual_type'] not in ['textbox', 'shape', 'image', 'actionButton']:
                    md.append("**Data Bindings**: *(No fields detected)*")
                    md.append("")

            md.append("---")
            md.append("")

        md.append("")

    return "\n".join(md)

def main():
    """Main execution."""
    print("Documenting all pages and visuals (Version 2 - Enhanced)...")

    pages_documentation = []

    for page_folder, page_name in PAGE_ORDER:
        print(f"Processing page: {page_name} ({page_folder})")
        page_doc = document_page(page_folder, page_name)
        pages_documentation.append(page_doc)
        print(f"  - Found {len(page_doc['visuals'])} visuals")

    # Generate markdown
    markdown_output = generate_markdown_documentation(pages_documentation)

    # Save to output file
    output_path = r"c:\Users\anorthrup\Documents\power_bi_analyst\visual_inventory_v2.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f"\nDocumentation complete! Output written to: {output_path}")
    print(f"Total pages documented: {len(pages_documentation)}")
    print(f"Total visuals documented: {sum(len(p['visuals']) for p in pages_documentation)}")

    # Summary statistics
    all_measures = set()
    all_tables = set()
    visual_types = {}

    for page in pages_documentation:
        for visual in page["visuals"]:
            # Count visual types
            vtype = visual["visual_type"]
            visual_types[vtype] = visual_types.get(vtype, 0) + 1

            # Collect unique measures and tables
            all_measures.update(visual["fields"])
            all_tables.update(visual["tables"])

    print(f"\nSummary:")
    print(f"  Unique measures/fields referenced: {len(all_measures)}")
    print(f"  Unique tables referenced: {len(all_tables)}")
    print(f"\nVisual Type Distribution:")
    for vtype, count in sorted(visual_types.items(), key=lambda x: -x[1]):
        print(f"    {vtype}: {count}")

if __name__ == "__main__":
    main()
