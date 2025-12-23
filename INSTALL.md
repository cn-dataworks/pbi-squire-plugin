# Installing the Power BI Analyst Plugin

This plugin provides Power BI development assistance including DAX/M code generation, dashboard analysis, and PBIR visual editing.

---

## Quick Install (Plugin Method - Recommended)

### Step 1: Add the Marketplace

In Claude Code, run:
```
/plugin marketplace add cn-dataworks/powerbi-analyst-plugin
```

### Step 2: Install the Plugin

```
/plugin install powerbi-analyst@cn-dataworks-plugins
```

### Step 3: Verify Installation

```
/plugin list
```

You should see `powerbi-analyst` in the list.

---

## Alternative: Team Installation via settings.json

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": ["cn-dataworks/powerbi-analyst-plugin"]
}
```

When team members open the project, they'll be prompted to trust and install the plugin.

---

## Alternative: Manual Installation

If you prefer not to use the plugin system:

### Option A: Clone to User Skills Folder

```bash
# Clone the repo
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git

# Copy skill to your global Claude skills
# Windows (PowerShell):
Copy-Item -Recurse "powerbi-analyst-plugin\skills\powerbi-analyst" "$env:USERPROFILE\.claude\skills\powerbi-analyst"

# macOS/Linux:
cp -r powerbi-analyst-plugin/skills/powerbi-analyst ~/.claude/skills/powerbi-analyst
```

### Option B: Copy to Project

```bash
# Copy to your project's .claude folder
cp -r powerbi-analyst-plugin/skills/powerbi-analyst your-project/.claude/skills/
cp powerbi-analyst-plugin/commands/*.md your-project/.claude/commands/
cp powerbi-analyst-plugin/agents/*.md your-project/.claude/agents/
```

---

## Post-Installation Setup

### Run the Installer (Optional but Recommended)

The installer detects MCP availability and configures Claude:

```powershell
# Windows
.\.claude\skills\powerbi-analyst\install.ps1

# macOS/Linux
./.claude/skills/powerbi-analyst/install.sh
```

This will:
- Detect if Power BI Modeling MCP is installed
- Configure Claude's MCP settings (if MCP found)
- Initialize session state
- Report your configuration mode (Desktop vs File-Only)

---

## Requirements

### Required
- **Claude Code** 1.0+
- **Power BI Project** in PBIP format (`.pbip` file with `.SemanticModel/` and `.Report/` folders)

### Optional (Enhanced Features)
- **Power BI Desktop** - For live DAX validation and data sampling
- **Power BI Modeling MCP** - For full semantic model operations
- **GitHub CLI (`gh`)** - For template promotion workflow

---

## Verification

Test that the skill is working:

1. Open a folder with a Power BI project
2. Ask Claude: "What Power BI workflows can you help me with?"
3. Or try: "Analyze this Power BI project"

---

## What's Included

### Skill
- `powerbi-analyst` - Main skill with 7 workflows (Evaluate, Create, Implement, Analyze, Merge, Create Page, Harvest Templates)

### Commands (6)
- `/evaluate-pbi-project-file` - Diagnose issues
- `/create-pbi-artifact` - Create measures, columns, visuals
- `/create-pbi-page-specs` - Design dashboard pages
- `/implement-deploy-test-pbi-project-file` - Apply and deploy changes
- `/merge-powerbi-projects` - Compare and merge projects
- `/analyze-pbi-dashboard` - Document existing dashboards

### Agents (20)
Specialized agents for DAX, M Code, PBIR editing, validation, and more.

---

## Troubleshooting

### Plugin not found
Ensure you've added the marketplace first:
```
/plugin marketplace add cn-dataworks/powerbi-analyst-plugin
```

### Skill not activating
Check that your project has a `.pbip` file or `.SemanticModel/` folder.

### MCP not detected
The skill works without MCP (File-Only mode) but with reduced validation.
Install Power BI Modeling MCP from: https://github.com/microsoft/powerbi-modeling-mcp

### Need help?
- See `skills/powerbi-analyst/references/troubleshooting-faq.md`
- See `skills/powerbi-analyst/references/getting-started.md`

---

## Updating

### Plugin method
```
/plugin update powerbi-analyst@cn-dataworks-plugins
```

### Manual method
```bash
cd powerbi-analyst-plugin
git pull
# Re-copy files to destination
```
