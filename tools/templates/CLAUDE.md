# CLAUDE.md

This project uses the **Power BI Analyst Plugin**.

## When to Use

Invoke the `powerbi-analyst` skill when working with:
- Power BI files (*.pbip, *.pbix)
- TMDL files (semantic model definitions)
- PBIR files (report visuals)
- DAX measures and M code

## Available Commands

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose issues |
| `/create-pbi-artifact` | Create measures, columns, tables |
| `/implement-deploy-test-pbi-project-file` | Deploy and test changes |
| `/setup-data-anonymization` | Set up data masking for sensitive data |

## Power BI Project Path

{{PBI_PROJECT_PATH}}

## File Permissions

Allowed paths for Read/Edit/Write:
{{ALLOWED_PATHS}}
