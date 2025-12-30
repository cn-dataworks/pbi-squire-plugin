---
name: powerbi-analyst
description: Analyze, create, and modify Power BI projects with intelligent assistance. Diagnose calculation issues, create new measures and visuals, and deploy changes with validation. Uses Microsoft's Power BI Modeling MCP for live semantic model editing when available, with automatic fallback to file-based TMDL manipulation. Supports PBIP projects and Power BI Desktop.
---

# Power BI Analyst

## Overview

Expert Power BI development assistant that orchestrates specialized DAX and M-Code agents for complex calculations. Handles both semantic model changes (measures, tables, columns) and report-side changes (PBIR visuals, layouts).

**Key Capabilities:**
- Diagnose and fix calculation issues in existing dashboards
- Create new measures, calculated columns, tables, and visuals
- Deploy changes with validation gates
- Merge and compare Power BI projects
- Document existing dashboards in business-friendly language

**Architecture:**
- Uses Power BI Modeling MCP for live model editing when available
- Falls back to file-based TMDL manipulation automatically
- Orchestrates specialist agents via Task Blackboard pattern

---

## When to Use This Skill

**Trigger Keywords:**
- Power BI, PBIX, PBIP, DAX, M code, Power Query
- Semantic model, measure, calculated column, TMDL
- Create dashboard, fix measure, add visual, deploy report

**Trigger Actions:**
- "Fix this measure" → EVALUATE workflow
- "Create a YoY growth measure" → CREATE_ARTIFACT workflow
- "Add a new dashboard page" → CREATE_PAGE workflow
- "Apply the changes" → IMPLEMENT workflow
- "What does this dashboard do?" → ANALYZE workflow
- "Merge these two projects" → MERGE workflow
- "Extract templates from this report" → HARVEST_TEMPLATES workflow

**File Patterns:**
- `*.pbip`, `*.pbix`, `*.tmdl`, `*.bim`
- `*/.SemanticModel/**`, `*/.Report/**`

---

## Workflows

### EVALUATE (Diagnose/Fix)

**Use when:** User reports something is broken, incorrect, or not working as expected.

**Process:**
1. Connect to project (MCP or file-based)
2. Clarify the problem through interactive Q&A
3. Investigate existing code and data
4. Plan changes with proposed fixes
5. Verify approach before implementation

**Output:** `findings.md` with diagnosed issues and proposed fixes

**Next step:** "implement the changes" to apply fixes

---

### CREATE_ARTIFACT (New Measure/Column/Table/Visual)

**Use when:** User wants to add something new that doesn't exist yet.

**Process:**
1. Connect to project and analyze schema
2. Decompose request into discrete artifacts
3. Specify each artifact through interactive Q&A
4. Discover existing patterns for consistency
5. Generate code with validation

**Output:** `findings.md` with new artifact specifications

**Next step:** "implement the changes" to create artifacts

---

### CREATE_PAGE (New Dashboard Page)

**Use when:** User wants a complete new report page with multiple visuals.

**Process:**
1. Validate project has .Report folder (PBIR required)
2. Analyze the business question being answered
3. Decompose into required measures and visuals
4. Specify measures (delegates to DAX Specialist)
5. Design layout using 8px grid system
6. Design interactions (cross-filtering, drill-through)
7. Generate PBIR files

**Output:** `findings.md` with measures + visual specifications + PBIR files

**Next step:** "implement the changes" to create the page

---

### IMPLEMENT (Apply Changes)

**Use when:** User has reviewed findings and wants to apply proposed changes.

**Prerequisites:** Must have `findings.md` from previous workflow

**Process:**
1. Validate findings file exists with proposed changes
2. Apply code changes (MCP transactions or file writes)
3. Validate DAX syntax
4. Apply visual changes (PBIR)
5. Validate PBIR structure
6. Deploy (optional, if requested)
7. Test (optional, if URL available)

**Output:** Updated project files + validation results

---

### ANALYZE (Document Existing)

**Use when:** User wants to understand what an existing dashboard does.

**Process:**
1. Connect to project
2. Discover all pages and visuals
3. Extract measure definitions
4. Analyze technical implementation
5. Synthesize business-friendly documentation

**Output:** `dashboard_analysis.md` with:
- Executive Summary
- Page descriptions (business-friendly)
- Metrics explained
- Technical appendix

---

### MERGE (Compare/Merge Projects)

**Use when:** User wants to compare or combine two Power BI projects.

**Process:**
1. Connect to both projects
2. Extract schemas from both
3. Compare and identify differences
4. Explain semantic meaning of differences
5. Present decisions for each conflict
6. Apply merge with user approval

**Output:** Merged project + merge report

---

### HARVEST_TEMPLATES (Extract Visual Templates)

**Use when:** User wants to extract reusable visual templates from existing dashboards.

**Commands:** `/harvest-templates`, `/review-templates`, `/promote-templates`

**Public Template Repository:** https://github.com/cn-dataworks/pbir-visuals

**Capability Tiers (Runtime Detection):**

| Command | Requirements | If Missing |
|---------|--------------|------------|
| `/harvest-templates` | PBIR .Report folder | Guide to convert PBIX → PBIP |
| `/review-templates` | Harvested templates | Prompt to harvest first |
| `/promote-templates` | GitHub CLI (`gh`) + authenticated | Manual PR instructions |

Each command checks requirements at runtime and provides helpful error messages with next steps.

**Process:**
1. **Harvest** (`/harvest-templates`) - *Always available with PBIR project*
   - Preflight: Verify .Report folder exists
   - Scan .Report folder for all visuals
   - Classify visuals by type and binding pattern
   - Deduplicate (keep unique structures only)
   - Sanitize (replace specifics with `{{PLACEHOLDER}}` syntax)
   - Save to local staging: `.templates/harvested/`

2. **Review** (`/review-templates`) - *Requires harvested templates*
   - Preflight: Verify harvested templates exist
   - Fetch existing templates from public repository
   - Compare harvested against public library
   - Flag as: NEW, DUPLICATE, VARIANT, IMPROVED
   - Mark templates for promotion

3. **Promote** (`/promote-templates`) - *Requires GitHub CLI*
   - Preflight: Check `gh --version` and `gh auth status`
   - If gh not installed → show install instructions + manual PR alternative
   - If not authenticated → prompt `gh auth login`
   - Fork public repo (if not already forked)
   - Create feature branch, copy templates, create PR

**Naming Convention:**
```
[visual-type]-[binding-pattern].json

Examples:
- bar-chart-category-y.json
- line-chart-multi-measure.json
- card-single-measure.json
- slicer-dropdown.json
```

**Storage:**
- Local staging: `[project]/.templates/harvested/`
- Public library: `github.com/cn-dataworks/pbir-visuals/visual-templates/` (via PR)

**Output:** Template files + harvest manifest + PR URL (on promotion)

---

## Specialist Agents

The orchestrator delegates to specialized agents based on artifact type:

### DAX Specialist (`powerbi-dax-specialist`)
**Handles:** Measures, calculated columns, calculation groups, KPIs

**Expertise:**
- Time Intelligence (SAMEPERIODLASTYEAR, DATEADD, etc.)
- Filter Context (CALCULATE, FILTER, ALL, KEEPFILTERS)
- Performance patterns (DIVIDE, iterator vs aggregator)
- Relationship-aware calculations (RELATED, USERELATIONSHIP)

### M-Code Specialist (`powerbi-mcode-specialist`)
**Handles:** Partitions (table M queries), named expressions, ETL

**Expertise:**
- ETL patterns (Table.TransformColumns, Table.AddColumn)
- Query folding optimization
- Privacy levels
- Data type enforcement
- Error handling (try/otherwise)

---

## Connection Modes

### Power BI Desktop Mode (Default)
- Connects to running Power BI Desktop instance
- Uses Windows Integrated Authentication
- Full MCP capabilities

### File-Only Mode (Fallback)
- Works directly with TMDL/PBIR files
- No live validation
- Reduced capabilities (warned per operation)

---

## Session State

The skill maintains session state in `.claude/state.json`:
- Active tasks and their status
- Model schema cache
- Resource locks (for file-based mode)
- Connection status

Tasks use the **Task Blackboard pattern** where specialists read/write to designated sections of `findings.md`.

---

## Project Setup (Bootstrap)

The skill requires Python tools and helper files to be present in the user's project directory. These are automatically copied from the plugin on first workflow run.

### Bootstrap Process

**Automatic (recommended):** On first workflow execution, run bootstrap:

```powershell
# Windows
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"

# macOS/Linux
bash "$HOME/.claude/plugins/custom/powerbi-analyst/tools/bootstrap.sh"
```

**What gets created:**
```
YourProject/
├── .claude/
│   ├── state.json           ← Session state
│   ├── tasks/               ← Task findings files
│   ├── tools/               ← Python utilities (copied from plugin)
│   │   ├── token_analyzer.py
│   │   ├── tmdl_format_validator.py
│   │   ├── analytics_merger.py
│   │   ├── version.txt      ← Tracks tool version
│   │   └── ...
│   └── helpers/             ← Helper files (copied from plugin)
│       └── pbi-url-filter-encoder.md
└── YourProject.pbip
```

### Version Tracking

The bootstrap script tracks versions to manage updates:

| Command | Purpose |
|---------|---------|
| `bootstrap.ps1` | Install/update tools if needed |
| `bootstrap.ps1 -CheckOnly` | Check if update available (exit code 1 = update needed) |
| `bootstrap.ps1 -Force` | Force reinstall even if current |

### Updating Tools

When the plugin is updated, re-run bootstrap to get new tool versions:

```powershell
# Check if update needed
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1" -CheckOnly

# Update tools
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

### Manual Tool Edits

If you edit local tools (`.claude/tools/*`), the version comparison will show "newer". Use `-Force` to overwrite with plugin versions if needed.

---

## Validation Gates

All changes pass through validation before completion:

| Validator | What it Checks | Blocking |
|-----------|----------------|----------|
| DAX Review | Syntax, semantics, best practices | Yes (errors) |
| PBIR Validator | JSON structure, config integrity | Yes (errors) |
| MCP Validation | Live syntax check (MCP mode only) | Yes (errors) |

Warnings are reported but don't block implementation.

---

## References

This skill includes reference documentation:

### `assets/findings_template.md`
Template for Task Blackboard used by all workflows.

### Visual Templates (Public Repository)
PBIR visual templates with `{{PLACEHOLDER}}` syntax are maintained in a public repository:

**GitHub:** https://github.com/cn-dataworks/pbir-visuals/visual-templates/

Template types include:
- Cards, line charts, bar charts, column charts
- Tables, matrices, pie charts, scatter charts
- Azure maps (gradient, bubble)
- Slicers (date range, dropdown, multi-select)
- Static images

Templates are fetched via `WebFetch` from raw.githubusercontent.com.
See `assets/visual-templates/README.md` for usage and contribution instructions.

### `references/`
- `getting-started.md` - Onboarding guide with data masking workflow
- `glossary.md` - Technical terms explained
- `troubleshooting-faq.md` - Common issues and solutions

---

## Quick Start

1. **Have a problem?** → "Help me fix the YoY calculation in my Sales dashboard"
2. **Want something new?** → "Create a margin percentage measure"
3. **Need a whole page?** → "Build a regional performance dashboard page"
4. **Ready to apply?** → "Implement the changes from findings.md"
5. **Want to understand?** → "Analyze this dashboard and explain what it does"
6. **Build template library?** → "Harvest visual templates from this report"
