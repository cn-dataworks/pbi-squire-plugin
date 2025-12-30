# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment.

## Quick Install (Recommended)

### One-Line Install (PowerShell)

```powershell
irm https://raw.githubusercontent.com/cn-dataworks/powerbi-analyst-plugin/main/install-plugin.ps1 | iex
```

Or download and run manually:

```powershell
.\install-plugin.ps1
```

### Manual Install

```powershell
# Step 1: Clone the repository
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"

# Step 2: Register with Claude Code
claude -c "/plugin install $HOME\.claude\plugins\custom\powerbi-analyst"

# Step 3: Verify
claude -c "/plugin list"
```

See [INSTALL.md](INSTALL.md) for detailed instructions and team setup.

### MCP Detection

The installer automatically detects **Power BI Modeling MCP** and configures it if found:

- **Desktop Mode** (MCP found): Full validation, live DAX checking
- **File-Only Mode** (no MCP): Core features work, no live validation

To enable full features after installing MCP, re-run the installer:
```powershell
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

### Contributing Templates

You can contribute new templates from your own reports:

```
/harvest-templates     Extract templates from your report
/review-templates      Compare against existing library
/promote-templates     Submit PR to public repository
```

## Updating

```powershell
# Re-run the installer to pull latest changes
.\install-plugin.ps1

# Or manually:
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull
```

## Requirements

- Claude Code (latest version)
- Python 3.10+
- Power BI Desktop (for testing)
- Optional: Power BI Service access (for deployment)
- Optional: GitHub CLI (`gh`) for template promotion

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
