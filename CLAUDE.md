# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for Power BI project analysis, modification, deployment, and merging.

## Plugin Structure

```
powerbi-analyst-plugin/
├── .claude-plugin/          # Plugin manifest
├── skills/                  # All skills
│   ├── powerbi-analyst/     # Main skill (agents, workflows, resources)
│   ├── power-bi-assistant/  # User guidance skill
│   ├── powerbi-dashboard-analyzer/  # Dashboard analysis
│   └── powerbi-data-prep/   # M code/Power Query
├── tools/
│   ├── core/               # Core Python utilities
│   ├── advanced/           # Pro features
│   ├── templates/          # Config templates for bootstrap
│   └── bootstrap.ps1       # Project setup script
├── .mcp.json               # MCP server config (Playwright)
├── README.md               # User installation guide
└── INSTALL.md              # Detailed installation
```

## Available Skills

| Skill | Purpose |
|-------|---------|
| `powerbi-analyst` | Main skill - orchestrates agents for DAX, M, TMDL, PBIR editing |
| `power-bi-assistant` | Guides users to correct workflow/command |
| `powerbi-dashboard-analyzer` | Analyzes dashboards, explains in business language |
| `powerbi-data-prep` | M code and Power Query transformations |

## Key Workflows

- `/evaluate-pbi-project-file` - Analyze and diagnose Power BI project issues
- `/create-pbi-artifact` - Create new measures, columns, tables, or visuals
- `/implement-deploy-test-pbi-project-file` - Implement, deploy, and test changes
- `/merge-powerbi-projects` - Compare and merge two Power BI projects

## Development Notes

- All workflows follow non-destructive patterns (versioned copies)
- Supports both TMDL and model.bim formats
- Python utilities in `tools/core/` provide reusable components
- Skills contain their own agents, workflows, and resources
- See `CONTRIBUTING.md` for Git workflow and branch strategy
