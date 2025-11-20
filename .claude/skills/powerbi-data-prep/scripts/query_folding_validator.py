#!/usr/bin/env python3
"""
Query Folding Validator for M Code

Analyzes M code to detect operations that break query folding and estimates
performance impact. Helps users make informed decisions about transformations.

Usage:
    python query_folding_validator.py --m-code "<m-code-file>"
    python query_folding_validator.py --m-code "<m-code-file>" --verbose
"""

import sys
import os
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class QueryFoldingIssue:
    """Represents a query folding break."""
    line_number: int
    line_content: str
    operation: str
    severity: str  # 'breaks_folding', 'may_break_folding', 'preserves_folding'
    reason: str
    recommendation: str

class QueryFoldingValidator:
    """Validator for query folding in M code."""

    # Operations that ALWAYS break query folding
    FOLDING_BREAKERS = {
        'Table.AddColumn': 'Adding custom columns breaks query folding',
        'Text.Start': 'Text operations break query folding',
        'Text.End': 'Text operations break query folding',
        'Text.Middle': 'Text operations break query folding',
        'Text.Replace': 'Text operations break query folding',
        'Text.Combine': 'Text operations break query folding',
        'Text.Upper': 'Text operations break query folding',
        'Text.Lower': 'Text operations break query folding',
        'Text.Trim': 'Text operations break query folding',
        'Date.Year': 'Date extraction functions break query folding',
        'Date.Month': 'Date extraction functions break query folding',
        'Date.Day': 'Date extraction functions break query folding',
        'DateTime.Date': 'DateTime extraction functions break query folding',
        'DateTime.Time': 'DateTime extraction functions break query folding',
        'List.Sum': 'List operations break query folding',
        'List.Count': 'List operations break query folding',
        'List.Max': 'List operations break query folding',
        'List.Min': 'List operations break query folding',
        'Record.Field': 'Record operations break query folding',
        'Table.Pivot': 'Pivot operations break query folding',
        'Table.Unpivot': 'Unpivot operations break query folding',
        'Table.Buffer': 'Buffering explicitly breaks query folding',
        'Table.Transpose': 'Transpose breaks query folding',
        '&': 'Text concatenation (&) breaks query folding'
    }

    # Operations that PRESERVE query folding
    FOLDING_PRESERVERS = {
        'Table.SelectRows': 'Row filtering preserves query folding',
        'Table.SelectColumns': 'Column selection preserves query folding',
        'Table.RemoveColumns': 'Column removal preserves query folding',
        'Table.RenameColumns': 'Column renaming preserves query folding',
        'Table.Sort': 'Sorting preserves query folding',
        'Table.Distinct': 'Distinct rows preserves query folding',
        'Table.NestedJoin': 'Table joins preserve query folding (if both sources fold)',
        'Table.Join': 'Table joins preserve query folding (if both sources fold)',
        'Table.Combine': 'Appending tables preserves query folding (if all sources fold)',
        'Table.Group': 'Standard aggregations preserve query folding',
        'Table.TransformColumnTypes': 'Type conversions preserve query folding',
        'Sql.Database': 'SQL database connection supports query folding'
    }

    # Operations that MAY break query folding (depends on context)
    FOLDING_MAYBE = {
        'Table.ReplaceValue': 'May preserve query folding depending on source capability',
        'Table.FillDown': 'May not be supported by all sources',
        'Table.FillUp': 'May not be supported by all sources'
    }

    def __init__(self, m_code):
        self.m_code = m_code
        self.lines = m_code.splitlines()
        self.issues = []
        self.folding_broken_at = None  # Line number where folding first breaks

    def validate(self):
        """Run validation and identify query folding issues."""
        for i, line in enumerate(self.lines, start=1):
            line_content = line.strip()

            if not line_content or line_content.startswith('//'):
                continue  # Skip blank lines and comments

            # Check for folding breakers
            for operation, reason in self.FOLDING_BREAKERS.items():
                if operation in line:
                    # Special handling for concatenation operator
                    if operation == '&':
                        # Only flag if used in context (not in strings or comments)
                        if self._is_concatenation(line):
                            self.issues.append(QueryFoldingIssue(
                                line_number=i,
                                line_content=line_content,
                                operation='Text Concatenation (&)',
                                severity='breaks_folding',
                                reason=reason,
                                recommendation='Move text operations to end of pipeline or use source-level calculation'
                            ))
                            if self.folding_broken_at is None:
                                self.folding_broken_at = i
                    else:
                        self.issues.append(QueryFoldingIssue(
                            line_number=i,
                            line_content=line_content,
                            operation=operation,
                            severity='breaks_folding',
                            reason=reason,
                            recommendation=self._get_recommendation(operation)
                        ))
                        if self.folding_broken_at is None:
                            self.folding_broken_at = i

            # Check for maybe-breakers
            for operation, reason in self.FOLDING_MAYBE.items():
                if operation in line:
                    self.issues.append(QueryFoldingIssue(
                        line_number=i,
                        line_content=line_content,
                        operation=operation,
                        severity='may_break_folding',
                        reason=reason,
                        recommendation='Verify query folding in Power Query Editor using "View Native Query"'
                    ))

        return self.issues

    def _is_concatenation(self, line):
        """Check if & is used for concatenation (not in string)."""
        # Simple heuristic: if & appears outside quotes
        in_string = False
        for char in line:
            if char == '"':
                in_string = not in_string
            elif char == '&' and not in_string:
                return True
        return False

    def _get_recommendation(self, operation):
        """Get specific recommendation for operation."""
        recommendations = {
            'Table.AddColumn': 'Move custom column creation to end of pipeline, or use calculated column in source',
            'Text.Start': 'Consider creating view at source with substring logic',
            'Text.Combine': 'Move text concatenation to end, or combine at source level',
            'Date.Year': 'Create view at source with YEAR() function, or move to end of pipeline',
            'Table.Pivot': 'Consider pre-pivoting data at source, or accept performance impact for small datasets',
            'Table.Buffer': 'Remove buffer unless table is referenced multiple times',
        }
        return recommendations.get(operation, 'Move this operation to end of pipeline to minimize data loaded')

    def estimate_impact(self):
        """Estimate performance impact of query folding breaks."""
        if not self.issues:
            return 'No query folding issues detected - all operations should fold to source'

        breaking_issues = [i for i in self.issues if i.severity == 'breaks_folding']

        if not breaking_issues:
            return 'Minor impact - some operations may not fold depending on source capabilities'

        if self.folding_broken_at and self.folding_broken_at <= 5:
            return 'HIGH IMPACT - Query folding breaks early in pipeline, loading most/all source data'
        elif self.folding_broken_at and self.folding_broken_at <= 10:
            return 'MEDIUM IMPACT - Query folding breaks mid-pipeline, some filtering occurs before break'
        else:
            return 'LOW IMPACT - Query folding breaks late in pipeline, most filtering completed at source'

    def generate_report(self, verbose=False):
        """Generate validation report."""
        report = []
        report.append("=" * 80)
        report.append("QUERY FOLDING VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")

        if not self.issues:
            report.append("✅ EXCELLENT - No query folding issues detected!")
            report.append("")
            report.append("All operations in this M code should fold to the data source,")
            report.append("resulting in optimal performance and minimal data transfer.")
            report.append("")
            return '\n'.join(report)

        # Summary
        breaking = [i for i in self.issues if i.severity == 'breaks_folding']
        maybe_breaking = [i for i in self.issues if i.severity == 'may_break_folding']

        report.append(f"⚠️  QUERY FOLDING ISSUES DETECTED")
        report.append("")
        report.append(f"Breaking Operations: {len(breaking)}")
        report.append(f"Potentially Breaking: {len(maybe_breaking)}")
        report.append("")

        # Performance impact
        impact = self.estimate_impact()
        report.append(f"PERFORMANCE IMPACT: {impact}")
        report.append("")

        if self.folding_broken_at:
            report.append(f"Query folding first breaks at line {self.folding_broken_at}")
            report.append("All subsequent operations will also not fold.")
            report.append("")

        # Details
        report.append("=" * 80)
        report.append("ISSUES DETECTED")
        report.append("=" * 80)
        report.append("")

        for issue in self.issues:
            if issue.severity == 'breaks_folding':
                report.append(f"❌ Line {issue.line_number}: {issue.operation}")
            else:
                report.append(f"⚠️  Line {issue.line_number}: {issue.operation}")

            if verbose:
                report.append(f"   Code: {issue.line_content[:70]}{'...' if len(issue.line_content) > 70 else ''}")

            report.append(f"   Reason: {issue.reason}")
            report.append(f"   Recommendation: {issue.recommendation}")
            report.append("")

        # Recommendations
        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("")

        if breaking:
            report.append("1. Move non-foldable operations to end of pipeline")
            report.append("   - Apply filters, column selection, and sorting BEFORE custom columns/text ops")
            report.append("   - This minimizes data loaded into Power BI before transformation")
            report.append("")

        if any('Text' in i.operation or 'Date.' in i.operation for i in breaking):
            report.append("2. Consider creating view at data source")
            report.append("   - SQL views can perform text/date operations server-side")
            report.append("   - Then query the view in Power BI for full query folding")
            report.append("")

        if len(breaking) > 3:
            report.append("3. Evaluate if all transformations are necessary")
            report.append("   - Complex transformations may be better suited for data warehouse/ETL")
            report.append("   - Consider data modeling implications vs. performance trade-offs")
            report.append("")

        report.append("=" * 80)

        return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Validate query folding in M code',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--m-code', required=True, help='Path to file containing M code')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output with code snippets')
    parser.add_argument('--output', help='Output file for report (default: stdout)')

    args = parser.parse_args()

    try:
        # Read M code
        m_code_path = Path(args.m_code)
        if not m_code_path.exists():
            print(f"[ERROR] M code file not found: {args.m_code}")
            return 1

        m_code = m_code_path.read_text(encoding='utf-8')

        # Initialize validator
        validator = QueryFoldingValidator(m_code)

        # Run validation
        issues = validator.validate()

        # Generate report
        report = validator.generate_report(verbose=args.verbose)

        # Output report
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"Report saved to: {args.output}")
        else:
            print(report)

        # Exit code: 0 if no breaking issues, 1 if has breaking issues
        breaking_issues = [i for i in issues if i.severity == 'breaks_folding']
        return 1 if breaking_issues else 0

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
