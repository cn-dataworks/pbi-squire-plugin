# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment.

## What It Does

| Skill | Purpose |
|-------|---------|
| `powerbi-analyst` | Diagnose issues, create measures/visuals, deploy changes |
| `power-bi-assistant` | Guides you to the right workflow |
| `powerbi-dashboard-analyzer` | Explains dashboards in business language |
| `powerbi-data-prep` | M code and Power Query transformations |

## Key Commands

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose issues |
| `/create-pbi-artifact` | Create measures, columns, tables, visuals |
| `/implement-deploy-test-pbi-project-file` | Deploy and test changes |
| `/merge-powerbi-projects` | Compare and merge projects |

## Development

When working on this plugin codebase, consult `CONTRIBUTING.md` for:

- **Git operations** - Which branch to use (`main` vs `pro`)
- **Committing changes** - Feature branches, commit workflow
- **Merging/pushing** - Cascading changes from `main` to `pro`
- **Adding features** - Core (both versions) vs Pro-only features
- **Hotfixes** - Critical bug fix workflow

**Key rule:** Changes flow `main` → `pro`, never the reverse.
