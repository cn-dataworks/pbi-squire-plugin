"""
Main orchestrator for generating business-friendly Power BI dashboard analysis.

This script:
1. Validates the Power BI project structure
2. Extracts page and visual information from .Report folder
3. Extracts measure definitions from .SemanticModel folder
4. Generates a business-friendly markdown analysis report

Usage:
    python generate_dashboard_analysis.py <path_to_pbip_project> <output_folder>

Example:
    python generate_dashboard_analysis.py "C:/Projects/SalesReport" "C:/Output/analysis"
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import the parsing scripts
import parse_pbir_pages
import extract_measure_info


def validate_project_structure(project_path: Path) -> Dict[str, Any]:
    """Validate that the project has the required structure."""
    validation_result = {
        "valid": False,
        "has_semantic_model": False,
        "has_report": False,
        "semantic_model_path": None,
        "report_path": None,
        "errors": []
    }

    # Check for .SemanticModel folder
    semantic_model_candidates = list(project_path.glob("*.SemanticModel"))

    if semantic_model_candidates:
        validation_result["has_semantic_model"] = True
        validation_result["semantic_model_path"] = semantic_model_candidates[0]
    else:
        validation_result["errors"].append("No .SemanticModel folder found")

    # Check for .Report folder
    report_candidates = list(project_path.glob("*.Report"))

    if report_candidates:
        validation_result["has_report"] = True
        validation_result["report_path"] = report_candidates[0]
    else:
        validation_result["errors"].append("No .Report folder found - page/visual analysis will be limited")

    # Project is valid if it has at least semantic model
    validation_result["valid"] = validation_result["has_semantic_model"]

    return validation_result


def extract_dashboard_data(project_path: Path) -> Dict[str, Any]:
    """Extract all relevant data from the Power BI project."""
    data = {
        "project_path": str(project_path),
        "timestamp": datetime.now().isoformat(),
        "pages": [],
        "measures": [],
        "calculated_columns": [],
        "tables": []
    }

    # Validate structure
    validation = validate_project_structure(project_path)

    if not validation["valid"]:
        raise ValueError(f"Invalid project structure: {', '.join(validation['errors'])}")

    # Extract measures from .SemanticModel
    if validation["has_semantic_model"]:
        semantic_model_path = validation["semantic_model_path"]
        measure_data = extract_measure_info.get_all_measures_from_folder(semantic_model_path)

        data["measures"] = measure_data.get("measures", [])
        data["calculated_columns"] = measure_data.get("calculated_columns", [])
        data["tables"] = measure_data.get("tables", [])

    # Extract pages and visuals from .Report
    if validation["has_report"]:
        report_path = validation["report_path"]
        pages = parse_pbir_pages.get_all_pages(report_path)
        data["pages"] = pages

    return data


def generate_markdown_report(data: Dict[str, Any], template_path: Path, output_path: Path) -> None:
    """Generate the markdown analysis report using the template."""
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace placeholders
    report = template

    # Basic info
    report = report.replace("{{PROJECT_PATH}}", data["project_path"])
    report = report.replace("{{TIMESTAMP}}", data["timestamp"])
    report = report.replace("{{NUM_PAGES}}", str(len(data["pages"])))
    report = report.replace("{{NUM_MEASURES}}", str(len(data["measures"])))
    report = report.replace("{{NUM_TABLES}}", str(len(data["tables"])))

    # Generate dashboard overview
    overview = generate_dashboard_overview(data)
    report = report.replace("{{DASHBOARD_OVERVIEW}}", overview)

    # Generate page-by-page analysis
    page_analysis = generate_page_analysis(data["pages"], data["measures"])
    report = report.replace("{{PAGE_ANALYSIS}}", page_analysis)

    # Generate metrics glossary
    metrics_glossary = generate_metrics_glossary(data["measures"])
    report = report.replace("{{METRICS_GLOSSARY}}", metrics_glossary)

    # Generate filter guide
    filter_guide = generate_filter_guide(data["pages"])
    report = report.replace("{{FILTER_GUIDE}}", filter_guide)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def generate_dashboard_overview(data: Dict[str, Any]) -> str:
    """Generate high-level dashboard overview section."""
    lines = []

    lines.append(f"This Power BI dashboard contains {len(data['pages'])} page(s) with {len(data['measures'])} metric(s) defined across {len(data['tables'])} table(s).")
    lines.append("")

    if data["pages"]:
        lines.append("**Pages:**")
        for i, page in enumerate(data["pages"], 1):
            lines.append(f"{i}. {page['page_name']} ({len(page['visuals'])} visuals)")

    return "\n".join(lines)


def generate_page_analysis(pages: List[Dict[str, Any]], measures: List[Dict[str, Any]]) -> str:
    """Generate detailed page-by-page analysis section."""
    lines = []

    # Create measure lookup
    measure_map = {m["name"]: m for m in measures}

    for i, page in enumerate(pages, 1):
        lines.append(f"### {i}. {page['page_name']}")
        lines.append("")

        # Page purpose (inferred from name)
        lines.append("**Purpose:** *(Inferred from page name and visuals)*")
        lines.append("")

        # List visuals
        lines.append(f"**Visuals ({len(page['visuals'])}):**")
        lines.append("")

        for j, visual in enumerate(page['visuals'], 1):
            lines.append(f"**Visual {j}: {visual.get('title', visual['name'])}**")
            lines.append(f"- **Type:** {visual['visual_type']}")
            lines.append(f"- **Position:** x={visual['position'].get('x', 0)}, y={visual['position'].get('y', 0)}")
            lines.append(f"- **Size:** {visual['size'].get('width', 0)} x {visual['size'].get('height', 0)}")

            # Data bindings
            if visual.get('data_bindings'):
                lines.append("- **Data:**")
                for binding in visual['data_bindings']:
                    binding_type = binding.get('type', 'field')
                    expression = binding.get('expression', 'unknown')
                    lines.append(f"  - {binding_type.title()}: {expression}")

            # Filters
            if visual.get('filters'):
                lines.append(f"- **Filters:** {len(visual['filters'])} applied")

            lines.append("")

        # Page filters
        if page.get('filters'):
            lines.append("**Page-Level Filters:**")
            lines.append(f"- {len(page['filters'])} filter(s) applied to all visuals on this page")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def generate_metrics_glossary(measures: List[Dict[str, Any]]) -> str:
    """Generate business-friendly metrics glossary."""
    lines = []

    # Build dependency graph
    dependency_graph = extract_measure_info.build_dependency_graph(measures)

    # Group by table
    measures_by_table = {}
    for measure in measures:
        table = measure["table"]
        if table not in measures_by_table:
            measures_by_table[table] = []
        measures_by_table[table].append(measure)

    for table in sorted(measures_by_table.keys()):
        lines.append(f"#### {table}")
        lines.append("")

        for measure in sorted(measures_by_table[table], key=lambda m: m["name"]):
            lines.append(f"**{measure['name']}**")
            lines.append("")

            # Show DAX expression (truncated)
            expr = measure["expression"]
            if len(expr) > 300:
                expr = expr[:300] + "..."

            lines.append("```dax")
            lines.append(expr)
            lines.append("```")
            lines.append("")

            # Show dependencies
            if measure["name"] in dependency_graph:
                deps = dependency_graph[measure["name"]]
                lines.append(f"- **Dependencies:** {', '.join(deps)}")
                lines.append("")

            # Business definition placeholder
            lines.append("- **Business Definition:** *(AI-generated explanation should be added here based on DAX pattern recognition)*")
            lines.append("")

    return "\n".join(lines)


def generate_filter_guide(pages: List[Dict[str, Any]]) -> str:
    """Generate filter and interaction guide."""
    lines = []

    lines.append("This section documents filters and interactions available in the dashboard.")
    lines.append("")

    # Extract common patterns
    lines.append("### Page Filters")
    lines.append("")

    for page in pages:
        if page.get('filters'):
            lines.append(f"**{page['page_name']}:** {len(page['filters'])} page-level filter(s)")

    lines.append("")
    lines.append("### Visual Interactions")
    lines.append("")
    lines.append("*(Cross-filtering and drillthrough behavior should be documented here based on visual analysis)*")

    return "\n".join(lines)


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python generate_dashboard_analysis.py <path_to_pbip_project> <output_folder>")
        print("Example: python generate_dashboard_analysis.py 'C:/Projects/SalesReport' 'C:/Output'")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    output_folder = Path(sys.argv[2])

    if not project_path.exists():
        print(f"Error: Project path not found: {project_path}")
        sys.exit(1)

    # Create output folder
    output_folder.mkdir(parents=True, exist_ok=True)

    # Find template
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "assets" / "analysis_report_template.md"

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)

    try:
        # Extract all data
        print("Extracting dashboard data...")
        data = extract_dashboard_data(project_path)

        # Generate report
        print("Generating markdown report...")
        output_path = output_folder / "dashboard_analysis.md"
        generate_markdown_report(data, template_path, output_path)

        print(f"\n✓ Analysis complete!")
        print(f"Report saved to: {output_path}")

        # Also save raw JSON data
        json_path = output_folder / "dashboard_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"Raw data saved to: {json_path}")

    except Exception as e:
        print(f"Error generating analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
