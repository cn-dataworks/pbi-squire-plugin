<#
.SYNOPSIS
    Installs or updates the Power BI Analyst plugin for Claude Code.

.DESCRIPTION
    This script clones (or pulls) the powerbi-analyst-plugin repository
    and registers it with Claude Code using the /plugin install command.

.NOTES
    Requirements:
    - Git installed and in PATH
    - Claude Code installed
    - GitHub access (for cloning)

.EXAMPLE
    .\install-plugin.ps1

    Installs or updates the plugin to the default location.
#>

[CmdletBinding()]
param(
    [string]$TargetDir = "$HOME\.claude\plugins\custom\powerbi-analyst",
    [switch]$SkipMcpConfig
)

$ErrorActionPreference = "Stop"

# ============================================================
# CONFIGURATION
# ============================================================

$script:McpBinaryName = "powerbi-modeling-mcp.exe"

# Search paths for MCP binary (Windows)
$script:McpSearchPaths = @(
    # VS Code extensions
    "$env:USERPROFILE\.vscode\extensions\*\*\$script:McpBinaryName",
    "$env:USERPROFILE\.vscode-insiders\extensions\*\*\$script:McpBinaryName",
    # Standard install locations
    "$env:ProgramFiles\PowerBI Modeling MCP\$script:McpBinaryName",
    "${env:ProgramFiles(x86)}\PowerBI Modeling MCP\$script:McpBinaryName",
    "$env:LOCALAPPDATA\Programs\PowerBI Modeling MCP\$script:McpBinaryName",
    "$env:APPDATA\PowerBI Modeling MCP\$script:McpBinaryName",
    # NPM global
    "$env:APPDATA\npm\node_modules\*\$script:McpBinaryName"
)

# Claude config locations
$script:ClaudeConfigPaths = @(
    "$env:APPDATA\Claude\claude_desktop_config.json",
    "$env:LOCALAPPDATA\Claude\claude_desktop_config.json",
    "$env:USERPROFILE\.claude\settings.json"
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Write-Step {
    param([string]$Message)
    Write-Host "`n>> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "   [OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "   [!] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "       $Message" -ForegroundColor Gray
}

# ============================================================
# MCP DETECTION
# ============================================================

function Find-McpBinary {
    # Check PATH first
    $pathResult = Get-Command $script:McpBinaryName -ErrorAction SilentlyContinue
    if ($pathResult) {
        return $pathResult.Source
    }

    # Search known locations
    foreach ($pattern in $script:McpSearchPaths) {
        $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        if ($matches) {
            $found = $matches | Select-Object -First 1
            return $found.FullName
        }
    }

    return $null
}

# ============================================================
# CLAUDE CONFIGURATION
# ============================================================

function Get-ClaudeConfigPath {
    foreach ($path in $script:ClaudeConfigPaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    # Return default path if none exist
    return $script:ClaudeConfigPaths[0]
}

function Update-ClaudeConfig {
    param([string]$McpPath)

    $configPath = Get-ClaudeConfigPath

    # Load or create config
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
            Write-Info "Updating existing config: $configPath"
        } catch {
            Write-Warn "Could not parse existing config, creating backup"
            Copy-Item $configPath "$configPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            $config = @{}
        }
    } else {
        $config = @{}
        $dir = Split-Path $configPath -Parent
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        Write-Info "Creating new config: $configPath"
    }

    # Ensure mcpServers exists
    if (-not $config.mcpServers) {
        $config | Add-Member -NotePropertyName 'mcpServers' -NotePropertyValue @{} -Force
    }

    # Check if already configured with same path
    if ($config.mcpServers.'powerbi-modeling') {
        $existingPath = $config.mcpServers.'powerbi-modeling'.command
        if ($existingPath -eq $McpPath) {
            Write-Success "MCP already configured"
            return
        }
        Write-Info "Updating MCP path in config"
    }

    # Add MCP server config
    $mcpConfig = @{
        command = $McpPath
        args = @()
        env = @{}
    }

    if ($config.mcpServers -is [PSCustomObject]) {
        $config.mcpServers | Add-Member -NotePropertyName 'powerbi-modeling' -NotePropertyValue $mcpConfig -Force
    } else {
        $config.mcpServers['powerbi-modeling'] = $mcpConfig
    }

    # Save config
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Success "Claude config updated with MCP server"
}

function Show-CapabilitySummary {
    param([bool]$McpAvailable)

    Write-Host ""
    if ($McpAvailable) {
        Write-Host "   Mode: " -NoNewline
        Write-Host "Desktop Mode (full validation)" -ForegroundColor Green
        Write-Host ""
        Write-Host "   Capabilities:" -ForegroundColor White
        Write-Host "       [OK] DAX/M code generation" -ForegroundColor Green
        Write-Host "       [OK] TMDL file editing" -ForegroundColor Green
        Write-Host "       [OK] PBIR visual creation" -ForegroundColor Green
        Write-Host "       [OK] Live DAX validation" -ForegroundColor Green
        Write-Host "       [OK] Real-time error checking" -ForegroundColor Green
    } else {
        Write-Host "   Mode: " -NoNewline
        Write-Host "File-Only Mode (limited validation)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Capabilities:" -ForegroundColor White
        Write-Host "       [OK] DAX/M code generation" -ForegroundColor Green
        Write-Host "       [OK] TMDL file editing" -ForegroundColor Green
        Write-Host "       [OK] PBIR visual creation" -ForegroundColor Green
        Write-Host "       [--] Live DAX validation (requires MCP)" -ForegroundColor Yellow
        Write-Host "       [--] Real-time error checking (requires MCP)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   To enable full features:" -ForegroundColor White
        Write-Host "       1. Install MCP: https://github.com/microsoft/powerbi-modeling-mcp" -ForegroundColor Gray
        Write-Host "       2. Re-run this installer: .\install-plugin.ps1" -ForegroundColor Gray
    }
}

# Banner
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Power BI Analyst Plugin Installer" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# Step 1: Check prerequisites
Write-Step "Checking prerequisites..."

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Success "Git found: $gitVersion"
} catch {
    Write-Host "   ERROR: Git not found. Install from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check Claude Code
try {
    $claudeVersion = claude --version 2>&1
    Write-Success "Claude Code found: $claudeVersion"
} catch {
    Write-Host "   ERROR: Claude Code not found. Install from https://claude.ai/code" -ForegroundColor Red
    exit 1
}

# Step 2: Clone or update repository
Write-Step "Setting up plugin directory..."

$repoUrl = "https://github.com/cn-dataworks/powerbi-analyst-plugin.git"

if (!(Test-Path $TargetDir)) {
    Write-Host "   Cloning repository to: $TargetDir" -ForegroundColor White

    # Create parent directory if needed
    $parentDir = Split-Path $TargetDir -Parent
    if (!(Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # Clone
    git clone $repoUrl $TargetDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ERROR: Git clone failed. Check your GitHub access." -ForegroundColor Red
        Write-Host "   TIP: Run 'gh auth login' if using GitHub CLI" -ForegroundColor Yellow
        exit 1
    }
    Write-Success "Repository cloned successfully"
} else {
    Write-Host "   Plugin already exists, pulling latest..." -ForegroundColor White
    Push-Location $TargetDir
    try {
        git pull
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "Git pull had issues, but continuing..."
        } else {
            Write-Success "Repository updated successfully"
        }
    } finally {
        Pop-Location
    }
}

# Step 3: Register with Claude Code
Write-Step "Registering plugin with Claude Code..."

# A. Add as Local Marketplace (This enables updates)
Write-Info "Adding local marketplace..."
$mkCommand = "/plugin marketplace add `"$TargetDir`""
$mkResult = claude -c $mkCommand 2>&1

# Check result (ignore "already exists" errors)
if ($LASTEXITCODE -ne 0) {
    if ($mkResult -match "already exists" -or $mkResult -match "Duplicate") {
        Write-Info "Marketplace already registered."
    } else {
        Write-Warn "Marketplace registration warning: $mkResult"
    }
} else {
    Write-Success "Local marketplace added."
}

# B. Install Plugin (by ID, not path, so it links to the marketplace)
Write-Info "Installing plugin..."
$installCommand = "/plugin install powerbi-analyst"
$installResult = claude -c $installCommand 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "Plugin installed successfully."
} elseif ($installResult -match "already installed") {
    Write-Info "Plugin is already installed. Attempting update..."
    claude -c "/plugin update powerbi-analyst" | Out-Null
    Write-Success "Plugin updated."
} else {
    Write-Warn "Plugin installation returned non-zero exit code"
    Write-Host "   Output: $installResult" -ForegroundColor Gray
}

# Step 4: Check for Power BI Modeling MCP
Write-Step "Checking for Power BI Modeling MCP..."

$mcpPath = Find-McpBinary
$mcpAvailable = $null -ne $mcpPath

if ($mcpAvailable) {
    Write-Success "Found: $mcpPath"

    # Configure Claude to use MCP
    if (-not $SkipMcpConfig) {
        Update-ClaudeConfig -McpPath $mcpPath
    } else {
        Write-Info "Skipping Claude config update (-SkipMcpConfig)"
    }
} else {
    Write-Warn "MCP not found"
    Write-Info "The plugin will work in File-Only mode"
}

# Step 5: Verification
Write-Step "Verifying installation..."

Write-Host "   Plugin location: $TargetDir" -ForegroundColor White

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Show-CapabilitySummary -McpAvailable $mcpAvailable

Write-Host ""
Write-Host "   Next steps:" -ForegroundColor White
Write-Host "       1. Open Claude Code in a Power BI project folder" -ForegroundColor Gray
Write-Host "       2. Run: /plugin list  (to verify)" -ForegroundColor Gray
Write-Host "       3. Ask: 'What Power BI workflows can you help with?'" -ForegroundColor Gray
Write-Host ""
