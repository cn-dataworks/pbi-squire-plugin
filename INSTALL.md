# Installing the Power BI Analyst Plugin

This plugin provides Power BI development assistance including DAX/M code generation, dashboard analysis, and PBIR visual editing.

---

## Quick Install (Recommended)

### Option A: One-Line PowerShell Install

```powershell
irm https://raw.githubusercontent.com/cn-dataworks/powerbi-analyst-plugin/main/install-plugin.ps1 | iex
```

### Option B: Download and Run Script

```powershell
# Download the script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cn-dataworks/powerbi-analyst-plugin/main/install-plugin.ps1" -OutFile "install-plugin.ps1"

# Run it
.\install-plugin.ps1
```

### Option C: Manual Steps

```powershell
# Step 1: Clone to the standard plugin location
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"

# Step 2: Register with Claude Code
claude -c "/plugin install $HOME\.claude\plugins\custom\powerbi-analyst"

# Step 3: Verify
claude -c "/plugin list"
```

---

## How the Plugin Works

### One Install, All Projects

When you run the installer, it:

1. **Clones the plugin** to a central location:
   ```
   C:\Users\YourName\.claude\plugins\custom\powerbi-analyst\
   ```

2. **Registers it globally** with Claude Code

After that, the plugin is available in **every project** you open:

```powershell
# Project A - plugin works
cd C:\Projects\SalesReport
claude

# Project B - same plugin works
cd C:\Projects\FinanceDashboard
claude
```

No per-project setup required. The plugin is stored **once** in your user profile, not copied into each project.

### Updating Applies Everywhere

When you update the plugin:

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull
```

All projects automatically use the updated version.

---

## Per-Project Control

You can control whether the plugin is active on a per-project basis.

### Disable in a Specific Project

Create `.claude/settings.json` in the project root:

```json
{
  "plugins": {
    "powerbi-analyst": {
      "enabled": false
    }
  }
}
```

### Enable Only in Specific Projects

If you prefer opt-in instead of opt-out:

1. **Skip the global registration** - just clone, don't run `/plugin install`:
   ```powershell
   git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"
   ```

2. **Add to specific projects** - in each project's `.claude/settings.json`:
   ```json
   {
     "plugins": {
       "powerbi-analyst": {
         "path": "C:\\Users\\YourName\\.claude\\plugins\\custom\\powerbi-analyst"
       }
     }
   }
   ```

### Example Project Structure

```
C:\Projects\
├── SalesReport\                    ← Power BI project
│   ├── .claude\
│   │   └── settings.json           ← (no override = plugin active)
│   └── SalesReport.pbip
│
├── WebApp\                         ← Non-Power BI project
│   ├── .claude\
│   │   └── settings.json           ← {"plugins": {"powerbi-analyst": {"enabled": false}}}
│   └── src\
│
└── FinanceDashboard\               ← Power BI project
    └── FinanceDashboard.pbip       ← (no .claude folder = plugin active globally)
```

### Auto-Activation Note

The plugin's skills only activate when they detect Power BI files (`.pbip`, `.SemanticModel/`). In non-Power BI projects, the skills won't trigger even if the plugin is installed globally. Explicitly disabling is mainly useful to avoid any overhead or potential skill conflicts.

---

## Why This Approach?

Claude Code runs Git in a non-interactive shell, which means credential helpers (like `gh auth setup-git`) don't work properly. The remote `/plugin marketplace add` command fails for private repositories because Git can't authenticate.

**The solution**: Clone the repository manually first (which uses your normal terminal's Git authentication), then point Claude to the local folder.

---

## Team Installation

For teams, you have two options:

### Option 1: Shared Setup Script

Have team members run the install script:

```powershell
# Each team member runs:
irm https://raw.githubusercontent.com/cn-dataworks/powerbi-analyst-plugin/main/install-plugin.ps1 | iex
```

### Option 2: Local Marketplace Registration

For more control, register the plugin as a local marketplace:

**Step 1**: Each team member clones the repo:
```powershell
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"
```

**Step 2**: Create/edit `~\.claude\plugins\known_marketplaces.json`:
```json
{
  "cn-dataworks-plugins": {
    "source": {
      "type": "directory",
      "path": "C:\\Users\\USERNAME\\.claude\\plugins\\custom\\powerbi-analyst"
    }
  }
}
```

**Step 3**: Install via marketplace reference:
```
/plugin install powerbi-analyst@cn-dataworks-plugins
```

### Option 3: Project-Level Configuration

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": {
    "powerbi-analyst": {
      "path": "C:\\Users\\USERNAME\\.claude\\plugins\\custom\\powerbi-analyst"
    }
  }
}
```

---

## Updating the Plugin

### Using the Install Script

Re-running the script will pull the latest changes:

```powershell
.\install-plugin.ps1
```

### Manual Update

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull
```

---

## Verification

Test that the plugin is working:

1. Open Claude Code in a folder with a Power BI project
2. Run: `/plugin list` - you should see `powerbi-analyst`
3. Ask: "What Power BI workflows can you help me with?"
4. Or try: `/evaluate-pbi-project-file`

---

## What's Included

### Skills (4)

| Skill | Purpose |
|-------|---------|
| `powerbi-analyst` | Main skill - 7 workflows for DAX, TMDL, PBIR editing |
| `power-bi-assistant` | Guides users to the right workflow |
| `powerbi-dashboard-analyzer` | Analyzes dashboards in business language |
| `powerbi-data-prep` | M code and Power Query transformations |

### Workflows (6)

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Diagnose project issues |
| `/create-pbi-artifact` | Create measures, columns, visuals |
| `/create-pbi-page-specs` | Design dashboard pages |
| `/implement-deploy-test-pbi-project-file` | Apply and deploy changes |
| `/merge-powerbi-projects` | Compare and merge projects |
| `/analyze-pbi-dashboard` | Document existing dashboards |

### Agents (20+)

Specialized agents for DAX, M Code, PBIR editing, validation, and more.

---

## Requirements

### Required
- **Claude Code** (latest version)
- **Git** (for cloning)
- **Power BI Project** in PBIP format (`.pbip` file with `.SemanticModel/` and `.Report/` folders)

### Optional (Enhanced Features)
- **Python 3.10+** - For utility scripts
- **Power BI Desktop** - For live DAX validation and testing
- **Power BI Modeling MCP** - For advanced semantic model operations
- **GitHub CLI (`gh`)** - For template promotion workflow

---

## Troubleshooting

### Git clone fails with authentication error

If you see `terminal prompts disabled`:
```powershell
# Authenticate with GitHub CLI first
gh auth login

# Then try the install again
.\install-plugin.ps1
```

### Plugin not showing in /plugin list

Make sure you ran the install command:
```powershell
claude -c "/plugin install $HOME\.claude\plugins\custom\powerbi-analyst"
```

### Skills not activating

Check that your project has a `.pbip` file or `.SemanticModel/` folder. The skill activates based on these triggers.

### MCP not detected

The skill works without MCP (File-Only mode) but with reduced validation. For full features, install Power BI Modeling MCP from: https://github.com/microsoft/powerbi-modeling-mcp

### Need more help?

- See `skills/powerbi-analyst/references/troubleshooting-faq.md`
- See `skills/powerbi-analyst/references/getting-started.md`
- [Open an issue](https://github.com/cn-dataworks/powerbi-analyst-plugin/issues)

---

## Uninstalling

```powershell
# Remove the plugin registration
claude -c "/plugin uninstall powerbi-analyst"

# Delete the files
Remove-Item -Recurse -Force "$HOME\.claude\plugins\custom\powerbi-analyst"
```
