# Installing the PBI Squire Plugin

This plugin provides Power BI development assistance including DAX/M code generation, dashboard analysis, and PBIR visual editing.

---

## Quick Install

### Option A: Direct Install (Recommended)

Run these commands inside Claude Code:

```
/plugin marketplace add https://github.com/cn-dataworks/pbi-squire-plugin
/plugin install pbi-squire
```

That's it! The plugin is now available in all your projects.

### Option B: Git Clone (For Contributors)

If you plan to contribute, need offline access, or want more control:

```powershell
# 1. Clone the repository
git clone https://github.com/cn-dataworks/pbi-squire-plugin.git "$HOME\.claude\plugins\custom\pbi-squire"

# 2. Run installer (registers as local marketplace + detects MCP)
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1
```

Choose **"Install for you"** when prompted (installs globally for all projects).

### Verify

Open Claude Code and verify the installation:

```powershell
claude
```

```
/plugin list
```

You should see `pbi-squire` under **cn-dataworks-plugins**.

---

## What's Next After Installation?

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  YOU'RE READY TO GO!                                                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

The plugin is now installed globally. Just navigate to any Power BI project
and start using the skill - it will auto-configure on first use!

ANALYST EDITION: No bootstrap required. The skill sets up automatically.

DEVELOPER EDITION: Bootstrap is optional but recommended for Python tools.
Without it, the skill uses Claude-native fallback (same features, slightly slower).
```

### Quick Start (No Bootstrap Needed)

```powershell
# 1. Navigate to your Power BI project folder
cd "C:\path\to\your\powerbi-project"

# 2. Open Claude Code
claude

# 3. Just ask for help - first-time setup happens automatically!
# "Help me fix the YoY growth measure"
```

**What happens on first use:**
1. PBI Squire detects your Power BI projects
2. Asks if this is a shared repository (if multiple projects found)
3. Asks about data sensitivity settings
4. Creates configuration files inline
5. Proceeds with your request

### Quick Start Checklist

After global installation:

- [ ] **Navigate to your Power BI project folder**
- [ ] **Verify your project is in PBIP format** (not .pbix)
  - If you have a .pbix file, convert it first:
    1. Open in Power BI Desktop
    2. File → Save As → Power BI Project (.pbip)
- [ ] **Open Claude Code** in your project folder
- [ ] **Try a command**: `/evaluate-pbi-project-file` or just describe your need
- [ ] **(Developer Edition only)** Optionally run bootstrap for Python tools

### Optional Bootstrap

Bootstrap is **optional** for Analyst Edition but provides benefits:

| Use Case | Run Bootstrap? |
|----------|----------------|
| Analyst Edition - normal use | No (auto-configures) |
| Developer Edition - want Python tools | Yes (recommended) |
| CI/CD automation | Yes (explicit setup) |
| Force refresh configuration | Yes (with `-Force` flag) |

```powershell
# Optional: Run bootstrap for explicit control
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
```

### Common First-Time Issues

| Issue | Solution |
|-------|----------|
| "Limited analysis mode" | Convert your .pbix to .pbip format |
| "MCP not detected" | Install Power BI Modeling MCP for live validation |
| "Python tools not found" | Developer only - run bootstrap or use Claude-native fallback |

---

## First Project Setup (Automatic or Bootstrap)

### Automatic Setup (Recommended)

For **Analyst Edition**, setup happens automatically on first skill invocation. Just:

1. Navigate to your Power BI project folder
2. Open Claude Code
3. Ask for help with Power BI

The skill will detect your projects and configure itself inline.

### Manual Bootstrap (Optional)

For **Developer Edition** or explicit control, run bootstrap:

```powershell
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
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
   cd "$HOME\.claude\plugins\custom\pbi-squire"
   .\install-plugin.ps1
   ```

**Option B: Manual Install**

1. Go to: https://github.com/microsoft/powerbi-modeling-mcp
2. Follow the installation instructions in the README
3. Ensure the `powerbi-modeling-mcp.exe` is in your PATH or one of these locations:
   - VS Code extensions folder
   - `%ProgramFiles%\PowerBI Modeling MCP\`
   - `%LOCALAPPDATA%\Programs\PowerBI Modeling MCP\`
4. Re-run the plugin installer to detect it

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
          cd $HOME\.claude\plugins\custom\pbi-squire
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
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1
```

The installer will:
1. Detect the newly installed MCP binary
2. Update Claude's configuration to use it
3. Show "Desktop Mode" in the capability summary

### Skipping MCP Configuration

If you want to skip MCP auto-configuration:

```powershell
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1 -SkipMcpConfig
```

---

## Project Bootstrap (First Run)

### Automatic Setup (Analyst Edition)

For **Analyst Edition**, no separate bootstrap is needed. The skill auto-configures when you first invoke it:

```
You: "Help me with this Power BI measure"

PBI Squire: "I need to configure PBI Squire for this location.
             Found 2 Power BI projects. Configure as shared repository? [Y/N]
             Does this project contain sensitive data? [Y/N]
             ✅ Configured! Now let me help..."
```

### Manual Bootstrap (Optional)

Run the bootstrap script for explicit control or to install Developer Edition Python tools:

**Analyst Edition:** Creates configuration files only (no Python)
**Developer Edition:** Creates configuration files + copies Python analysis tools

```powershell
# Windows (from your Power BI project folder)
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
```

```bash
# macOS/Linux
bash "$HOME/.claude/plugins/custom/pbi-squire/tools/bootstrap.sh"
```

### What Gets Created

**Analyst Edition:**
```
YourProject/
├── CLAUDE.md                        ← Project instructions for Claude
├── .claude/
│   ├── pbi-squire.json         ← Skill configuration
│   ├── settings.json                ← Auto-approve permissions
│   ├── tasks/                       ← Task findings files
│   ├── tools/
│   │   └── pbi-squire/
│   │       └── version.txt          ← Version tracking only
│   └── helpers/
│       └── pbi-squire/
│           └── pbi-url-filter-encoder.md
└── YourProject.pbip
```

**Developer Edition (additional):**
```
YourProject/
├── .claude/
│   ├── tools/
│   │   └── pbi-squire/         ← Plugin tools (Pro only)
│   │       ├── token_analyzer.py
│   │       ├── tmdl_format_validator.py
│   │       ├── version.txt
│   │       └── ... (13 Python scripts)
│   └── powerbi-design-standards.md  ← Design standards template (Pro only)
└── ...
```

### CLAUDE.md (Project Instructions)

Bootstrap creates or updates a `CLAUDE.md` file in your project root. This file tells Claude Code to use the PBI Squire skill when working with Power BI files.

**What gets added:**

```markdown
# CLAUDE.md

This project uses the **PBI Squire Plugin**.

## When to Use

Invoke the `pbi-squire` skill when working with:
- Power BI files (*.pbip, *.pbix)
- TMDL files (semantic model definitions)
- PBIR files (report visuals)
- DAX measures and M code

## Available Commands

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose issues |
| `/create-pbi-artifact-spec` | Create measures, columns, tables |
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
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1" -CheckOnly

# Force reinstall even if current
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1" -Force
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
   C:\Users\YourName\.claude\plugins\custom\pbi-squire\
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
cd "$HOME\.claude\plugins\custom\pbi-squire"
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
    "pbi-squire": {
      "enabled": false
    }
  }
}
```

### Enable Only in Specific Projects

If you prefer opt-in instead of opt-out:

1. **Skip the global registration** - just clone, don't run `/plugin install`:
   ```powershell
   git clone https://github.com/cn-dataworks/pbi-squire-plugin.git "$HOME\.claude\plugins\custom\pbi-squire"
   ```

2. **Add to specific projects** - in each project's `.claude/settings.json`:
   ```json
   {
     "plugins": {
       "pbi-squire": {
         "path": "C:\\Users\\YourName\\.claude\\plugins\\custom\\pbi-squire"
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
│   │   └── settings.json           ← {"plugins": {"pbi-squire": {"enabled": false}}}
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

### Option 1: Direct Install (Recommended)

Each team member runs inside Claude Code:

```
/plugin marketplace add https://github.com/cn-dataworks/pbi-squire-plugin
/plugin install pbi-squire
```

### Option 2: Git Clone (For Contributors)

If team members need to contribute or need offline access:

```powershell
git clone https://github.com/cn-dataworks/pbi-squire-plugin.git "$HOME\.claude\plugins\custom\pbi-squire"
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1
```

### Option 3: Project-Level Configuration

For project-specific installation, add to your project's `.claude/settings.json`:

```json
{
  "plugins": {
    "pbi-squire": {
      "path": "C:\\Users\\USERNAME\\.claude\\plugins\\custom\\pbi-squire"
    }
  }
}
```

Each team member still needs to clone the repo first.

---

## Updating the Plugin

### If You Used Option A (Direct Install)

Inside Claude Code:
```
/plugin update pbi-squire
```

### If You Used Option B (Git Clone)

```powershell
cd "$HOME\.claude\plugins\custom\pbi-squire"
git pull; if ($?) { claude -c "/plugin update pbi-squire" }
```

### Update Project Tools

After updating, re-run bootstrap in your projects to get updated tools:

```powershell
cd "C:\path\to\your\powerbi-project"
& "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
```

### Re-detect MCP (if newly installed)

If you installed MCP after the initial setup:

```powershell
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1
```

---

## Verification

Test that the plugin is working:

1. **Navigate to a Power BI project folder** (containing .pbip file)
2. **Open Claude Code** in that folder:
   ```powershell
   claude
   ```
3. **Verify plugin is listed**: `/plugin list` - you should see `pbi-squire`
4. **Test the skill**: Ask "What Power BI workflows can you help me with?"
5. **Or try a command**: `/evaluate-pbi-project-file`

The skill will auto-configure on first use if needed.

### Expected Behavior

When working correctly, you should see:
- Plugin listed under `cn-dataworks-plugins` in `/plugin list`
- First-time setup prompts (if not previously configured)
- Clear prompts when invoking workflows
- Format detection warnings if using .pbix instead of .pbip

### If Skills Don't Activate

Check that Power BI files are present:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  CHECK: Does this folder contain Power BI files?                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

Look for:
  ✓ *.pbip file
  ✓ *.SemanticModel/ folder
  ✓ *.Report/ folder

If you've already used the skill, also check:
  ✓ .claude/pbi-squire.json (auto-created)
  ✓ CLAUDE.md (with plugin reference)
```

---

## What's Included

### Skills (4)

| Skill | Purpose |
|-------|---------|
| `pbi-squire` | Main skill - 7 workflows for DAX, TMDL, PBIR editing |
| `power-bi-assistant` | Guides users to the right workflow |
| `powerbi-dashboard-analyzer` | Analyzes dashboards in business language |
| `powerbi-data-prep` | M code and Power Query transformations |

### Workflows (6)

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Diagnose project issues |
| `/create-pbi-artifact-spec` | Create measures, columns, visuals |
| `/create-pbi-page-specs` | Design dashboard pages |
| `/implement-deploy-test-pbi-project-file` | Apply and deploy changes |
| `/merge-powerbi-projects` | Compare and merge projects |
| `/summarize-pbi-dashboard` | Document existing dashboards |

### Agents (20+)

Specialized agents for DAX, M Code, PBIR editing, validation, and more.

---

## Requirements

### Analyst Edition (Default) - Simple Install
- **Claude Code** (latest version)
- **Power BI Project** in PBIP format (`.pbip` file with `.SemanticModel/` and `.Report/` folders)
- **Power BI Desktop** - For testing and (with MCP) live validation
- **Recommended: Power BI Modeling MCP** - For DAX validation before writing

> **Note:** Analyst Edition does NOT require Python. It uses MCP + Claude-native validation.

### Developer Edition (Additional Requirements)
- **Python 3.10+** - Required for advanced analysis tools
- **Git** (for cloning the Pro repository)
- **Power BI Service access** - For deployment features

### Determining Your Edition

| Feature | Core (Free) | Pro |
|---------|-------------|-----|
| Plugin install | `/plugin install` | Git clone |
| Python required | No | Yes (3.10+) |
| MCP validation | Yes | Yes + Python tools |
| TMDL editing | Yes | Yes |
| PBIR editing | Yes | Yes |
| Advanced analytics | - | Yes |
| Design standards | - | Yes |
| QA Loop | - | Yes |

---

## Troubleshooting

### Git clone fails with authentication error

If you see `terminal prompts disabled`:
```powershell
# Authenticate with GitHub CLI first
gh auth login

# Then try cloning again
git clone https://github.com/cn-dataworks/pbi-squire-plugin.git "$HOME\.claude\plugins\custom\pbi-squire"
```

### Plugin not showing in /plugin list

Make sure you ran the installer script:

```powershell
cd "$HOME\.claude\plugins\custom\pbi-squire"
.\install-plugin.ps1
```

Or manually register inside Claude Code:
```
/plugin marketplace add ~/.claude/plugins/custom/pbi-squire
/plugin install pbi-squire
```

### Skills not activating

**Most likely cause: No Power BI files found**

The skill activates when it detects Power BI files. Check:
- Project has a `.pbip` file or `.SemanticModel/` folder
- You're in the correct directory

**If auto-setup didn't run:**

The skill should auto-configure on first use. If it didn't:
1. Try invoking the skill directly: `/evaluate-pbi-project-file`
2. Or run bootstrap manually:
   ```powershell
   cd "C:\path\to\your\project"
   & "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
   ```

**Also check:**
- `CLAUDE.md` exists and references the PBI Squire plugin
- `.claude/pbi-squire.json` exists in your project (created by auto-setup or bootstrap)

### MCP not detected

The plugin works without MCP (File-Only mode) but with reduced validation.

To enable full features:
1. Install Power BI Modeling MCP from: https://github.com/microsoft/powerbi-modeling-mcp
2. Re-run bootstrap in your project:
   ```powershell
   & "$HOME\.claude\plugins\custom\pbi-squire\tools\bootstrap.ps1"
   ```

### Need more help?

- See `skills/pbi-squire/references/troubleshooting-faq.md`
- See `skills/pbi-squire/references/getting-started.md`
- [Open an issue](https://github.com/cn-dataworks/pbi-squire-plugin/issues)

---

## Uninstalling

Inside Claude Code:
```
/plugin uninstall pbi-squire
```

Then delete the files:
```powershell
Remove-Item -Recurse -Force "$HOME\.claude\plugins\custom\pbi-squire"
```
