# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment.

## Quick Install

### Option A: Direct Install (Recommended)

Run these commands inside Claude Code:

```
/plugin marketplace add https://github.com/cn-dataworks/powerbi-analyst-plugin
/plugin install powerbi-analyst
```

That's it! The plugin is now available in all your projects.

### Option B: Git Clone (For Contributors)

If you plan to contribute or need offline access:

```powershell
# 1. Clone the repository
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"

# 2. Run installer
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
.\install-plugin.ps1
```

### Bootstrap (per project)

In each Power BI project, run the bootstrap tool to configure project-specific settings:

```powershell
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

This creates:
- `CLAUDE.md` - Project instructions
- `.claude/settings.json` - Permissions
- `.claude/tools/` - Local tool copies

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
   cd "$HOME\.claude\plugins\custom\powerbi-analyst"
   .\install-plugin.ps1
   ```

## How It Works

### One Install, All Projects

The plugin installs **once** to a central location on your computer:

```
C:\Users\YourName\.claude\plugins\custom\powerbi-analyst\
```

After installation, it's automatically available in **every project** you open with Claude Code. No per-project setup required.

### Per-Project Control

**Disable in a specific project** - Create `.claude/settings.json` in that project:

```json
{
  "plugins": {
    "powerbi-analyst": {
      "enabled": false
    }
  }
}
```

**Enable only in specific projects** - Skip the global install, then add to each project's `.claude/settings.json`:

```json
{
  "plugins": {
    "powerbi-analyst": {
      "path": "C:\\Users\\YourName\\.claude\\plugins\\custom\\powerbi-analyst"
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

## Skills

| Skill | Description |
|-------|-------------|
| `powerbi-analyst` | Main skill - diagnose issues, create measures/visuals, deploy changes |
| `power-bi-assistant` | Guides you to the right workflow command |
| `powerbi-dashboard-analyzer` | Analyzes dashboards in business-friendly language |
| `powerbi-data-prep` | M code and Power Query transformations |

## Key Workflows

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose Power BI project issues |
| `/create-pbi-artifact` | Create new measures, columns, tables, or visuals |
| `/implement-deploy-test-pbi-project-file` | Implement, deploy, and test changes |
| `/merge-powerbi-projects` | Compare and merge two Power BI projects |

## Quick Start

1. Install the plugin (see above)
2. Navigate to a folder containing a `.pbip` project
3. Ask Claude: "Help me fix the YoY growth measure" or "Create a new sales dashboard page"
4. Claude will guide you through the appropriate workflow

## Visual Templates

The skill includes 17 PBIR visual templates for generating new visuals. Templates are bundled with the skill and work offline.

### Using Templates

Templates are used automatically when you create visuals via `/create-pbi-artifact`. The skill selects the appropriate template based on your request.

## Updating

**If you used Option A (Direct Install):**

```
/plugin update powerbi-analyst
```

**If you used Option B (Git Clone):**

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull; if ($?) { claude -c "/plugin update powerbi-analyst" }
```

## Requirements

- Claude Code (latest version)
- Python 3.10+
- Power BI Desktop (for testing)
- Optional: Power BI Service access (for deployment)

## Structure

```
powerbi-analyst-plugin/
├── skills/
│   ├── powerbi-analyst/           # Main skill with 20+ agents
│   │   ├── agents/                # Specialized agents
│   │   ├── workflows/             # Workflow definitions
│   │   └── resources/
│   │       └── visual-templates/  # 17 bundled templates
│   ├── power-bi-assistant/        # User guidance
│   ├── powerbi-dashboard-analyzer/# Dashboard analysis
│   └── powerbi-data-prep/         # M code specialist
├── tools/                         # Python utilities
└── .mcp.json                      # Playwright MCP for testing
```

## License

Proprietary - All rights reserved.

## Support

For issues: [GitHub Issues](https://github.com/cn-dataworks/powerbi-analyst-plugin/issues)
