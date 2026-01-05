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
│   ├── core/               # PUBLIC - Core Python utilities (always installed)
│   ├── advanced/           # PRIVATE - Pro features (only in pro branch)
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

## Branch Strategy (Public/Private Split)

This project uses a **branch-based** approach to manage public and private versions:

| Branch | Contents | Repository |
|--------|----------|------------|
| `main` | Core + Anonymization + Merge | Public (github.com/cn-dataworks/powerbi-analyst-plugin) |
| `pro` | Everything + Playwright + Template Harvesting | Private |

### Development Workflow

```bash
# Work on public features
git checkout main
# ... make changes ...
git commit -m "Add feature"
git push origin main

# Work on Pro features
git checkout pro
# ... make changes ...
git commit -m "Add Pro feature"
git push origin pro

# Sync public fixes into Pro
git checkout pro
git merge main
git push origin pro
```

### File Organization

| Location | Public (main) | Private (pro) |
|----------|---------------|---------------|
| `tools/core/` | All files | All files |
| `tools/advanced/` | Empty | Pro scripts |
| `skills/powerbi-analyst/workflows/harvest_templates.md` | Excluded | Included |
| `skills/powerbi-analyst/agents/powerbi-playwright-tester.md` | Excluded | Included |

### Bootstrap Behavior

The `bootstrap.ps1` script automatically detects which version is installed:
- Always copies from `tools/core/`
- Copies from `tools/advanced/` only if files exist (Pro version)
