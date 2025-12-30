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
