# Power BI Analyst Update Information

This reference documents version management, update procedures, and tier detection for the Power BI Analyst plugin.

---

## Version Locations

| Component | Location | Purpose |
|-----------|----------|---------|
| Plugin manifest | `~/.claude/plugins/custom/powerbi-analyst/.claude-plugin/plugin.json` | Version, repository URL (Claude Code schema) |
| Plugin metadata | `~/.claude/plugins/custom/powerbi-analyst/.claude-plugin/plugin-meta.json` | Tier, releases URL (custom fields) |
| Plugin version | `~/.claude/plugins/custom/powerbi-analyst/tools/core/version.txt` | Numeric version only |
| Project version | `.claude/tools/powerbi-analyst/version.txt` | Version installed in project |

> **Note:** Claude Code's plugin.json only supports specific fields (name, version, description, author, repository). Custom fields like `tier` and `releases` are stored in `plugin-meta.json` to avoid validation errors.

---

## Tier Detection

The plugin has two tiers: **Core** (Free) and **Pro**.

**How tier is determined (file-based detection):**
1. Check if `skills/powerbi-analyst/pro-features.md` exists in the plugin folder
2. If exists → **Pro**; if missing → **Core**

> This file is excluded via `.gitignore` on the `main` branch, so Core installs won't have it.

**What differs by tier:**

| Feature | Core | Pro |
|---------|------|-----|
| Core workflows (EVALUATE, CREATE, IMPLEMENT, MERGE) | Yes | Yes |
| DAX/M-Code specialists | Yes | Yes |
| Design Standards | No | Yes |
| QA Loop (deploy/inspect/fix) | No | Yes |
| UX Dashboard Review | No | Yes |
| Template Harvesting | No | Yes |

---

## Update Source

| Resource | URL |
|----------|-----|
| Repository | https://github.com/cn-dataworks/powerbi-analyst-plugin |
| Releases | https://github.com/cn-dataworks/powerbi-analyst-plugin/releases |
| API (latest) | https://api.github.com/repos/cn-dataworks/powerbi-analyst-plugin/releases/latest |

**Branches:**
- `main` - Free version (stable)
- `pro` - Pro version (additional features)

---

## Checking Current Version

### Quick Check (PowerShell)

```powershell
# Read plugin version
$pluginJson = Get-Content "$HOME\.claude\plugins\custom\powerbi-analyst\.claude-plugin\plugin.json" | ConvertFrom-Json
Write-Host "Plugin Version: $($pluginJson.version)"

# Detect tier (file-based)
$proFeaturesPath = "$HOME\.claude\plugins\custom\powerbi-analyst\skills\powerbi-analyst\pro-features.md"
$tier = if (Test-Path $proFeaturesPath) { "Pro" } else { "Core" }
Write-Host "Edition: $tier"

# Read project version (if bootstrapped)
$projectVersion = Get-Content ".claude\tools\powerbi-analyst\version.txt" -ErrorAction SilentlyContinue
if ($projectVersion) {
    Write-Host "Project Version: $projectVersion"
} else {
    Write-Host "Project: Not bootstrapped"
}
```

### Quick Check (Bash)

```bash
# Read plugin version
cat ~/.claude/plugins/custom/powerbi-analyst/.claude-plugin/plugin.json | jq '.version'

# Detect tier (file-based)
if [ -f ~/.claude/plugins/custom/powerbi-analyst/skills/powerbi-analyst/pro-features.md ]; then
    echo "Edition: Pro"
else
    echo "Edition: Core"
fi

# Read project version
cat .claude/tools/powerbi-analyst/version.txt 2>/dev/null || echo "Not bootstrapped"
```

---

## Update Procedures

### Update Plugin (Global)

Pull the latest changes from the repository:

```powershell
# Windows
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git pull
```

```bash
# macOS/Linux
cd ~/.claude/plugins/custom/powerbi-analyst
git pull
```

### Update Project Tools (Per-Project)

After updating the plugin, re-run bootstrap in each project:

```powershell
# Windows (from your project directory)
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1"
```

```bash
# macOS/Linux (from your project directory)
bash ~/.claude/plugins/custom/powerbi-analyst/tools/bootstrap.sh
```

### Check If Update Needed

```powershell
# Returns exit code 1 if update available, 0 if current
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1" -CheckOnly
```

---

## Version Comparison Logic

The bootstrap script compares versions using semantic versioning:

1. Parse both versions as `major.minor.patch`
2. Compare each component numerically
3. Return status:
   - `missing` - Project not bootstrapped
   - `outdated` - Project version < Plugin version
   - `current` - Versions match
   - `newer` - Project version > Plugin version (manual edits?)

---

## Switching Tiers

### Free → Pro

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git checkout pro
git pull
```

Then re-bootstrap your projects.

### Pro → Free

```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git checkout main
git pull
```

Then re-bootstrap your projects. Note: Pro-specific files in your projects will remain but won't be used.

---

## Troubleshooting

### "Plugin not found"

Ensure the plugin is installed at the expected location:
```powershell
Test-Path "$HOME\.claude\plugins\custom\powerbi-analyst"
```

If not installed, clone the repository:
```powershell
git clone https://github.com/cn-dataworks/powerbi-analyst-plugin "$HOME\.claude\plugins\custom\powerbi-analyst"
```

### "Version mismatch after update"

Force re-bootstrap:
```powershell
& "$HOME\.claude\plugins\custom\powerbi-analyst\tools\bootstrap.ps1" -Force
```

### "Can't detect edition"

Edition is detected by checking if the Pro features file exists:
```powershell
Test-Path "$HOME\.claude\plugins\custom\powerbi-analyst\skills\powerbi-analyst\pro-features.md"
```

- Returns `True` → Pro edition
- Returns `False` → Core edition

If you expect Pro but see Core, ensure you're on the `pro` branch:
```powershell
cd "$HOME\.claude\plugins\custom\powerbi-analyst"
git branch
git checkout pro
git pull
```
