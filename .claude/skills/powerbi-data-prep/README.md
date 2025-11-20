# Power BI Data Prep Skill

Write and edit M code (Power Query) transformations in Power BI TMDL projects with intelligent pattern analysis, query folding validation, and safe TMDL editing.

## Installation

This skill is already available in the project. To use it, simply invoke it by discussing data transformations or Power Query modifications in Power BI projects.

## What This Skill Does

- **Analyzes existing M code patterns** to ensure consistency with project conventions
- **Validates query folding** to warn about performance impacts before applying changes
- **Safely edits TMDL partition files** with proper tab handling and indentation
- **Supports all levels of M code complexity** (simple to advanced)
- **Integrates with TMDL syntax validator** for automatic validation after changes

## When to Use

Trigger this skill when you need to:
- Filter tables or add/remove columns in Power Query
- Create new calculated tables with M code
- Merge or join tables
- Add custom columns or transformations
- Modify existing partition M code
- Perform any ETL or data prep operations in Power BI

## Core Workflow

1. **Analyze patterns** - Discovers naming conventions and transformation styles from existing code
2. **Design transformation** - Presents simplest approach with pros/cons for complex alternatives
3. **Validate query folding** - Warns about performance impacts
4. **Apply M code changes** - Safely edits TMDL files with backups
5. **Validate TMDL syntax** - Runs syntax checker automatically

## Files Included

### Scripts (`scripts/`)
- `m_partition_editor.py` - Safely edit M code in TMDL partition files
- `m_pattern_analyzer.py` - Analyze project patterns for consistency
- `query_folding_validator.py` - Detect query folding breaks

### References (`references/`)
- `query_folding_guide.md` - Complete rules for query folding
- `common_transformations.md` - Library of M code patterns with examples
- `tmdl_partition_structure.md` - TMDL partition formatting specification
- `m_best_practices.md` - M code style guide and optimization techniques
- `m_pattern_discovery.md` - How to interpret pattern analysis output

## Example Usage

**User:** "Remove inactive customers from the Customer table"

**Skill Response:**
1. Analyzes existing project patterns
2. Presents filtering transformation with query folding validation
3. Shows simple option (filter in M) vs advanced (filter at SQL source)
4. Gets user confirmation
5. Applies M code changes with proper formatting
6. Runs TMDL syntax validation
7. Reports success with backup file location

## Integration with Power BI Workflows

This skill works alongside existing Power BI workflows:
- Use this skill for **M code / Power Query transformations**
- Use `/create-pbi-artifact` for **DAX measures and calculated columns**
- Use `/evaluate-pbi-project-file` for **debugging existing issues**
- Use `/implement-deploy-test-pbi-project-file` for **deployment and testing**

## Key Features

- ✅ **Pattern-aware**: Follows project naming conventions and coding styles
- ✅ **Query folding validation**: Always warns about performance impacts
- ✅ **Safe editing**: Creates automatic backups before modifying files
- ✅ **Simplicity-first**: Recommends simplest approach, presents complex alternatives
- ✅ **TMDL validation**: Automatic syntax checking after changes
- ✅ **Comprehensive guidance**: Extensive reference documentation for M code best practices

## Version

Created: 2025-11-19
Last Updated: 2025-11-19
