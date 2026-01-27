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
- Plugin version, update, check for updates, what version

**Trigger Actions:**
- "Fix this measure" → EVALUATE workflow
- "Create a YoY growth measure" → CREATE_ARTIFACT workflow
- "Add a new dashboard page" → CREATE_PAGE workflow
- "Apply the changes" → IMPLEMENT workflow
- "What does this dashboard do?" → ANALYZE workflow
- "Merge these two projects" → MERGE workflow
- "Check for updates" → VERSION_CHECK workflow
- "What version am I running?" → VERSION_CHECK workflow
- "Is Power BI Analyst up to date?" → VERSION_CHECK workflow

**File Patterns:**
- `*.pbip`, `*.pbix`, `*.tmdl`, `*.bim`
- `*/.SemanticModel/**`, `*/.Report/**`

---

## Pre-Workflow Checks

Before executing any workflow, perform these checks in order:

### Step -1: Bootstrap Status Check (CRITICAL)

**Purpose**: Ensure the project has been bootstrapped for this plugin.

**Check for bootstrap indicators in the current project directory:**

1. Look for `.claude/powerbi-analyst.json`
2. Look for `.claude/tools/powerbi-analyst/` folder
3. Look for `CLAUDE.md` with plugin reference

**If ANY of these are missing:**

```
+-------------------------------------------------------------------------+
|  BOOTSTRAP REQUIRED                                                      |
+-------------------------------------------------------------------------+

This project has not been set up for the Power BI Analyst plugin.

The plugin is installed GLOBALLY but needs to be bootstrapped for EACH
project to work properly. This copies necessary tools and configuration.

To set up this project, run:

  Windows:
  & "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"

  macOS/Linux:
  bash "$HOME/.claude/plugins/custom/powerbi-analyst/tools/bootstrap.sh"

This creates:
  - .claude/powerbi-analyst.json  (skill configuration)
  - .claude/tools/powerbi-analyst/ (plugin tools)
  - CLAUDE.md (project instructions)

After bootstrap, re-run your command.
+-------------------------------------------------------------------------+
```

**Exit workflow** - do not proceed until bootstrap is complete.

**Why This Matters**: Without bootstrap:
- Python tools won't be found
- CLAUDE.md won't reference the plugin properly
- Skill configuration won't exist
- The skill may appear to work but will fail mysteriously

### Step 0: Read Skill Configuration

Check for `.claude/powerbi-analyst.json` in the project directory:

```json
{
  "projectPath": "C:/Projects/SalesReport",
  "dataSensitiveMode": true
}
```

**`projectPath`:**
- If set → Use this as the default project location (skip project selection prompt)
- If null → Ask user for project path
- Can be a folder (will search for .pbip) or specific .pbip file

**`dataSensitiveMode`:**
- If `true` → Enforce anonymization check before any MCP data queries (Step 2 is required)
- If `false` → Proceed without anonymization checks (Step 2 can be skipped)

### Step 0.5: PBIX File Detection (CRITICAL - First Response)

**Purpose**: Immediately detect when user references a `.pbix` file and recommend conversion BEFORE any analysis begins.

**Check the user's provided path:**

1. If the path ends with `.pbix` (case-insensitive), this is a binary PBIX file
2. **STOP** - Do not proceed with any workflow

**Extract project name:** Remove `.pbix` extension from filename (e.g., `SalesReport.pbix` → `SalesReport`)

**Display this message IMMEDIATELY as the first response:**

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  📦 PBIX FILE DETECTED - CONVERSION REQUIRED                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  You've pointed to a .pbix file:                                          ║
║  <user-provided-path>                                                     ║
║                                                                           ║
║  PBIX is a compressed binary format that significantly limits analysis.   ║
║  To get full visibility into your DAX, M code, and visuals, you need     ║
║  to convert to the Power BI Project (.pbip) format.                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│  ⚠️  IMPORTANT: Each PBIP project needs its own folder!                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  When you save a PBIP project, Power BI creates MULTIPLE files:         │
│                                                                         │
│    <project-name>/                    ← Container folder (you create)   │
│    ├── <project-name>.pbip            ← Project file                    │
│    ├── <project-name>.SemanticModel/  ← Data model folder               │
│    └── <project-name>.Report/         ← Report folder                   │
│                                                                         │
│  Without a container folder, these files mix with other projects!       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Would you like me to create the project folder for you?

  [Y] Yes, create: <configured-projects-folder>/<project-name>/
      Then I'll guide you through the Save As steps.

  [N] No, I'll handle it myself
      (Make sure to create a folder first, then Save As PBIP inside it)

  [E] Explain extraction options (DAX-only, limited analysis)
```

**Variable Substitutions:**
- `<user-provided-path>`: The exact path the user provided
- `<configured-projects-folder>`: Read from `.claude/powerbi-analyst.json` → `projectPath`
  - If `projectPath` is null: Use "a short path like C:\PBI or D:\Projects"
- `<project-name>`: Extract from the .pbix filename (without extension)

**If user selects [Y] (Create folder for me):**

1. Create the folder using Bash:
   ```bash
   mkdir -p "<configured-projects-folder>/<project-name>"
   ```

2. Display success message with Save As instructions:
   ```
   ✅ Folder created: <configured-projects-folder>/<project-name>/

   Now complete the conversion in Power BI Desktop:
   ─────────────────────────────────────────────────
   1. Open Power BI Desktop
   2. File → Open → Select: <user-provided-pbix-path>
   3. File → Save As → Power BI Project (.pbip)
   4. Navigate to: <configured-projects-folder>/<project-name>/
   5. Click Save (use the default filename)

   When you're done, let me know and I'll analyze the project at:
   <configured-projects-folder>/<project-name>
   ```

3. Wait for user confirmation, then continue to Step 1 with the new path

**If user selects [N] (I'll handle it myself):**
- Remind them to create a containing folder first
- Display the recommended path structure
- Wait for them to provide the new PBIP folder path
- When they return with a path, continue to Step 1

**If user selects [E] (Explain extraction options):**
- Explain pbi-tools extraction option (DAX-only)
- Emphasize this is limited analysis without M code visibility
- Still recommend PBIP conversion for full analysis

**Why Each Project Needs Its Own Folder:**
- PBIP "Save As" creates 3+ items at the save location (not inside a single file)
- Without a container folder, multiple projects' files intermix
- This makes it impossible to identify which files belong to which project
- A clean folder structure enables working with multiple projects over time

**Why This Step is First:**
- Users often have .pbix files on their Desktop or Downloads folder
- The first response should guide them to the proper workflow
- Offering to create the folder removes friction from the conversion process
- This prevents wasted time analyzing a format with limited capabilities

### Step 1: Project Selection (Multi-Project Handling)

When the user provides a folder path (not a specific .pbip file):

1. Search for `*.pbip` files in the target folder
2. **If 1 project found**: Use it automatically
3. **If multiple projects found**: Ask user to select:
   ```
   Found N Power BI projects:
   1. ProjectA/ProjectA.pbip
   2. ProjectB/ProjectB.pbip

   Which project would you like to work with?
   ```
4. **If 0 projects found**: Report error and suggest checking the path

### Step 2: Anonymization Check (Before Data Queries)

**After selecting a specific project**, check for anonymization configuration:

1. Look for `.anonymization/config.json` **inside the project folder**
   - Correct: `ProjectA/.anonymization/config.json`
   - Wrong: `ParentFolder/.anonymization/config.json`

2. **If config exists**: Verify `DataMode` parameter is set appropriately before sampling data

3. **If config does NOT exist** and workflow will query data:
   ```
   ⚠️ This project doesn't have anonymization configured.
   MCP queries may expose sensitive data.

   Options:
   1. Set up anonymization first (/setup-data-anonymization --project "<path>")
   2. Proceed anyway (data is not sensitive)
   3. Work in file-only mode (no data queries)
   ```

### Safe Operations (No Anonymization Check Needed)

These operations don't expose data and can proceed without anonymization:
- `dax_query_operations.validate()` — syntax check only
- `measure_operations.list()` — metadata only
- `table_operations.list()` — metadata only
- File-based TMDL reads/edits

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

### VERSION_CHECK (Plugin Status)

**Use when:** User asks about plugin version, updates, tier (Pro/Free), or installation status.

**Trigger phrases:**
- "Check for updates"
- "What version am I running?"
- "Is Power BI Analyst up to date?"
- "Am I on Pro or Free?"
- "Update the plugin"

**Process:**

1. **Read Plugin Metadata**
   - Load `.claude-plugin/plugin.json` from plugin installation directory
   - Extract: `version`, `repository`
   - Detect edition: Check if `skills/powerbi-analyst/pro-features.md` exists (Pro) or not (Core)

2. **Read Project Version (if bootstrapped)**
   - Check `.claude/tools/powerbi-analyst/version.txt` in current project
   - Compare with plugin version

3. **Report Status**
   ```
   ┌──────────────────────────────────────────────────┐
   │ Power BI Analyst Status                          │
   ├──────────────────────────────────────────────────┤
   │ Plugin (global):                                 │
   │   Version:  1.3.0 (Pro edition)                  │
   │   Location: ~/.claude/plugins/custom/powerbi-*  │
   ├──────────────────────────────────────────────────┤
   │ Project (local):                                 │
   │   Version:  1.2.0  ← Update available            │
   │   Location: .claude/tools/powerbi-analyst/       │
   ├──────────────────────────────────────────────────┤
   │ Update Instructions:                             │
   │   Plugin:  cd ~/.claude/plugins/custom/power*    │
   │            git pull                              │
   │   Project: Run bootstrap.ps1 from project dir   │
   └──────────────────────────────────────────────────┘
   ```

4. **If Update Requested**
   - Provide step-by-step update commands
   - Warn about any breaking changes (if known)

**Output:** Version status report with update instructions if needed

**Plugin metadata location:** `$HOME/.claude/plugins/custom/powerbi-analyst/.claude-plugin/plugin.json`

**See also:** `references/update-info.md` for detailed update procedures

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
├── CLAUDE.md                        ← Project instructions
├── .claude/
│   ├── powerbi-analyst.json         ← Skill configuration
│   ├── settings.json                ← Permissions
│   ├── tasks/                       ← Task findings files
│   ├── tools/
│   │   ├── powerbi-analyst/         ← Plugin tools (isolated)
│   │   │   ├── token_analyzer.py
│   │   │   ├── tmdl_format_validator.py
│   │   │   ├── version.txt
│   │   │   └── ...
│   │   └── (your scripts here)      ← Safe from overwrites
│   └── helpers/
│       ├── powerbi-analyst/         ← Plugin helpers (isolated)
│       │   └── pbi-url-filter-encoder.md
│       └── (your files here)        ← Safe from overwrites
└── YourProject.pbip
```

### Version Tracking

The bootstrap script tracks versions to manage updates:

| Command | Purpose |
|---------|---------|
| `bootstrap.ps1` | Install/update tools if needed |
| `bootstrap.ps1 -CheckOnly` | Check if update available (exit code 1 = update needed) |
| `bootstrap.ps1 -Force` | Force reinstall even if current |

### Updating the Plugin

To update this skill to the latest version:

**Step 1: Pull latest plugin code**
```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull
```

**Step 2: Update project tools (run from your project directory)**
```powershell
cd "C:\path\to\your\project"
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

**Quick check if update is available:**
```powershell
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1" -CheckOnly
# Exit code 1 = update available, 0 = current
```

**Plugin location:** `$HOME\.claude\plugins\custom\powerbi-analyst\`

### What Gets Overwritten on Update

| File | Behavior | Safe to Customize? |
|------|----------|-------------------|
| `CLAUDE.md` | Prompts before appending | ✅ Yes |
| `.claude/settings.json` | Skips if exists | ✅ Yes |
| `.claude/powerbi-analyst.json` | Skips if exists | ✅ Yes |
| `.claude/tasks/*` | Not touched | ✅ Yes |
| `.claude/tools/powerbi-analyst/*` | Overwritten | ❌ No (plugin-managed) |
| `.claude/helpers/powerbi-analyst/*` | Overwritten | ❌ No (plugin-managed) |
| `.claude/tools/*.py` (root) | Not touched | ✅ Yes (your scripts) |
| `.claude/helpers/*` (root) | Not touched | ✅ Yes (your files) |

**Important:** Only the `powerbi-analyst/` subfolders are plugin-managed. Your own scripts in `.claude/tools/` or `.claude/helpers/` are safe.

To customize behavior, edit:
- `.claude/settings.json` - Permissions and Claude Code settings
- `.claude/powerbi-analyst.json` - Skill configuration
- `CLAUDE.md` - Project-specific instructions

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

## Tracing & Observability

The skill provides structured trace output to show workflow progress, agent invocations, and MCP tool usage.

### Trace Output Format

**Workflow Start:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: [workflow-name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase Markers:**
```
📋 PHASE [N]: [Phase Name]
   └─ [Description of what's happening]
```

**Agent Invocations:**
```
   └─ 🤖 [AGENT] [agent-name]
   └─    Starting: [brief description]
   └─ 🤖 [AGENT] [agent-name] complete
   └─    Result: [summary]
```

**MCP Tool Calls:**
```
   └─ 🔌 [MCP] [tool-name]
   └─    [parameters or context]
   └─    ✅ Success: [result summary]
   └─    ❌ Error: [error message]
```

**Workflow Complete:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: [workflow-name]
   └─ Output: [file path or summary]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Icon Reference

| Icon | Meaning |
|------|---------|
| 🚀 | Workflow start |
| 📋 | Phase/step |
| 🤖 | Agent invocation |
| 🔌 | MCP tool call |
| 📂 | File operation |
| 🔍 | Search/discovery/validation |
| ✏️ | Edit/write |
| ✅ | Success |
| ❌ | Error/failure |
| ⚠️ | Warning |

See `resources/tracing-conventions.md` for complete tracing documentation.

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
- `update-info.md` - Version management, update procedures, edition detection

---

## Quick Start

1. **Have a problem?** → "Help me fix the YoY calculation in my Sales dashboard"
2. **Want something new?** → "Create a margin percentage measure"
3. **Need a whole page?** → "Build a regional performance dashboard page"
4. **Ready to apply?** → "Implement the changes from findings.md"
5. **Want to understand?** → "Analyze this dashboard and explain what it does"
6. **Check version/updates?** → "What version of Power BI Analyst am I running?"
7. **Update the plugin?** → "Check for Power BI Analyst updates"

---

## Pro Features

> **Note:** The following features require the Pro version of this plugin.
> If `pro-features.md` exists in this skill folder, those additional capabilities are available.

**Pro capabilities include:**
- **Template Harvesting** - Extract reusable visual templates from existing dashboards
- **UX Dashboard Review** - Expert analysis of published dashboards using Playwright
- **Advanced Testing** - Browser-based visual validation and interaction testing

See `pro-features.md` for full Pro documentation (Pro version only).
