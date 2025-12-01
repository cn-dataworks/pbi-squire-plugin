# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment workflows.

## Installation

### From GitHub (Recommended)

```bash
# Add the marketplace
/plugin marketplace add cn-dataworks/powerbi-analyst-plugin

# Install the plugin
/plugin install powerbi-analyst@cn-dataworks/powerbi-analyst-plugin

# Verify installation
/plugin list
```

### From Local Development

For local development and testing:

```bash
# Clone the repository
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git
cd powerbi-analyst-plugin

# Add as local marketplace (use absolute path)
/plugin marketplace add C:\path\to\powerbi-analyst-plugin

# Install from local marketplace
/plugin install powerbi-analyst@C:\path\to\powerbi-analyst-plugin
```

## Troubleshooting

### Slash commands not appearing after installation

**Known Issue:** The plugin marketplace may show the plugin as "installed" but the actual files aren't copied to your repository. You can verify this by checking if `.claude/commands/` exists:

```bash
ls .claude/commands/
```

If this directory doesn't exist or is empty, use manual installation below.

### Manual Installation

If the plugin installation doesn't copy files properly, manually copy them:

**Windows (PowerShell):**
```powershell
# Clone the plugin temporarily
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git C:\temp\pbi-plugin

# Copy the .claude folder contents to your target repository
xcopy /E /I /Y "C:\temp\pbi-plugin\.claude\*" ".claude\"

# Clean up
rmdir /S /Q C:\temp\pbi-plugin
```

**macOS/Linux:**
```bash
# Clone the plugin temporarily
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git /tmp/pbi-plugin

# Copy the .claude folder contents to your target repository
cp -r /tmp/pbi-plugin/.claude/* .claude/

# Clean up
rm -rf /tmp/pbi-plugin
```

**After manual installation:**
1. Restart Claude Code (exit with `/exit` or Ctrl+C, then run `claude` again)
2. Type `/` to verify commands appear:
   - `/evaluate-pbi-project-file`
   - `/create-pbi-artifact`
   - `/implement-deploy-test-pbi-project-file`
   - `/analyze-pbi-dashboard`
   - `/create-pbi-page-specs`

### Commands still not appearing

1. **Verify files exist:** Check that `.claude/commands/*.md` files are present
2. **Restart Claude Code:** Commands are loaded at startup
3. **Check directory:** Make sure you're running Claude Code from the repository where you installed the plugin

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

## Sandboxing Configuration

The plugin uses Claude Code's permission system to control file access. Permissions are split between project settings (shared) and local settings (personal).

### Quick Setup

1. Copy the template to create your local settings:
   ```bash
   cp .claude/settings.local.json.template .claude/settings.local.json
   ```

2. Edit `.claude/settings.local.json` and replace `YOUR_USERNAME` with your Windows username

3. Add any additional project folders you work with

### Configuration Files

| File | Purpose | Git Status |
|------|---------|------------|
| `.claude/settings.json` | Core plugin permissions (bash, web, MCP) | Committed |
| `.claude/settings.local.json` | Your project folder paths | Ignored |
| `.claude/settings.local.json.template` | Template for new users | Committed |

### Adding Project Folders

To allow Claude Code to work on a Power BI project folder, add these lines to your `settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(C:/Users/YourName/Documents/Customer Projects/ProjectName/**)",
      "Edit(C:/Users/YourName/Documents/Customer Projects/ProjectName/**)",
      "Write(C:/Users/YourName/Documents/Customer Projects/ProjectName/**)"
    ]
  }
}
```

### Path Format

- Use forward slashes: `C:/Users/Name/folder/**`
- Use `**` for recursive matching
- `Read()` = read files, `Edit()` = modify existing files, `Write()` = create new files

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
