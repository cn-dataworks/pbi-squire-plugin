# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment workflows.

## Installation

```bash
/plugin install powerbi-analyst@github/cn-dataworks/powerbi-analyst-plugin
```

## Features

### Commands

- **`/evaluate-pbi-project-file`** - Analyze and diagnose Power BI project issues
- **`/create-pbi-artifact`** - Create new measures, calculated columns, tables, or visuals
- **`/implement-deploy-test-pbi-project-file`** - Implement changes and optionally deploy
- **`/merge-powerbi-projects`** - Compare and merge two Power BI projects

### Skills

- **`power-bi-assistant`** - Interactive workflow guidance and command builder
- **`agentic-workflow-reviewer`** - Workflow quality validation and best practices

### Agents

23+ specialized agents for:
- Project validation and verification
- Data model analysis and understanding
- Code location and modification
- Visual editing (PBIR format)
- Quality assurance and validation
- Project merging and comparison

## Documentation

See [.claude/README.md](.claude/README.md) for comprehensive documentation including:
- Detailed command usage and parameters
- Agent descriptions and capabilities
- Complete workflow sequences
- Best practices and troubleshooting

## Requirements

- Claude Code (latest version)
- Python 3.10+
- Power BI Desktop (for testing generated code)
- Optional: Power BI Service access (for deployment and data sampling)

## Related Projects

- **[Power BI Analyst Desktop](https://github.com/cn-dataworks/powerbi-analyst-desktop)** - GUI desktop application version of this plugin (coming soon)

## License

Proprietary - All rights reserved.

## Support

For issues and feature requests, please use [GitHub Issues](https://github.com/cn-dataworks/powerbi-analyst-plugin/issues).
