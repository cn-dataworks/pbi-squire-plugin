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

### Bootstrap (per project)

In each Power BI project, run the bootstrap tool to configure project-specific settings:

```powershell
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
```

This creates:
- `CLAUDE.md` - Project instructions
- `.claude/settings.json` - Permissions
- `.claude/pbi-squire.json` - Skill configuration

**For Developer Edition:** Also copies Python analysis tools to `.claude/tools/`

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

After installation, it's automatically available in **every project** you open with Claude Code. No per-project setup required.

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
