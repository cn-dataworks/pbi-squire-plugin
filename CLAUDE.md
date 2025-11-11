# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Power BI analyst project repository containing agentic workflows for Power BI project analysis, modification, deployment, and merging.

## Available Workflows

Detailed documentation for all workflows is available in [.claude/README.md](.claude/README.md).

### Commands

- `/evaluate-pbi-project-file` - Analyze and diagnose Power BI project issues
- `/create-pbi-artifact` - Create new measures, columns, tables, or visuals
- `/implement-deploy-test-pbi-project-file` - Implement, deploy, and test changes
- `/merge-powerbi-projects` - Compare and merge two Power BI projects

## Development Notes

- All workflows follow non-destructive patterns (versioned copies)
- Supports both TMDL and model.bim formats
- Comprehensive error handling and logging
- Python utilities in `.claude/tools/` provide reusable components

## Tool Organization Guidelines

### Tool Consolidation
Before creating new tools in `.claude/tools/`, evaluate whether the functionality should be integrated into an existing tool. Prefer consolidating related functionality into comprehensive tools rather than creating many specialized standalone files.

**Example**: TMDL validation checks are consolidated into `tmdl_format_validator.py` (TMDL001-TMDL013) rather than separate validators for each check type.

### Problem-Specific Scripts
Scripts or tools created for specific dashboard problems should remain in the problem's scratchpad folder (`agent_scratchpads/<timestamp>-<problem-name>/`) rather than being promoted to `.claude/tools/`. Only promote tools that have broad reusability across multiple projects.

**Example**: `fix_misc_gp.py` for a specific measure issue stays in its scratchpad folder, while `tmdl_format_validator.py` that validates any TMDL file belongs in `.claude/tools/`.

### Documentation Location
Workflow documentation and agent instructions should be maintained in [.claude/README.md](.claude/README.md). Avoid creating standalone markdown documentation files. Use the scratchpad folder's `findings.md` for problem-specific documentation.

**Example**: TMDL validation capabilities are documented in `.claude/README.md` under the validator section, not in separate files like `tmdl_validation_guide.md`.
