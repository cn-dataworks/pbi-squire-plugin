# PBI Squire Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment.

## Quick Install

### Option A: Direct Install (Recommended)

Run these commands inside Claude Code:

```
/plugin marketplace add https://github.com/cn-dataworks/pbi-squire-plugin
/plugin install pbi-squire
```

That's it! The plugin is now available in all your projects.

### Option B: Git Clone (For Contributors)

If you plan to contribute or need offline access:

```powershell
# 1. Clone the repository
git clone https://github.com/cn-dataworks/pbi-squire-plugin.git "$HOME\.claude\plugins\custom\pbi-squire"

# 2. Run installer
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1
```

### First-Time Setup (Automatic)

**No bootstrap required!** When you first invoke the skill, PBI Squire automatically:

1. Detects Power BI projects in your folder
2. Asks about data sensitivity settings
3. Creates configuration files inline
4. Continues with your request

```
You: "Help me fix this YoY measure"

PBI Squire: "Let me configure PBI Squire for this location...
             Found 1 Power BI project: SalesReport.pbip
             Does this project contain sensitive data? [Y/N]"

You: "N"

PBI Squire: "✅ Configured! Now let me help with that YoY measure..."
```

### Bootstrap (Optional)

Bootstrap is **optional** for Analyst Edition but recommended for Developer Edition:

| Edition | Bootstrap Required? | What It Does |
|---------|---------------------|--------------|
| **Analyst** | No (auto-configures) | Creates config files only |
| **Developer** | Recommended | Installs Python tools for faster performance |

```powershell
# Optional: Run bootstrap for explicit control or Developer Edition Python tools
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
```

See [INSTALL.md](INSTALL.md) for detailed instructions and team setup.

### MCP (Recommended for Writing)

**Install Power BI Modeling MCP** if you plan to create or edit DAX/M code:

| Mode | Reading | Writing |
|------|---------|---------|
| File-Only (no MCP) | ✅ Works | ⚠️ No compile validation |
| Desktop Mode (MCP) | ✅ Works | ✅ Validates before writing |

**Install via VS Code (Recommended):**
1. Open VS Code → Extensions (Ctrl+Shift+X)
2. Search "Power BI Modeling MCP" → Install (by Analysis Services)
3. Re-run installer:
   ```powershell
   cd "$HOME\.claude\plugins\custom\pbi-squire"
   .\install-plugin.ps1
   ```

## How It Works

### One Install, All Projects

The plugin installs **once** to a central location on your computer:

```
C:\Users\YourName\.claude\plugins\custom\pbi-squire\
```

After installation, it's automatically available in **every project** you open with Claude Code.

**First-time setup is automatic:** When you first use the skill in a new project, it auto-configures itself inline. No separate bootstrap step required for Analyst Edition.

### Per-Project Control

**Disable in a specific project** - Create `.claude/settings.json` in that project:

```json
{
  "plugins": {
    "pbi-squire": {
      "enabled": false
    }
  }
}
```

**Enable only in specific projects** - Skip the global install, then add to each project's `.claude/settings.json`:

```json
{
  "plugins": {
    "pbi-squire": {
      "path": "C:\\Users\\YourName\\.claude\\plugins\\custom\\pbi-squire"
    }
  }
}
```

> **Note**: The plugin's skills only activate when they detect Power BI files (`.pbip`, `.SemanticModel/`). In non-Power BI projects, the skills won't trigger even if the plugin is installed globally.

### Auto-Approve Permissions

Bootstrap creates `.claude/settings.json` with permissions so common tools run without prompts:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Edit",
      "Write",
      "Bash(python *)",
      "Bash(git *)"
    ]
  }
}
```

Customize by editing `.claude/settings.json`. See [INSTALL.md](INSTALL.md#auto-approve-permissions) for details.

## Skill

This plugin provides one comprehensive skill:

**`pbi-squire`** - Complete Power BI development assistant

| Capability | Description |
|------------|-------------|
| Diagnose & Fix | EVALUATE workflow - fix calculation issues |
| Create Artifacts | CREATE_ARTIFACT workflow - new measures, columns, tables |
| Transform Data | DATA_PREP workflow - M code / Power Query |
| Document | SUMMARIZE workflow - business-friendly dashboard docs |
| Deploy | IMPLEMENT workflow - apply changes with validation |
| Merge Projects | MERGE workflow - compare and combine projects |

The skill automatically routes your requests to the appropriate workflow. Just describe what you need.

## Key Workflows

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose Power BI project issues |
| `/create-pbi-artifact-spec` | Create new measures, columns, tables, or visuals |
| `/implement-deploy-test-pbi-project-file` | Implement, deploy, and test changes |
| `/merge-powerbi-projects` | Compare and merge two Power BI projects |

## Architecture

### How Requests Flow Through the Plugin

When you ask Claude to help with Power BI, the request flows through two layers:

```
┌─────────────────────────────────────────────────────────────────┐
│  SKILL + WORKFLOW (SKILL.md + workflows/*.md)                   │
│  Routes your request to the appropriate workflow based on       │
│  trigger phrases. Main thread executes workflow phases and      │
│  spawns leaf subagents via Task().                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Task(powerbi-code-locator)
                              │ Task(powerbi-visual-locator)
                              │ Task(powerbi-dax-review-agent)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LEAF SUBAGENTS (24+ agents)                                    │
│  Each agent has focused expertise: code location, DAX review,   │
│  visual editing, M code transforms, validation, etc.            │
│  Subagents do NOT spawn other subagents (leaf node pattern).    │
└─────────────────────────────────────────────────────────────────┘
```

### Task Blackboard Pattern

Agents coordinate through a shared `findings.md` file:

1. **Main thread** creates `findings.md` with the problem statement
2. **Investigation agents** write to Section 1 (what they found)
3. **Planning agents** read Section 1, write to Section 2 (proposed changes)
4. **Validation agents** read Section 2, write to Section 2.5-2.7 (pass/fail)
5. **Implementation agents** read Section 2, apply changes

Each agent only sees its assigned sections—they're isolated from the broader workflow.

### Workflow Routing

| You Say | Detected Intent | Workflow | Has Validation Phase? |
|---------|-----------------|----------|----------------------|
| "Fix this measure" | Problem to solve | EVALUATE | Yes (proposes changes) |
| "How is this calculated?" | Question to answer | SUMMARIZE | No (read-only) |
| "Create a YoY measure" | New artifact | CREATE_ARTIFACT | Yes |
| "Apply the changes" | Execute plan | IMPLEMENT | Yes |

The main thread picks the workflow based on keywords, and each workflow has a predefined phase sequence. Read-only workflows (SUMMARIZE) skip validation phases because there are no changes to validate.

### Agent Invocation

The main thread spawns agents using Claude Code's `Task()` tool:

```
Task(powerbi-visual-locator):
  "Locate the bar chart in the upper right with title 'Revenue'

   Task memory: agent_scratchpads/.../findings.md
   Write to: Section 1.B
   Project: C:/Projects/SalesReport"
```

The agent receives:
- A task prompt with natural language instructions
- The path to `findings.md` for reading/writing
- The project path

The agent does the work (e.g., translates "upper right bar chart" into actual file paths by reading PBIR coordinates), writes results to its section, and returns.

## Quick Start

1. Install the plugin (see above)
2. Navigate to a folder containing a `.pbip` project
3. Ask Claude: "Help me fix the YoY growth measure" or "Create a new sales dashboard page"
4. Claude will guide you through the appropriate workflow

## Multi-Project Setup

When managing multiple Power BI projects that need separate context — such as different departments, business units, or clients — use a **one repository per project group** structure. This gives each project group its own `CLAUDE.md` with tailored business context, and keeps git history, permissions, and deployment pipelines cleanly separated.

### Recommended Structure

Create a separate git repository for each independent group of dashboards. The repository **is** the Power BI folder — `.pbip` projects sit at the root alongside `CLAUDE.md`. Multiple dashboards that share the same business context (same team, same client, same division) belong in the same repo:

```
your-org/
├── sales-pbi/                     # Repo: Sales department dashboards
│   ├── .gitignore
│   ├── CLAUDE.md                  # Sales-specific context & conventions
│   ├── .claude/
│   │   └── settings.json         # Recommended permissions (see below)
│   ├── SalesExec.pbip/            # Dashboard 1
│   │   ├── SalesExec.pbip
│   │   ├── SalesExec.SemanticModel/
│   │   └── SalesExec.Report/
│   └── SalesRegional.pbip/        # Dashboard 2 (same team, same repo)
│       ├── SalesRegional.pbip
│       ├── SalesRegional.SemanticModel/
│       └── SalesRegional.Report/
│
├── finance-pbi/                   # Repo: Finance department dashboards
│   ├── .gitignore
│   ├── CLAUDE.md
│   ├── .claude/
│   │   └── settings.json
│   └── FinanceReview.pbip/
│
└── ops-pbi/                       # Repo: Operations dashboards
    ├── .gitignore
    ├── CLAUDE.md
    ├── .claude/
    │   └── settings.json
    └── OpsMonitoring.pbip/
```

**Multiple dashboards in one repo:** If dashboards share the same business context, naming conventions, and stakeholders, they belong together. The shared `CLAUDE.md` gives Claude consistent context across all of them. Only split into separate repos when dashboards have genuinely different business contexts or access requirements.

On your local machine or server, mirror this as separate clones:

```
/home/user/projects/
├── sales-pbi/          ← git@github.com:your-org/sales-pbi.git
├── finance-pbi/        ← git@github.com:your-org/finance-pbi.git
└── ops-pbi/            ← git@github.com:your-org/ops-pbi.git
```

### Why Separate Repos

| Concern | Separate Repos | Single Repo |
|---------|---------------|-------------|
| **CLAUDE.md context** | Tailored per project group | One file trying to serve everything |
| **Git history** | Clean, scoped to one group | Noisy, mixes unrelated changes |
| **Access control** | Grant access per repo | All-or-nothing |
| **Plugin behavior** | Clean `.pbip` discovery | Ambiguous project targeting |
| **CI/CD** | Independent pipelines | Complex path-based filtering |

### Per-Project CLAUDE.md Template

Each repository should have a `CLAUDE.md` at the root that enforces plugin usage and provides business context. Adapt this template for each project group:

```markdown
# [Project Group Name] — Power BI Projects

## MANDATORY TOOLS — READ FIRST

**You MUST use the pbi-squire plugin for ALL Power BI work in this repository.**
- Invoke `/pbi-squire` for any task involving DAX, M code, TMDL, visuals,
  or model changes.
- Do NOT manually edit TMDL, PBIR JSON, or model definition files directly.
  Always route through the plugin's workflows (EVALUATE, CREATE_ARTIFACT,
  DATA_PREP, IMPLEMENT, etc.).
- The plugin provides specialist agents for code location, validation, review,
  and implementation. Use them — do not bypass them with raw file edits.

**You MUST use the Power BI Modeling MCP server for live semantic model
operations.**
- Use the MCP tools for reading model metadata, testing DAX queries, and
  validating changes against the live model.
- Before modifying any measure, column, or relationship, query the current
  state through the MCP server to confirm what exists.
- After implementing changes, use the MCP server to verify the changes were
  applied correctly.
- If the MCP server is unavailable (model not connected), fall back to
  file-based TMDL — but always attempt MCP first.

**Workflow enforcement:**
1. Diagnose/investigate → use EVALUATE workflow via the plugin
2. Create new measures/columns/visuals → use CREATE_ARTIFACT workflow
3. Power Query / M code changes → use DATA_PREP workflow
4. Document a dashboard → use SUMMARIZE workflow
5. Apply planned changes → use IMPLEMENT workflow
6. Compare projects → use MERGE workflow

Do NOT skip plugin workflows. Do NOT edit .tmdl or visual.json files with
the Edit tool directly. The plugin's agents handle validation, naming
conventions, and consistency checks that manual edits will miss.

---

## Business Context
- Industry / Department: [e.g., Finance, Sales, Operations]
- Key stakeholders: [who sees these dashboards]
- Reporting cadence: [monthly, weekly, daily]

## Projects in This Repo
| Folder | Dashboard | Workspace | Refresh |
|--------|-----------|-----------|---------|
| `ProjectName.pbip` | Dashboard Name | Workspace Name | Schedule |

## Naming Conventions
- Measures prefix: [e.g., "m_" or none]
- Calculated columns prefix: [e.g., "cc_"]
- Measure folders: [how measure groups are organized]
- Date table name: [e.g., "DimDate", "Calendar"]

## Business Terminology
- [Term] = [Definition]

## Data Sources
- [Source] → [what it feeds]

## Deployment Notes
- Production workspace: [workspace name]
- Gateway: [gateway name if relevant]
- Refresh schedule: [when and how]

## Change Management
- All changes go through feature branches
- PRs required before merging to main
- main = what's deployed to Power BI Service

## Known Quirks
- [Anything unusual about the data model or environment]
```

### Recommended .gitignore for Power BI Repos

```gitignore
# Power BI local cache and build artifacts
*.pbir.json.bak
*.pbi/
*.pbit
.pbi/
localSettings.json

# Dataset cache
*.SemanticModel/model.bim
*.SemanticModel/.pbi/

# Report cache
*.Report/.pbi/

# Never commit data files
*.pbix
*.xlsx
*.csv

# OS / editor
.DS_Store
Thumbs.db
*.swp
```

Commit the TMDL definition files and PBIR JSON. Never commit binary caches, data extracts, or `.pbix` files.

### Recommended Permissions

Each Power BI repository should include a `.claude/settings.json` that auto-approves the tools the plugin needs. Without this, Claude Code will prompt for permission on every file read and edit, which slows down the multi-agent workflows significantly.

Create `.claude/settings.json` in each repo:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Edit",
      "Write",
      "Bash(python *)",
      "Bash(git *)"
    ]
  }
}
```

| Permission | Why It's Needed |
|-----------|-----------------|
| `Read` | Agents read TMDL, PBIR JSON, and M code files during investigation |
| `Glob` | Agents discover `.pbip` projects, visual folders, and table definitions |
| `Grep` | Agents search for measure references, relationship patterns, and dependencies |
| `Edit` | Implementation agents apply changes to TMDL and PBIR files |
| `Write` | Agents write `findings.md` (task blackboard) and new visual files |
| `Bash(python *)` | Developer Edition Python tools for validation and analysis |
| `Bash(git *)` | Git operations for committing and branching |

Commit this file to the repo so permissions are consistent for anyone who clones it.

### Working Across Projects

Switch between project groups by changing directories. Each Claude Code session picks up the local `CLAUDE.md` automatically:

```bash
cd /home/user/projects/sales-pbi && claude     # Sales context
cd /home/user/projects/finance-pbi && claude   # Finance context
```

You can run multiple terminal sessions simultaneously — each Claude Code instance is independent.

### Non-Power BI Code

If you also maintain applications, ETL pipelines, or other code for the same team or client, keep those in their own repositories. Do **not** nest Power BI projects inside an app repo or vice versa. Each repo gets a `CLAUDE.md` tuned for its contents:

```
your-org/
├── sales-pbi/              # Power BI dashboards (CLAUDE.md enforces plugin)
├── sales-webapp/           # Web application (CLAUDE.md has app conventions)
├── sales-etl/              # Data pipelines (CLAUDE.md has pipeline context)
├── finance-pbi/            # Power BI dashboards
└── finance-api/            # Backend API
```

Mixing Power BI projects with unrelated codebases in a single repo creates conflicting `CLAUDE.md` instructions, noisy git history, and complicated access controls. The Power BI repo's `CLAUDE.md` mandates plugin usage and MCP enforcement — those directives don't make sense in an app repo, and app-specific instructions (test runners, linters, frameworks) don't belong in a Power BI repo.

### Consultancy & Multi-Client Note

This structure works identically for consultancies managing multiple clients. Replace department/division names with client names and use **private repositories** — client Power BI models contain business logic, KPIs, and potentially connection strings. Tag dashboard releases (e.g., `v2026.Q1`) so you can track and roll back deployments per client.

## Visual Templates

The skill includes 17 PBIR visual templates for generating new visuals. Templates are bundled with the skill and work offline.

### Using Templates

Templates are used automatically when you create visuals via `/create-pbi-artifact-spec`. The skill selects the appropriate template based on your request.

## Updating

**If you used Option A (Direct Install):**

```
/plugin update pbi-squire
```

**If you used Option B (Git Clone):**

```powershell
cd "$HOME\.claude\plugins\custom\pbi-squire"
git pull; if ($?) { claude -c "/plugin update pbi-squire" }
```

## Requirements

### Analyst Edition (Default)
- Claude Code (latest version)
- Power BI Desktop (for testing)
- **Recommended:** Power BI Modeling MCP (for live validation)

### Developer Edition (Additional)
- Python 3.10+ (for advanced analysis tools)
- Power BI Service access (for deployment)

### Tool-First Fallback Pattern

The plugin uses a **tool-first fallback pattern** to optimize performance while ensuring all users have full functionality.

| Edition | Python Tools | How It Works |
|---------|--------------|--------------|
| **Core** | Not installed | Uses Claude-native approaches (Read, Edit, reference docs) |
| **Pro** | Installed via bootstrap | Uses Python tools for faster, deterministic execution |

**Both editions have identical functionality.** The difference is execution speed and token usage:

- **Pro tools** execute in milliseconds with lower token cost
- **Core fallback** uses Claude's reasoning against reference docs (slower, more tokens, same results)

**How it works at runtime:**

```
Agent checks: Does .claude/tools/tmdl_format_validator.py exist?
  ├─ Yes (Developer) → Run Python tool (fast, deterministic)
  └─ No (Analyst) → Claude validates against tmdl_partition_structure.md (slower, same result)
```

**Example tasks affected:**

| Task | Pro Tool | Core Fallback |
|------|----------|---------------|
| TMDL validation | `tmdl_format_validator.py` | Claude + `tmdl_partition_structure.md` |
| Sensitive column detection | `sensitive_column_detector.py` | Claude + `anonymization-patterns.md` |
| M code pattern analysis | `m_pattern_analyzer.py` | Claude reads and analyzes TMDL directly |

**Pro tools** are available from a private repository. Contact the maintainers for access. Analyst Edition is fully functional without them.

## Structure

```
pbi-squire-plugin/
├── agents/                        # Leaf subagent definitions
│   ├── core/                      # Core agents (23 agents, all editions)
│   │   ├── powerbi-code-locator.md    # Finds DAX/M code
│   │   ├── powerbi-visual-locator.md  # Finds PBIR visuals
│   │   ├── powerbi-dax-specialist.md  # DAX expertise
│   │   └── ...                        # 20 more specialists
│   └── pro/                       # Developer-only agents (3 agents)
│       ├── powerbi-playwright-tester.md
│       ├── powerbi-ux-reviewer.md
│       └── powerbi-qa-inspector.md
│
├── skills/
│   └── pbi-squire/           # Main skill definition
│       ├── SKILL.md               # Skill routing & capabilities
│       ├── workflows/             # Detailed workflow definitions
│       │   ├── evaluate-pbi-project-file.md
│       │   ├── create-pbi-artifact-spec.md
│       │   ├── implement-deploy-test-pbi-project-file.md
│       │   └── ...                # 7 more workflows
│       ├── references/            # Technical reference docs
│       ├── resources/             # Runtime resources
│       │   └── visual-templates/  # 17 PBIR templates
│       └── assets/                # Report templates
│
├── tools/                         # Bootstrap & utilities
│   ├── bootstrap.ps1              # Windows project setup
│   ├── bootstrap.sh               # macOS/Linux project setup
│   └── core/                      # Python tools (Developer Edition)
│
└── .mcp.json                      # Playwright MCP config
```

### Key Files by Purpose

| File | Purpose |
|------|---------|
| `SKILL.md` | Routes requests to workflows, defines triggers |
| `workflows/*.md` | Detailed step-by-step workflow logic (executed by main thread) |
| `references/orchestration-pattern.md` | Routing logic and quality gate reference |
| `agents/analyst/*.md` | Leaf subagent definitions (do not spawn other subagents) |
| `findings.md` (runtime) | Shared document for agent coordination |

## License

Proprietary - All rights reserved.

## Support

For issues: [GitHub Issues](https://github.com/cn-dataworks/pbi-squire-plugin/issues)
