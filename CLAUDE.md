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

## Git Workflow (Cascading/Waterfall Pattern)

This project uses a **cascading branch strategy** to manage public (Core) and private (Pro) versions.

### The Golden Rule: "Flow Downstream"

```
main (Core) ──────► pro (Pro)
   ↑                    │
   │                    │
Changes flow         Changes NEVER
INTO main            flow back to main
```

- **Changes to Core** flow into **Pro**
- **Changes to Pro** NEVER flow back to **Core**
- **Pro is a superset** - contains everything in Core, plus extras

### Permanent Branches

| Branch | Purpose | Contents |
|--------|---------|----------|
| `main` | Stable Core (Public/Free) | Core + Anonymization + Merge |
| `pro` | Stable Pro (Private/Paid) | Everything + Playwright + Template Harvesting |

### File Organization

| Location | `main` branch | `pro` branch |
|----------|---------------|--------------|
| `tools/core/` | All files | All files |
| `tools/advanced/` | Empty (gitignored) | Pro scripts |
| `workflows/harvest-templates.md` | Excluded (gitignored) | Included |
| `agents/powerbi-playwright-tester.md` | Excluded (gitignored) | Included |

---

## Development Scenarios

### Scenario A: Feature for Everyone (Core + Pro)

Adding a feature that both versions need (e.g., new validator):

```bash
# 1. Branch off Core
git checkout main
git checkout -b feature/new-validator

# 2. Do the work, commit
git add .
git commit -m "Add new validator"

# 3. Merge into Core
git checkout main
git merge feature/new-validator
git push origin main

# 4. CASCADE to Pro (critical!)
git checkout pro
git merge main
git push origin pro

# 5. Cleanup
git branch -d feature/new-validator
```

### Scenario B: Pro-Only Feature

Adding a feature only for Pro (e.g., Playwright testing):

```bash
# 1. Branch off PRO (not main!)
git checkout pro
git checkout -b feature/playwright-tests

# 2. Do the work, commit
git add .
git commit -m "Add Playwright testing"

# 3. Merge into Pro ONLY
git checkout pro
git merge feature/playwright-tests
git push origin pro

# 4. STOP - Do NOT merge to main
git branch -d feature/playwright-tests
```

### Scenario C: Hotfix (Critical Bug in Core)

Fixing a bug that affects both versions:

```bash
# 1. Branch off main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix and commit
git add .
git commit -m "Fix critical bug"

# 3. Merge to main
git checkout main
git merge hotfix/critical-bug
git push origin main

# 4. IMMEDIATELY cascade to Pro
git checkout pro
git merge main
git push origin pro

# 5. Cleanup
git branch -d hotfix/critical-bug
```

---

## Visual History Flow

```
(Time flows right ->)

main (Core):  A --- B --- C (Bugfix) ---------------> E (New Core Feat)
                     \         \                       \
                      \         \ (merge to pro)        \ (merge to pro)
                       \         \                       \
pro (Pro):              X ------- M1 -------------------- M2 --- P (Pro Feat)
```

- **A, B:** Old core commits
- **X:** Initial pro branch creation
- **C:** Bug fixed in Core
- **M1:** Merged main into pro (got the bugfix)
- **E:** New Core feature
- **M2:** Merged main into pro (got new feature)
- **P:** Pro-only feature (stays in pro, never goes to main)

---

## Rules of the Road

1. **Always fix shared bugs in `main`** - If you fix a shared bug in `pro`, it becomes "trapped" and Core users never get it

2. **Merge `main` into `pro` frequently** - Don't let them drift apart or you'll get merge conflicts

3. **Pro is a superset** - Pro contains everything in Core, plus extras. Core never contains Pro stuff

4. **Never merge `pro` into `main`** - This would leak Pro features into the free version

5. **Use feature branches** - Never commit directly to `main` or `pro`

---

## Quick Reference

```bash
# Check current branch
git branch

# Switch to Core development
git checkout main

# Switch to Pro development
git checkout pro

# Sync Core changes into Pro (do this often!)
git checkout pro
git merge main
git push origin pro

# See what's different between branches
git log main..pro --oneline    # Commits in pro not in main
git log pro..main --oneline    # Commits in main not in pro (should be empty!)
```

---

## Bootstrap Behavior

The `bootstrap.ps1` script automatically detects which version is installed:
- Always copies from `tools/core/`
- Copies from `tools/advanced/` only if files exist (Pro version)
