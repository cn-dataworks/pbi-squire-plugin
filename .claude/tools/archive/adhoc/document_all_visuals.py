"""
Comprehensive documentation script for all Power BI report pages and visuals.
Systematically extracts visual metadata, configurations, and data bindings.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

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

def extract_measures_from_query(query_data: Any) -> List[str]:
    """Extract measure names from query transforms or projections."""
    measures = []

    if not query_data:
        return measures

    # Check Select projections
    if "Select" in query_data:
        for select_item in query_data["Select"]:
            if "Measure" in select_item:
                measure_expr = select_item["Measure"]
                if "Property" in measure_expr:
                    measures.append(measure_expr["Property"])

    return measures

def extract_columns_from_query(query_data: Any) -> List[str]:
    """Extract column names from query transforms or projections."""
    columns = []

    if not query_data:
        return columns

    # Check Select projections
    if "Select" in query_data:
        for select_item in query_data["Select"]:
            if "Column" in select_item:
                col_expr = select_item["Column"]
                if "Property" in col_expr:
                    columns.append(col_expr["Property"])

    return columns

def parse_visual_config(config_str: str) -> Dict:
    """Parse the stringified config JSON."""
    try:
        if config_str:
            return json.loads(config_str)
        return {}
    except:
        return {}

def extract_visual_title(config: Dict) -> str:
    """Extract visual title from config."""
    if "singleVisual" in config:
        if "vcObjects" in config["singleVisual"]:
            vc_objects = config["singleVisual"]["vcObjects"]
            if "title" in vc_objects:
                title_list = vc_objects["title"]
                if title_list and len(title_list) > 0:
                    title_props = title_list[0].get("properties", {})
                    if "text" in title_props:
                        text_expr = title_props["text"]
                        if "expr" in text_expr:
                            if "Literal" in text_expr["expr"]:
                                return text_expr["expr"]["Literal"].get("Value", "").strip("'\"")
    return ""

def document_visual(page_folder: str, page_name: str, visual_folder: str) -> Dict:
    """Extract comprehensive visual documentation."""
    visual_path = os.path.join(REPORT_PATH, "pages", page_folder, "visuals", visual_folder, "visual.json")

    with open(visual_path, 'r', encoding='utf-8') as f:
        visual_data = json.load(f)

    # Basic properties
    visual_type = visual_data.get("visualType", "unknown")
    x = visual_data.get("x", 0)
    y = visual_data.get("y", 0)
    width = visual_data.get("width", 0)
    height = visual_data.get("height", 0)
    tab_order = visual_data.get("tabOrder", 0)

    # Parse config
    config_str = visual_data.get("config", "")
    config = parse_visual_config(config_str)
    title = extract_visual_title(config)

    # Extract data bindings from query transforms
    measures = []
    columns = []

    if "query" in visual_data:
        query = visual_data["query"]

        # Extract from Commands (typical structure)
        if "Commands" in query:
            for command in query["Commands"]:
                if "SemanticQueryDataShapeCommand" in command:
                    sq_command = command["SemanticQueryDataShapeCommand"]
                    if "Query" in sq_command:
                        query_obj = sq_command["Query"]
                        measures.extend(extract_measures_from_query(query_obj))
                        columns.extend(extract_columns_from_query(query_obj))

    # Extract from dataTransforms if present
    if "dataTransforms" in visual_data:
        dt = visual_data["dataTransforms"]
        if "projections" in dt:
            for role, projection_list in dt["projections"].items():
                for proj in projection_list:
                    if "queryRef" in proj:
                        # This references a query binding
                        pass

    return {
        "visual_folder": visual_folder,
        "visual_type": visual_type,
        "title": title,
        "position": {"x": x, "y": y},
        "size": {"width": width, "height": height},
        "tab_order": tab_order,
        "measures": measures,
        "columns": columns,
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

    md.append("### B. Visual Current State Investigation")
    md.append("")
    md.append("**Status**: Documented - Comprehensive Inventory")
    md.append("")
    md.append("**Report Structure**: This Power BI report contains 9 pages with a total of {} visuals across all pages.".format(
        sum(len(p["visuals"]) for p in pages_data)
    ))
    md.append("")
    md.append("---")
    md.append("")

    for page_data in pages_data:
        page_name = page_data["page_name"]
        page_folder = page_data["page_folder"]
        visuals = page_data["visuals"]

        md.append(f"## Page: {page_name}")
        md.append("")
        md.append(f"**Page ID**: `{page_folder}`")
        md.append(f"**Total Visuals**: {len(visuals)}")
        md.append("")

        if len(visuals) == 0:
            md.append("*No visuals found on this page.*")
            md.append("")
            md.append("---")
            md.append("")
            continue

        for idx, visual in enumerate(visuals, 1):
            md.append(f"### Visual {idx}: {visual['title'] or '(Untitled)'}")
            md.append("")
            md.append(f"**Visual Type**: `{visual['visual_type']}`  ")
            md.append(f"**File Path**: [{visual['visual_folder']}/visual.json]({visual['file_path']})")
            md.append("")

            md.append("**Layout Properties**:")
            md.append(f"- **Position**: (x: {visual['position']['x']}, y: {visual['position']['y']})")
            md.append(f"- **Size**: {visual['size']['width']}px × {visual['size']['height']}px")
            md.append(f"- **Tab Order**: {visual['tab_order']}")
            md.append("")

            if visual['measures'] or visual['columns']:
                md.append("**Data Bindings**:")
                if visual['measures']:
                    md.append(f"- **Measures**: {', '.join([f'`{m}`' for m in visual['measures']])}")
                if visual['columns']:
                    md.append(f"- **Columns**: {', '.join([f'`{c}`' for c in visual['columns']])}")
                md.append("")
            else:
                md.append("**Data Bindings**: *(No measures or columns detected in query)*")
                md.append("")

            md.append("---")
            md.append("")

    return "\n".join(md)

def main():
    """Main execution."""
    print("Documenting all pages and visuals...")

    pages_documentation = []

    for page_folder, page_name in PAGE_ORDER:
        print(f"Processing page: {page_name} ({page_folder})")
        page_doc = document_page(page_folder, page_name)
        pages_documentation.append(page_doc)

    # Generate markdown
    markdown_output = generate_markdown_documentation(pages_documentation)

    # Save to output file
    output_path = r"c:\Users\anorthrup\Documents\power_bi_analyst\visual_inventory.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f"\nDocumentation complete! Output written to: {output_path}")
    print(f"Total pages documented: {len(pages_documentation)}")
    print(f"Total visuals documented: {sum(len(p['visuals']) for p in pages_documentation)}")

if __name__ == "__main__":
    main()
