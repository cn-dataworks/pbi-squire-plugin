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
