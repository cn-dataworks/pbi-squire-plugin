# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment.

## Installation

```bash
# Add the marketplace (one-time)
/plugin marketplace add cn-dataworks/powerbi-analyst-plugin

# Install the plugin
/plugin install powerbi-analyst@cn-dataworks-powerbi-analyst-plugin

# Verify installation
/plugin list
```

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
