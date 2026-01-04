# Installing the Power BI Analyst Plugin

This plugin provides Power BI development assistance including DAX/M code generation, dashboard analysis, and PBIR visual editing.

---

## Quick Install

### Step 1: Clone the Repository

```powershell
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"
```

### Step 2: Register as Marketplace

Claude Code requires registering local plugins as a marketplace first. You must run this from your home directory:

```powershell
cd $HOME
claude
```

Inside Claude Code, run these commands:

```
/plugin marketplace add ./.claude/plugins/custom/powerbi-analyst
/plugin install powerbi-analyst
```

Choose **"Install for you"** when prompted (installs globally for all projects).

### Step 3: Restart and Verify

Exit Claude Code and restart:

```
/exit
```

```powershell
claude
```

Then verify:

```
/plugin list
```

You should see `powerbi-analyst` under **cn-dataworks-plugins**.

---

## First Project Setup (Bootstrap)

After installing the plugin, run bootstrap in each Power BI project to copy the tools:

```powershell
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

See [Project Bootstrap](#project-bootstrap-first-run) section below for details.

---

## MCP Detection (Recommended for Writing)

**Power BI Modeling MCP is strongly recommended** if you plan to create or edit DAX measures, M queries, or other model artifacts.

| Mode | Reading/Analyzing | Writing/Editing |
|------|-------------------|-----------------|
| File-Only | ✅ Works well | ⚠️ No validation - errors found when opening in PBI Desktop |
| With MCP | ✅ Works well | ✅ Validates code compiles before writing |

### Installing Power BI Modeling MCP

**Option A: VS Code Extension (Recommended)**

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Power BI Modeling MCP"
4. Install the extension by **Analysis Services**
5. Re-run the plugin installer to detect it:
   ```powershell
   cd "$HOME\.claude\plugins\custom\powerbi-analyst"
   .\install-plugin.ps1
   ```

**Option B: Manual Install**

See: https://github.com/microsoft/powerbi-modeling-mcp

Then re-run the installer to detect it.

### Verifying MCP Detection

The installer automatically checks for MCP and configures the plugin accordingly.

### What Happens During Install

```
>> Checking for Power BI Modeling MCP...
   [OK] Found: C:\path\to\powerbi-modeling-mcp.exe

   Mode: Desktop Mode (full validation)

   Capabilities:
       [OK] DAX/M code generation
       [OK] TMDL file editing
       [OK] PBIR visual creation
       [OK] Live DAX validation
       [OK] Real-time error checking
```

Or if MCP is not installed:

```
>> Checking for Power BI Modeling MCP...
   [!] MCP not found
       The plugin will work in File-Only mode

   Mode: File-Only Mode (limited validation)

   Capabilities:
       [OK] DAX/M code generation
       [OK] TMDL file editing
       [OK] PBIR visual creation
       [--] Live DAX validation (requires MCP)
       [--] Real-time error checking (requires MCP)

   To enable full features:
       1. Install MCP: https://github.com/microsoft/powerbi-modeling-mcp
       2. Re-run the installer from the plugin folder:
          cd $HOME\.claude\plugins\custom\powerbi-analyst
          .\install-plugin.ps1
```

### File-Only Mode vs Desktop Mode

| Feature | File-Only Mode | Desktop Mode |
|---------|----------------|--------------|
| DAX/M code generation | ✅ | ✅ |
| TMDL file editing | ✅ | ✅ |
| PBIR visual creation | ✅ | ✅ |
| Live DAX validation | ❌ | ✅ |
| Real-time error checking | ❌ | ✅ |
| Requires Power BI Desktop open | No | Yes |

### Enabling MCP After Initial Install

If you install Power BI Modeling MCP after the initial plugin installation:

```powershell
# Navigate to plugin folder and re-run installer
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
.\install-plugin.ps1
```

The installer will:
1. Detect the newly installed MCP binary
2. Update Claude's configuration to use it
3. Show "Desktop Mode" in the capability summary

### Skipping MCP Configuration

If you want to skip MCP auto-configuration:

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
.\install-plugin.ps1 -SkipMcpConfig
```

---

## Project Bootstrap (First Run)

When you first use the plugin in a Power BI project, it needs to copy Python tools and helper files to your project directory. This is called "bootstrapping."

### Automatic Bootstrap

Run the bootstrap script from your project directory:

```powershell
# Windows (from your Power BI project folder)
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

```bash
# macOS/Linux
bash "$HOME/.claude/plugins/custom/powerbi-analyst/tools/bootstrap.sh"
```

### What Gets Created

```
YourProject/
├── CLAUDE.md                ← Project instructions for Claude
├── .claude/
│   ├── state.json           ← Session state (tasks, locks)
│   ├── tasks/               ← Task findings files
│   ├── tools/               ← Python utilities
│   │   ├── token_analyzer.py
│   │   ├── tmdl_format_validator.py
│   │   ├── analytics_merger.py
│   │   ├── version.txt      ← Version tracking
│   │   └── ...
│   ├── helpers/             ← Reference files
│   │   └── pbi-url-filter-encoder.md
│   └── settings.json        ← Auto-approve permissions
└── YourProject.pbip
```

### CLAUDE.md (Project Instructions)

Bootstrap creates or updates a `CLAUDE.md` file in your project root. This file tells Claude Code to use the Power BI Analyst skill when working with Power BI files.

**What gets added:**

```markdown
# CLAUDE.md

This project uses the **Power BI Analyst Plugin**.

## When to Use

Invoke the `powerbi-analyst` skill when working with:
- Power BI files (*.pbip, *.pbix)
- TMDL files (semantic model definitions)
- PBIR files (report visuals)
- DAX measures and M code

## Available Commands

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose issues |
| `/create-pbi-artifact` | Create measures, columns, tables |
| `/implement-deploy-test-pbi-project-file` | Deploy and test changes |
| `/setup-data-anonymization` | Set up data masking for sensitive data |

## Power BI Project Path

Power BI projects are located at: `C:/Projects/YourProject`

## File Permissions

Allowed paths for Read/Edit/Write:
- `C:/Projects/YourProject/**`
```

**Behavior:**
- If `CLAUDE.md` doesn't exist → creates it with the plugin reference
- If `CLAUDE.md` exists but doesn't reference the plugin → appends the plugin section
- If `CLAUDE.md` already references the plugin → leaves it unchanged

**Why this matters:** Claude reads `CLAUDE.md` at the start of every session to understand project-specific instructions. Without this reference, Claude won't know to invoke the Power BI skill automatically.

### Auto-Approve Permissions

Bootstrap creates a `settings.json` that auto-approves common tools so you don't get prompted for every file read:

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
      "Bash(git *)",
      "Bash(npm *)",
      "Bash(npx *)"
    ]
  }
}
```

**What this means:**
- `Read`, `Glob`, `Grep` - File reading/searching runs without prompts
- `Edit`, `Write` - File modifications run without prompts
- `Bash(python *)` - Python scripts run without prompts
- `Bash(git *)` - Git commands run without prompts

**Customizing permissions:**

If you want stricter or looser permissions, edit `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep"
    ]
  }
}
```

Or allow everything (use with caution):
```json
{
  "permissions": {
    "allow": ["*"]
  }
}
```

**Note:** Bootstrap won't overwrite an existing `settings.json`. To get the default permissions on an existing project, copy from `tools/templates/settings.json`.

### Version Tracking

The bootstrap script tracks versions so you know when updates are available:

```powershell
# Check if update needed (exit code 1 = update available)
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1" -CheckOnly

# Force reinstall even if current
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1" -Force
```

### When to Re-run Bootstrap

Re-run bootstrap after:
- Updating the plugin (`git pull`)
- Wanting to reset local tool modifications
- Starting a new Power BI project

### Git Considerations

You can choose to:
- **Commit `.claude/`** - Tools are versioned with your project (self-contained)
- **Gitignore `.claude/`** - Tools are fetched fresh on each clone

Add to `.gitignore` if you prefer fresh tools:
```
.claude/
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

### Option 1: Standard Install (Recommended)

Each team member runs the same install steps:

```powershell
# Step 1: Clone
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"

# Step 2: Register (from home directory)
cd $HOME
claude
```

Inside Claude Code:
```
/plugin marketplace add ./.claude/plugins/custom/powerbi-analyst
/plugin install powerbi-analyst
```

### Option 2: Project-Level Configuration

For project-specific installation, add to your project's `.claude/settings.json`:

```json
{
  "plugins": {
    "powerbi-analyst": {
      "path": "C:\\Users\\USERNAME\\.claude\\plugins\\custom\\powerbi-analyst"
    }
  }
}
```

Each team member still needs to clone the repo first.

---

## Updating the Plugin

### Pull Latest Changes

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull
```

### Update Project Tools

After pulling, re-run bootstrap in your projects to get updated tools:

```powershell
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

### Re-detect MCP (if newly installed)

If you installed MCP after the initial setup:

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
.\install-plugin.ps1
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

# Then try cloning again
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin.git "$HOME\.claude\plugins\custom\powerbi-analyst"
```

### Plugin not showing in /plugin list

Make sure you registered the marketplace and installed the plugin:

```powershell
cd $HOME
claude
```

Inside Claude Code:
```
/plugin marketplace add ./.claude/plugins/custom/powerbi-analyst
/plugin install powerbi-analyst
```

### Skills not activating

Check that your project has a `.pbip` file or `.SemanticModel/` folder. The skill activates based on these triggers.

### MCP not detected

The plugin works without MCP (File-Only mode) but with reduced validation.

To enable full features:
1. Install Power BI Modeling MCP from: https://github.com/microsoft/powerbi-modeling-mcp
2. Re-run bootstrap in your project:
   ```powershell
   & "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
   ```

### Need more help?

- See `skills/powerbi-analyst/references/troubleshooting-faq.md`
- See `skills/powerbi-analyst/references/getting-started.md`
- [Open an issue](https://github.com/cn-dataworks/powerbi-analyst-plugin/issues)

---

## Uninstalling

Inside Claude Code:
```
/plugin uninstall powerbi-analyst
```

Then delete the files:
```powershell
Remove-Item -Recurse -Force "$HOME\.claude\plugins\custom\powerbi-analyst"
```
