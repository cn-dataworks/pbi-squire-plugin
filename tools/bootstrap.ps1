#Requires -Version 5.1
<#
.SYNOPSIS
    OPTIONAL bootstrap script for PBI Squire Plugin - configures project for the plugin.

.DESCRIPTION
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  THIS SCRIPT IS OPTIONAL                                                   ║
    ╠═══════════════════════════════════════════════════════════════════════════╣
    ║                                                                           ║
    ║  ANALYST EDITION: This script is NOT REQUIRED. The skill will auto-       ║
    ║  configure on first invocation. Use bootstrap only for:                   ║
    ║  - Explicit control over setup                                            ║
    ║  - CI/CD automation                                                       ║
    ║  - Force refresh of configuration                                         ║
    ║                                                                           ║
    ║  DEVELOPER EDITION: Run bootstrap to install Python analysis tools for   ║
    ║  faster performance. Without bootstrap, skill uses Claude-native          ║
    ║  fallback (same functionality, slightly slower).                          ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝

    This script configures your project for the PBI Squire plugin.

    **For ANALYST edition:**
    - Creates .claude/pbi-squire.json (skill configuration)
    - Creates .claude/settings.json (permissions)
    - Creates/updates CLAUDE.md (project instructions)
    - Copies helper files
    - NO Python tools required (uses MCP + Claude-native validation)

    **For DEVELOPER edition (additional):**
    - Copies Python analysis tools to .claude/tools/pbi-squire/
    - Enables advanced features like TMDL validation, analytics

    NOTE: Agents and skills are registered globally when you install the plugin.
    This script only handles per-project configuration and (for Developer) Python tools.

    What this script does:
    - Creates skill configuration files
    - Creates settings.json with recommended permissions
    - Optionally configures Power BI project path for auto-approve
    - [Developer only] Copies Python analysis tools

    What this script does NOT do:
    - Register agents (they're globally available from the plugin)
    - Install skills (they're globally available from the plugin)

.PARAMETER Force
    Force update even if versions match.

.PARAMETER Silent
    Suppress output messages.

.PARAMETER CheckOnly
    Only check if update is needed, don't copy files.

.PARAMETER PBIProjectPath
    Path to your Power BI project folder(s). This path will be added to the
    auto-approve permissions in settings.json so the analyst can read/edit
    your TMDL files without prompting.

.EXAMPLE
    .\bootstrap.ps1
    .\bootstrap.ps1 -Force
    .\bootstrap.ps1 -CheckOnly
    .\bootstrap.ps1 -PBIProjectPath "C:\Projects\MyPowerBI"
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Silent,
    [switch]$CheckOnly,
    [string]$PBIProjectPath
)

$ErrorActionPreference = "Stop"

# ============================================================
# CONFIGURATION
# ============================================================

# Determine plugin path (this script is in {plugin}/tools/)
$script:PluginPath = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not (Test-Path "$script:PluginPath\.claude-plugin")) {
    # Fallback: script might be in {plugin}/tools/ directly
    $script:PluginPath = Split-Path $PSScriptRoot -Parent
}

$script:PluginToolsPath = Join-Path $script:PluginPath "tools"
$script:DeveloperToolsPath = Join-Path $script:PluginToolsPath "developer"
$script:PluginResourcesPath = Join-Path $script:PluginPath "skills\pbi-squire\resources"
$script:VersionFile = "version.txt"

# Local paths (in user's project)
$script:LocalClaudeDir = ".claude"
$script:LocalToolsDir = ".claude\tools\pbi-squire"
$script:LocalHelpersDir = ".claude\helpers\pbi-squire"

# Core files to copy (PUBLIC - always installed, no Python)
# Note: Analyst Edition uses MCP + Claude-native validation, no Python required
$script:CoreToolFiles = @(
    "version.txt"
)

# Python tools (DEVELOPER only - require Python 3.10+)
# These provide advanced analysis capabilities beyond MCP
$script:PythonToolFiles = @(
    "token_analyzer.py",
    "analytics_merger.py",
    "tmdl_format_validator.py",
    "tmdl_measure_replacer.py",
    "pbir_visual_editor.py",
    "pbi_project_validator.py",
    "pbi_merger_utils.py",
    "pbi_merger_schemas.json",
    "extract_visual_layout.py",
    "agent_logger.py",
    "sensitive_column_detector.py",
    "anonymization_generator.py",
    "m_partition_editor.py",
    "m_pattern_analyzer.py",
    "query_folding_validator.py"
)

# Advanced files to copy (PRIVATE - only in Developer edition)
$script:AdvancedToolFiles = @(
    # Playwright testing, template harvesting scripts go here
)

# Developer template files (copied to .claude/ root for user customization)
$script:DeveloperTemplateFiles = @(
    "powerbi-design-standards.md"
)

$script:HelperFiles = @(
    "pbi-url-filter-encoder.md"
)

$script:TemplatesPath = Join-Path $script:PluginToolsPath "templates"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Write-Info {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "  [bootstrap] $Message" -ForegroundColor Cyan
    }
}

function Write-Success {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "  [bootstrap] $Message" -ForegroundColor Green
    }
}

function Write-Warn {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "  [bootstrap] $Message" -ForegroundColor Yellow
    }
}

# ============================================================
# VERSION FUNCTIONS
# ============================================================

function Get-PluginVersion {
    $versionPath = Join-Path $script:DeveloperToolsPath $script:VersionFile
    if (Test-Path $versionPath) {
        return (Get-Content $versionPath -Raw).Trim()
    }
    return "0.0.0"
}

function Get-LocalVersion {
    $versionPath = Join-Path $script:LocalToolsDir $script:VersionFile
    if (Test-Path $versionPath) {
        return (Get-Content $versionPath -Raw).Trim()
    }
    return $null
}

function Compare-Versions {
    param(
        [string]$PluginVersion,
        [string]$LocalVersion
    )

    if ($null -eq $LocalVersion) {
        return "missing"
    }

    $pluginParts = $PluginVersion.Split('.') | ForEach-Object { [int]$_ }
    $localParts = $LocalVersion.Split('.') | ForEach-Object { [int]$_ }

    for ($i = 0; $i -lt 3; $i++) {
        $p = if ($i -lt $pluginParts.Count) { $pluginParts[$i] } else { 0 }
        $l = if ($i -lt $localParts.Count) { $localParts[$i] } else { 0 }

        if ($p -gt $l) { return "outdated" }
        if ($p -lt $l) { return "newer" }
    }

    return "current"
}

# ============================================================
# COPY FUNCTIONS
# ============================================================

function Initialize-LocalDirectories {
    # Create .claude directory structure
    if (-not (Test-Path $script:LocalClaudeDir)) {
        New-Item -ItemType Directory -Path $script:LocalClaudeDir -Force | Out-Null
        Write-Info "Created $script:LocalClaudeDir directory"
    }

    # Create parent tools/helpers directories first
    $toolsParent = ".claude\tools"
    $helpersParent = ".claude\helpers"

    if (-not (Test-Path $toolsParent)) {
        New-Item -ItemType Directory -Path $toolsParent -Force | Out-Null
    }

    if (-not (Test-Path $helpersParent)) {
        New-Item -ItemType Directory -Path $helpersParent -Force | Out-Null
    }

    # Create plugin-specific subdirectories
    if (-not (Test-Path $script:LocalToolsDir)) {
        New-Item -ItemType Directory -Path $script:LocalToolsDir -Force | Out-Null
        Write-Info "Created $script:LocalToolsDir directory"
    }

    if (-not (Test-Path $script:LocalHelpersDir)) {
        New-Item -ItemType Directory -Path $script:LocalHelpersDir -Force | Out-Null
        Write-Info "Created $script:LocalHelpersDir directory"
    }

    # Create tasks directory for workflow outputs
    $tasksDir = Join-Path $script:LocalClaudeDir "tasks"
    if (-not (Test-Path $tasksDir)) {
        New-Item -ItemType Directory -Path $tasksDir -Force | Out-Null
        Write-Info "Created $tasksDir directory"
    }
}

function Copy-ToolFiles {
    param([bool]$IsDeveloper)

    $copied = 0
    $skipped = 0

    # Copy core files (always present - version tracking only for Analyst)
    foreach ($file in $script:CoreToolFiles) {
        $sourcePath = Join-Path $script:DeveloperToolsPath $file
        $destPath = Join-Path $script:LocalToolsDir $file

        if (Test-Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            $copied++
        } else {
            Write-Warn "Core tool not found: $file"
            $skipped++
        }
    }

    Write-Info "Copied $copied core files"

    # Copy Python tools (Developer edition only)
    if ($IsDeveloper) {
        $pythonCopied = 0
        foreach ($file in $script:PythonToolFiles) {
            $sourcePath = Join-Path $script:DeveloperToolsPath $file
            $destPath = Join-Path $script:LocalToolsDir $file

            if (Test-Path $sourcePath) {
                Copy-Item -Path $sourcePath -Destination $destPath -Force
                $pythonCopied++
            } else {
                Write-Warn "Python tool not found: $file"
            }
        }
        if ($pythonCopied -gt 0) {
            Write-Success "Copied $pythonCopied Python analysis tools (Developer)"
        }
    } else {
        Write-Info "Analyst Edition: Python tools not required"
        Write-Info "  (Uses MCP + Claude-native validation)"
    }

    # Copy advanced files if present (Developer edition only)
    if ($IsDeveloper -and $script:AdvancedToolFiles.Count -gt 0) {
        $advCopied = 0
        foreach ($file in $script:AdvancedToolFiles) {
            $sourcePath = Join-Path $script:DeveloperToolsPath $file
            $destPath = Join-Path $script:LocalToolsDir $file

            if (Test-Path $sourcePath) {
                Copy-Item -Path $sourcePath -Destination $destPath -Force
                $advCopied++
            }
        }
        if ($advCopied -gt 0) {
            Write-Success "Copied $advCopied advanced Developer features"
        }
    }
}

function Copy-HelperFiles {
    $copied = 0

    foreach ($file in $script:HelperFiles) {
        $sourcePath = Join-Path $script:PluginResourcesPath $file
        $destPath = Join-Path $script:LocalHelpersDir $file

        if (Test-Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            $copied++
        } else {
            Write-Warn "Helper file not found: $file"
        }
    }

    Write-Info "Copied $copied helper files"
}

function Copy-DocsFiles {
    # Copy documentation that might be useful locally
    $docsSource = Join-Path $script:PluginToolsPath "docs"
    $docsDir = Join-Path $script:LocalToolsDir "docs"

    if (Test-Path $docsSource) {
        if (-not (Test-Path $docsDir)) {
            New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
        }
        Copy-Item -Path "$docsSource\*" -Destination $docsDir -Force -Recurse
        Write-Info "Copied documentation files"
    }
}

function Copy-DeveloperTemplateFiles {
    # Copy Developer template files to .claude/ root for user customization
    # These are only copied if this is a Developer edition installation

    $devFeaturesPath = Join-Path $script:PluginPath "skills\pbi-squire\developer-features.md"
    if (-not (Test-Path $devFeaturesPath)) {
        return  # Not a Developer installation
    }

    $copied = 0

    foreach ($file in $script:DeveloperTemplateFiles) {
        $sourcePath = Join-Path $script:TemplatesPath $file
        $destPath = Join-Path $script:LocalClaudeDir $file

        # Only copy if destination doesn't exist (preserve user customizations)
        if ((Test-Path $sourcePath) -and (-not (Test-Path $destPath))) {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            $copied++
            Write-Success "Created customizable $file"
        } elseif (Test-Path $destPath) {
            Write-Info "$file already exists (preserving your customizations)"
        }
    }

    if ($copied -gt 0) {
        Write-Info "Developer templates ready for customization in $script:LocalClaudeDir"
    }
}

function Get-ExistingPBIPath {
    # Check if settings.json already has a PBI path configured
    $settingsPath = Join-Path $script:LocalClaudeDir "settings.json"

    if (-not (Test-Path $settingsPath)) {
        return $null
    }

    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json

        # Look for Read/Edit/Write permissions that aren't the standard tool paths
        $allowList = $settings.permissions.allow
        if (-not $allowList) {
            return $null
        }

        foreach ($permission in $allowList) {
            # Match patterns like "Read(C:/Projects/MyPBI/**)" or "Read(/path/to/pbi/**)"
            if ($permission -match '^Read\(([^)]+/\*\*)\)$') {
                $path = $matches[1] -replace '/\*\*$', ''
                # Skip if it's the .claude tools path
                if ($path -notmatch '\.claude') {
                    return $path
                }
            }
        }
    } catch {
        Write-Warn "Could not parse existing settings.json: $_"
    }

    return $null
}

function Get-PBIProjectPath {
    # First, check if a path is already configured in settings.json
    $existingPath = Get-ExistingPBIPath
    if ($existingPath) {
        Write-Success "Found existing Power BI path in settings.json: $existingPath"
        return $null  # Return null to indicate no new path needed
    }

    # Prompt user for Power BI project path if not provided
    if (-not $Silent) {
        Write-Host ""
        Write-Host "  ============================================================" -ForegroundColor Cyan
        Write-Host "  POWER BI PROJECT PATH CONFIGURATION" -ForegroundColor Cyan
        Write-Host "  ============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  To allow PBI Squire to read/edit your Power BI files without" -ForegroundColor White
        Write-Host "  prompting for permission each time, enter the path to your" -ForegroundColor White
        Write-Host "  Power BI project folder." -ForegroundColor White
        Write-Host ""
        Write-Host "  Examples:" -ForegroundColor Gray
        Write-Host "    C:\Projects\SalesReport" -ForegroundColor Gray
        Write-Host "    C:\Users\Me\Documents\Power BI Projects" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Press Enter to skip (you can add paths later in settings.json)" -ForegroundColor Yellow
        Write-Host ""
    }

    $path = Read-Host "  Enter Power BI project path (or press Enter to skip)"
    return $path.Trim()
}

function Get-DataSensitiveMode {
    # Check if config already exists
    $configPath = Join-Path $script:LocalClaudeDir "pbi-squire.json"

    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
            if ($null -ne $config.dataSensitiveMode) {
                $mode = if ($config.dataSensitiveMode) { "enabled" } else { "disabled" }
                Write-Success "Data-sensitive mode: $mode (from existing config)"
                return $null  # Don't prompt, use existing
            }
        } catch {
            Write-Warn "Could not parse existing config: $_"
        }
    }

    # Prompt user
    if (-not $Silent) {
        Write-Host ""
        Write-Host "  ============================================================" -ForegroundColor Cyan
        Write-Host "  DATA SENSITIVITY CONFIGURATION" -ForegroundColor Cyan
        Write-Host "  ============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Does this project contain sensitive data (PII, financial," -ForegroundColor White
        Write-Host "  healthcare, or confidential business data)?" -ForegroundColor White
        Write-Host ""
        Write-Host "  If YES: The skill will require data anonymization before" -ForegroundColor Gray
        Write-Host "          any MCP queries that could expose actual values." -ForegroundColor Gray
        Write-Host ""
        Write-Host "  If NO:  The skill will proceed without anonymization checks." -ForegroundColor Gray
        Write-Host ""
    }

    $response = Read-Host "  Enable data-sensitive mode? (y/N)"
    return ($response -match "^[Yy]")
}

function Initialize-SkillConfig {
    param(
        [string]$ProjectPath,
        [bool]$DataSensitiveMode
    )

    $configPath = Join-Path $script:LocalClaudeDir "pbi-squire.json"

    if (Test-Path $configPath) {
        Write-Info "pbi-squire.json already exists"
        return
    }

    $config = @{
        projectPath = if ($ProjectPath) { $ProjectPath.Replace('\', '/') } else { $null }
        dataSensitiveMode = $DataSensitiveMode
        mode = "single"
        projectOverrides = @{}
    }

    $config | ConvertTo-Json -Depth 3 | Set-Content $configPath -Encoding UTF8

    $sensitiveMode = if ($DataSensitiveMode) { "enabled" } else { "disabled" }
    Write-Success "Created pbi-squire.json"
    if ($ProjectPath) {
        Write-Info "  Project path: $ProjectPath"
    }
    Write-Info "  Data-sensitive mode: $sensitiveMode"
    Write-Info "  Repository mode: single"
}

function Initialize-SettingsFile {
    param([string]$PBIPath)

    # Create settings.json with recommended permissions if it doesn't exist
    $settingsPath = Join-Path $script:LocalClaudeDir "settings.json"
    $templatePath = Join-Path $script:TemplatesPath "settings.json"

    if (Test-Path $settingsPath) {
        Write-Info "settings.json already exists - skipping (won't overwrite your config)"
        Write-Info "To add recommended permissions, see: tools/templates/settings.json"

        # If a PBI path was provided, offer to add it to existing config
        if ($PBIPath -and (Test-Path $PBIPath)) {
            Write-Info "To add your Power BI path, manually edit .claude/settings.json"
            Write-Info "Add these lines to the 'allow' array:"
            $normalizedPath = $PBIPath.Replace('\', '/')
            Write-Host "      `"Read($normalizedPath/**)`"," -ForegroundColor Yellow
            Write-Host "      `"Edit($normalizedPath/**)`"," -ForegroundColor Yellow
            Write-Host "      `"Write($normalizedPath/**)`"" -ForegroundColor Yellow
        }
        return
    }

    if (-not (Test-Path $templatePath)) {
        Write-Warn "Settings template not found at: $templatePath"
        return
    }

    # Read the template
    $settings = Get-Content $templatePath -Raw | ConvertFrom-Json

    # Add PBI project path permissions if provided
    if ($PBIPath -and (Test-Path $PBIPath)) {
        # Normalize path: use forward slashes for cross-platform compatibility
        $normalizedPath = $PBIPath.Replace('\', '/')

        # Add path-specific permissions
        $settings.permissions.allow += "Read($normalizedPath/**)"
        $settings.permissions.allow += "Edit($normalizedPath/**)"
        $settings.permissions.allow += "Write($normalizedPath/**)"

        Write-Success "Added permissions for: $PBIPath"
    }

    # Write the settings file
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8

    Write-Success "Created settings.json with auto-approve permissions"
    Write-Info "Tools like Read, Glob, Grep, Edit will run without prompts"

    if ($PBIPath) {
        Write-Info "Power BI project path added to permissions"
    }
}

function Initialize-ClaudeMd {
    param([string]$PBIPath)

    # Create minimal CLAUDE.md that references the PBI Squire plugin
    # Detailed instructions live in SKILL.md (updated with plugin, not user files)
    $claudeMdPath = "CLAUDE.md"
    $templatePath = Join-Path $script:TemplatesPath "CLAUDE.md"

    if (-not (Test-Path $templatePath)) {
        Write-Warn "CLAUDE.md template not found at: $templatePath"
        return
    }

    # Read template and replace placeholders
    $content = Get-Content $templatePath -Raw
    if ($PBIPath) {
        $normalizedPath = $PBIPath.Replace('\', '/')
        $content = $content.Replace('{{PBI_PROJECT_PATH}}', "Power BI projects are located at: ``$normalizedPath``")
        $content = $content.Replace('{{ALLOWED_PATHS}}', "- ``$normalizedPath/**``")
    } else {
        $content = $content.Replace('{{PBI_PROJECT_PATH}}', "_No Power BI project path configured._")
        $content = $content.Replace('{{ALLOWED_PATHS}}', "_No specific paths configured._")
    }

    if (Test-Path $claudeMdPath) {
        $existing = Get-Content $claudeMdPath -Raw
        if ($existing -match "PBI Squire") {
            Write-Info "CLAUDE.md already references PBI Squire Plugin"
            return
        }

        # CLAUDE.md exists but doesn't have the plugin reference - prompt user
        if (-not $Silent) {
            Write-Host ""
            Write-Host "  ============================================================" -ForegroundColor Yellow
            Write-Host "  CLAUDE.md UPDATE RECOMMENDED" -ForegroundColor Yellow
            Write-Host "  ============================================================" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  Your project has a CLAUDE.md file, but it doesn't reference" -ForegroundColor White
            Write-Host "  the PBI Squire Plugin. Claude won't automatically use" -ForegroundColor White
            Write-Host "  the skill without this reference." -ForegroundColor White
            Write-Host ""
            Write-Host "  Would you like to append the plugin reference to CLAUDE.md?" -ForegroundColor Cyan
            Write-Host ""
            $response = Read-Host "  Add plugin reference? (Y/n)"

            if ($response -match "^[Nn]") {
                Write-Warn "Skipping CLAUDE.md update. To add manually, see:"
                Write-Warn "  $templatePath"
                return
            }
        }

        # Append to existing CLAUDE.md
        Write-Info "Appending PBI Squire plugin reference to existing CLAUDE.md"
        $content = $existing + "`n`n" + $content
    } else {
        Write-Info "Creating CLAUDE.md with PBI Squire plugin reference"
    }

    Set-Content -Path $claudeMdPath -Value $content -Encoding UTF8
    Write-Success "CLAUDE.md configured with PBI Squire plugin reference"
}

# ============================================================
# MAIN
# ============================================================

try {
    $pluginVersion = Get-PluginVersion
    $localVersion = Get-LocalVersion
    $status = Compare-Versions -PluginVersion $pluginVersion -LocalVersion $localVersion

    # Detect edition (Developer vs Analyst)
    $devFeaturesPath = Join-Path $script:PluginPath "skills\pbi-squire\developer-features.md"
    $edition = if (Test-Path $devFeaturesPath) { "Developer" } else { "Analyst" }

    Write-Info "Plugin version: $pluginVersion ($edition Edition)"
    Write-Info "Local version:  $(if ($localVersion) { $localVersion } else { '(not installed)' })"
    Write-Info "Status: $status"

    # Determine if we need to copy
    $needsCopy = $false

    switch ($status) {
        "missing" {
            Write-Info "Tools not found in project - will install"
            $needsCopy = $true
        }
        "outdated" {
            Write-Warn "Local tools are outdated - will update"
            $needsCopy = $true
        }
        "newer" {
            Write-Warn "Local tools are newer than plugin (manual edits?)"
            if ($Force) {
                Write-Info "Force flag set - will overwrite"
                $needsCopy = $true
            }
        }
        "current" {
            Write-Success "Tools are up to date"
            if ($Force) {
                Write-Info "Force flag set - will refresh"
                $needsCopy = $true
            }
        }
    }

    # Check-only mode
    if ($CheckOnly) {
        if ($needsCopy) {
            Write-Info "Update available: $localVersion -> $pluginVersion"
            exit 1  # Exit code 1 = update needed
        } else {
            Write-Success "No update needed"
            exit 0  # Exit code 0 = current
        }
    }

    # Perform copy if needed
    if ($needsCopy) {
        $isDeveloper = ($edition -eq "Developer")

        Initialize-LocalDirectories
        Copy-ToolFiles -IsDeveloper $isDeveloper
        Copy-HelperFiles
        Copy-DocsFiles
        if ($isDeveloper) {
            Copy-DeveloperTemplateFiles
        }

        # Get PBI project path (from parameter or prompt)
        $pbiPath = $PBIProjectPath
        if (-not $pbiPath -and -not $Silent -and -not $CheckOnly) {
            $pbiPath = Get-PBIProjectPath
        }

        # Get data sensitivity preference
        $dataSensitive = Get-DataSensitiveMode
        if ($null -ne $dataSensitive) {
            Initialize-SkillConfig -ProjectPath $pbiPath -DataSensitiveMode $dataSensitive
        }

        Initialize-SettingsFile -PBIPath $pbiPath
        Initialize-ClaudeMd -PBIPath $pbiPath

        Write-Success "Bootstrap complete! ($edition Edition)"
        Write-Info "Configuration installed to: $script:LocalClaudeDir"
        Write-Info "Version: $pluginVersion"
        Write-Info ""
        if ($isDeveloper) {
            Write-Info "Developer features enabled: Python analysis tools installed"
            Write-Info "  Tools location: $script:LocalToolsDir"
        } else {
            Write-Info "Analyst Edition: Uses MCP + Claude-native validation"
            Write-Info "  No Python required - install Power BI Modeling MCP for best results"
        }
        Write-Info ""
        Write-Info "Note: Agents and skills are already available globally from the plugin."
    }

    exit 0

} catch {
    Write-Host "  [bootstrap] ERROR: $_" -ForegroundColor Red
    exit 1
}
