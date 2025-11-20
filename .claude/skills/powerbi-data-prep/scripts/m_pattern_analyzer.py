#!/usr/bin/env python3
"""
M Code Pattern Analyzer

Scans Power BI project TMDL files to discover M code patterns, naming conventions,
and coding styles to ensure new transformations follow project standards.

Usage:
    python m_pattern_analyzer.py "<project-path>"
    python m_pattern_analyzer.py "<project-path>" --output "<report-file>"
"""

import sys
import os
import re
import argparse
from pathlib import Path
from collections import Counter, defaultdict
import json

class MCodePatternAnalyzer:
    """Analyzer for discovering M code patterns in TMDL files."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.tmdl_files = list(self.project_path.rglob('*.tmdl'))

        if not self.tmdl_files:
            raise ValueError(f"No TMDL files found in {project_path}")

        self.partitions = []
        self.patterns = {
            'naming': defaultdict(list),
            'transformations': defaultdict(list),
            'organization': defaultdict(list),
            'error_handling': defaultdict(list),
            'parameters': {}
        }

    def analyze(self):
        """Run full analysis."""
        print(f"Analyzing {len(self.tmdl_files)} TMDL files...\n")

        # Extract all partitions
        for tmdl_file in self.tmdl_files:
            self._extract_partitions(tmdl_file)

        print(f"Found {len(self.partitions)} M code partitions\n")

        # Analyze patterns
        self._analyze_naming()
        self._analyze_transformations()
        self._analyze_organization()
        self._analyze_error_handling()
        self._analyze_parameters()

        return self.patterns

    def _extract_partitions(self, tmdl_file):
        """Extract M code partitions from TMDL file."""
        content = tmdl_file.read_text(encoding='utf-8')
        lines = content.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i]

            # Find partition declaration
            match = re.match(r'^\s*partition\s+\'([^\']+)\'\s*=\s*m\s*$', line)
            if match:
                partition_name = match.group(1)

                # Extract M code (find source = and collect until next partition or table)
                m_code_lines = []
                j = i + 1
                in_m_code = False

                while j < len(lines):
                    current_line = lines[j]

                    # Start of M code
                    if re.match(r'^\s*source\s*=\s*$', current_line):
                        in_m_code = True
                        j += 1
                        continue

                    # End of partition (next partition or table)
                    if re.match(r'^\s*partition\s+', current_line) or re.match(r'^table\s+', current_line):
                        break

                    if in_m_code:
                        m_code_lines.append(current_line)

                    j += 1

                self.partitions.append({
                    'name': partition_name,
                    'file': tmdl_file.name,
                    'm_code': '\n'.join(m_code_lines),
                    'lines': m_code_lines
                })

                i = j
            else:
                i += 1

    def _analyze_naming(self):
        """Analyze naming conventions."""
        step_names = []
        step_styles = Counter()

        for partition in self.partitions:
            # Extract step names from let-in blocks
            for line in partition['lines']:
                # Match: StepName = ...
                match = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
                if match:
                    step_name = match.group(1)

                    # Skip M keywords
                    if step_name.lower() in ['let', 'in', 'each']:
                        continue

                    step_names.append(step_name)

                    # Classify style
                    if re.match(r'^#"', step_name):
                        step_styles['Default (Power Query)'] += 1
                    elif re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', step_name):
                        step_styles['PascalCase'] += 1
                    elif re.match(r'^[a-z]+(?:_[a-z]+)*$', step_name):
                        step_styles['snake_case'] += 1
                    elif re.match(r'^[a-z]+(?:[A-Z][a-z]+)*$', step_name):
                        step_styles['camelCase'] += 1
                    else:
                        step_styles['Mixed/Other'] += 1

        # Store results
        total_steps = len(step_names)
        self.patterns['naming']['step_names'] = step_names[:10]  # Sample
        self.patterns['naming']['step_styles'] = {
            style: {
                'count': count,
                'percentage': round(count / total_steps * 100, 1) if total_steps > 0 else 0
            }
            for style, count in step_styles.most_common()
        }

    def _analyze_transformations(self):
        """Analyze common transformation patterns."""
        transform_patterns = Counter()

        for partition in self.partitions:
            m_code = partition['m_code']

            # Detect common functions
            if 'Sql.Database(' in m_code:
                transform_patterns['SQL Database Connection'] += 1
            if 'Table.SelectRows(' in m_code:
                transform_patterns['Filter Rows (SelectRows)'] += 1
            if 'Table.SelectColumns(' in m_code:
                transform_patterns['Select Columns'] += 1
            if 'Table.RemoveColumns(' in m_code:
                transform_patterns['Remove Columns'] += 1
            if 'Table.AddColumn(' in m_code:
                transform_patterns['Add Custom Column'] += 1
            if 'Table.TransformColumnTypes(' in m_code:
                transform_patterns['Transform Column Types'] += 1
            if 'Table.NestedJoin(' in m_code or 'Table.Join(' in m_code:
                transform_patterns['Merge/Join Tables'] += 1
            if 'Table.Combine(' in m_code:
                transform_patterns['Append Tables'] += 1
            if 'Table.Group(' in m_code:
                transform_patterns['Group By'] += 1
            if '#date(' in m_code:
                transform_patterns['Date Literals'] += 1

        total_partitions = len(self.partitions)
        self.patterns['transformations'] = {
            pattern: {
                'count': count,
                'percentage': round(count / total_partitions * 100, 1)
            }
            for pattern, count in transform_patterns.most_common()
        }

    def _analyze_organization(self):
        """Analyze code organization patterns."""
        has_comments = 0
        has_blank_lines = 0
        comment_style = Counter()

        for partition in self.partitions:
            m_code = partition['m_code']

            # Check for comments
            if '//' in m_code:
                has_comments += 1
                # Count single-line vs multi-line comments
                if '//' in m_code:
                    comment_style['Single-line (//)'] += 1
                if '/*' in m_code:
                    comment_style['Multi-line (/* */)'] += 1

            # Check for blank lines (indicates grouping)
            if re.search(r'\n\s*\n', m_code):
                has_blank_lines += 1

        total = len(self.partitions)
        self.patterns['organization']['comments'] = {
            'frequency': round(has_comments / total * 100, 1) if total > 0 else 0,
            'styles': dict(comment_style)
        }
        self.patterns['organization']['blank_lines'] = {
            'frequency': round(has_blank_lines / total * 100, 1) if total > 0 else 0
        }

    def _analyze_error_handling(self):
        """Analyze error handling patterns."""
        has_try_otherwise = 0
        fallback_values = Counter()

        for partition in self.partitions:
            m_code = partition['m_code']

            if 'try' in m_code.lower() and 'otherwise' in m_code.lower():
                has_try_otherwise += 1

                # Extract fallback values
                fallback_matches = re.findall(r'otherwise\s+(\w+|null|0|"")', m_code, re.IGNORECASE)
                for fallback in fallback_matches:
                    fallback_values[fallback] += 1

        total = len(self.partitions)
        self.patterns['error_handling']['try_otherwise_usage'] = {
            'frequency': round(has_try_otherwise / total * 100, 1) if total > 0 else 0,
            'fallback_values': dict(fallback_values.most_common(5))
        }

    def _analyze_parameters(self):
        """Analyze parameter usage patterns."""
        # Look for common parameter names in M code
        parameters_found = set()
        param_pattern = re.compile(r'\b([A-Z][a-zA-Z]+(?:Date|Name|Path|Server|Database))\b')

        for partition in self.partitions:
            matches = param_pattern.findall(partition['m_code'])
            parameters_found.update(matches)

        self.patterns['parameters'] = {
            'likely_parameters': sorted(list(parameters_found)[:10]),
            'count': len(parameters_found)
        }

    def generate_report(self):
        """Generate human-readable report."""
        report = []
        report.append("=" * 80)
        report.append("M CODE PATTERN ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Project: {self.project_path}")
        report.append(f"TMDL Files Analyzed: {len(self.tmdl_files)}")
        report.append(f"M Code Partitions Found: {len(self.partitions)}")
        report.append("=" * 80)
        report.append("")

        # Naming Conventions
        report.append("=== NAMING CONVENTIONS ===")
        report.append("")
        report.append("Step Naming Styles:")
        for style, data in sorted(self.patterns['naming']['step_styles'].items(),
                                   key=lambda x: x[1]['count'], reverse=True):
            report.append(f"  - {style}: {data['percentage']}% ({data['count']} occurrences)")
        report.append("")
        report.append("Sample Step Names:")
        for name in self.patterns['naming']['step_names'][:5]:
            report.append(f"  - {name}")
        report.append("")

        # Transformations
        report.append("=== TRANSFORMATION PATTERNS ===")
        report.append("")
        for transform, data in sorted(self.patterns['transformations'].items(),
                                       key=lambda x: x[1]['count'], reverse=True):
            report.append(f"  - {transform}: {data['percentage']}% ({data['count']} partitions)")
        report.append("")

        # Organization
        report.append("=== CODE ORGANIZATION ===")
        report.append("")
        report.append(f"Comments: {self.patterns['organization']['comments']['frequency']}% of partitions")
        if self.patterns['organization']['comments']['styles']:
            report.append("Comment Styles:")
            for style, count in self.patterns['organization']['comments']['styles'].items():
                report.append(f"  - {style}: {count} occurrences")
        report.append(f"Blank Lines (Grouping): {self.patterns['organization']['blank_lines']['frequency']}% of partitions")
        report.append("")

        # Error Handling
        report.append("=== ERROR HANDLING ===")
        report.append("")
        report.append(f"Try-Otherwise Usage: {self.patterns['error_handling']['try_otherwise_usage']['frequency']}% of partitions")
        if self.patterns['error_handling']['try_otherwise_usage']['fallback_values']:
            report.append("Common Fallback Values:")
            for value, count in self.patterns['error_handling']['try_otherwise_usage']['fallback_values'].items():
                report.append(f"  - {value}: {count} occurrences")
        report.append("")

        # Parameters
        report.append("=== PARAMETER USAGE ===")
        report.append("")
        if self.patterns['parameters']['likely_parameters']:
            report.append(f"Likely Parameters Found: {self.patterns['parameters']['count']}")
            report.append("Sample Parameter Names:")
            for param in self.patterns['parameters']['likely_parameters'][:10]:
                report.append(f"  - {param}")
        else:
            report.append("No clear parameter usage detected")
        report.append("")

        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("")

        # Generate recommendations based on patterns
        dominant_style = max(self.patterns['naming']['step_styles'].items(),
                             key=lambda x: x[1]['count'], default=None)
        if dominant_style and dominant_style[1]['percentage'] > 50:
            report.append(f"✓ Use {dominant_style[0]} for new step names (dominant pattern)")
        else:
            report.append("⚠ Mixed naming styles detected - consider standardizing")

        if self.patterns['organization']['comments']['frequency'] > 30:
            report.append("✓ Comments are commonly used - add comments for complex logic")
        else:
            report.append("⚠ Low comment usage - consider adding comments for maintainability")

        if self.patterns['error_handling']['try_otherwise_usage']['frequency'] > 20:
            report.append("✓ Error handling is used - apply try-otherwise for risky operations")
        else:
            report.append("⚠ Limited error handling - consider adding try-otherwise where needed")

        report.append("")
        report.append("=" * 80)

        return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze M code patterns in Power BI TMDL files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('project_path', help='Path to Power BI project folder (contains .SemanticModel)')
    parser.add_argument('--output', help='Output file for report (default: stdout)')
    parser.add_argument('--json', help='Output JSON file for structured data')

    args = parser.parse_args()

    try:
        # Initialize analyzer
        analyzer = MCodePatternAnalyzer(args.project_path)

        # Run analysis
        patterns = analyzer.analyze()

        # Generate report
        report = analyzer.generate_report()

        # Output report
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"Report saved to: {args.output}")
        else:
            print(report)

        # Output JSON if requested
        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2)
            print(f"JSON data saved to: {args.json}")

        return 0

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
