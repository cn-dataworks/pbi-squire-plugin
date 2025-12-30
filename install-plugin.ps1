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
    [string]$TargetDir = "$HOME\.claude\plugins\custom\powerbi-analyst"
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n>> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "   $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "   $Message" -ForegroundColor Yellow
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

# Use claude -c to run the install command
$installResult = claude -c "/plugin install `"$TargetDir`"" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "Plugin registered successfully"
} else {
    Write-Warn "Plugin registration returned non-zero exit code"
    Write-Host "   Output: $installResult" -ForegroundColor Gray
}

# Step 4: Verification
Write-Step "Verifying installation..."

Write-Host "   Plugin location: $TargetDir" -ForegroundColor White
Write-Host "   To verify, run in Claude Code: /plugin list" -ForegroundColor White

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Open Claude Code in a Power BI project folder" -ForegroundColor Gray
Write-Host "  2. Run: /plugin list  (to verify)" -ForegroundColor Gray
Write-Host "  3. Ask: 'What Power BI workflows can you help with?'" -ForegroundColor Gray
Write-Host ""
