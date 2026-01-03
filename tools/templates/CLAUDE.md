# CLAUDE.md

This project uses the **Power BI Analyst Plugin** for Claude Code.

## Available Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `powerbi-analyst` | `/evaluate-pbi-project-file` | Analyze and diagnose issues |
| `powerbi-analyst` | `/create-pbi-artifact` | Create measures, columns, tables |
| `powerbi-analyst` | `/implement-deploy-test-pbi-project-file` | Deploy and test changes |
| `powerbi-data-prep` | `/setup-data-anonymization` | Set up data masking |

## Power BI Project Path

{{PBI_PROJECT_PATH}}

## CRITICAL: Data Anonymization Check

**Before using MCP tools that query or sample data**, you MUST check if this project has anonymization configured:

1. **Check for `.anonymization/config.json`** in the Power BI project folder
2. **If it exists**: Check that `DataMode` parameter is set to "Anonymized" before sampling data
3. **If it does NOT exist**:
   - WARN the user that MCP queries may expose sensitive data
   - Ask: "This project doesn't have anonymization configured. Would you like to:"
     - Set up anonymization first (`/setup-data-anonymization`)
     - Proceed anyway (data is not sensitive)
     - Work in file-only mode (no MCP data queries)

### When to Check

Check for anonymization BEFORE:
- Using `dax_query_operations.execute()` (runs DAX queries that return data)
- Using any MCP operation that samples or previews data
- Using Playwright to view dashboards with real data

### Safe Operations (No Check Needed)

These operations don't expose data:
- `dax_query_operations.validate()` (syntax check only)
- `measure_operations.list()` (metadata only)
- `table_operations.list()` (metadata only)
- File-based TMDL edits

## Workflow Usage

When working with Power BI projects in this folder:

1. **First time setup**: Run `/setup-data-anonymization` if the project contains sensitive data
2. **Evaluating issues**: Use `/evaluate-pbi-project-file --project "<path>"`
3. **Creating artifacts**: Use `/create-pbi-artifact --project "<path>"`
4. **Testing changes**: Use `/implement-deploy-test-pbi-project-file --project "<path>"`

## File Permissions

This project is configured to allow Read/Edit/Write operations on:
{{ALLOWED_PATHS}}
