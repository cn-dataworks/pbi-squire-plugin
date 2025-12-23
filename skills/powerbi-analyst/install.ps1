#Requires -Version 5.1
<#
.SYNOPSIS
    Power BI Analyst Skill - Installer (PowerShell)

.DESCRIPTION
    Sets up the Power BI Analyst skill for Claude Code:
    - Detects MCP binary availability
    - Configures Claude settings if MCP found
    - Initializes state management
    - Reports configuration status

.EXAMPLE
    .\install.ps1
    .\install.ps1 -SkipMcpConfig
    .\install.ps1 -Verbose
#>

[CmdletBinding()]
param(
    [switch]$SkipMcpConfig,
    [switch]$Force
)

# ============================================================
# CONFIGURATION
# ============================================================

$script:SkillName = "powerbi-analyst"
$script:SkillVersion = "1.0.0"
$script:McpBinaryName = "powerbi-modeling-mcp.exe"
$script:StateManagerPath = Join-Path $PSScriptRoot "..\..\tools\state_manage.ps1"

# Search paths for MCP binary (Windows)
$script:McpSearchPaths = @(
    # VS Code extensions
    "$env:USERPROFILE\.vscode\extensions\*\*\$McpBinaryName",
    "$env:USERPROFILE\.vscode-insiders\extensions\*\*\$McpBinaryName",
    # Standard install locations
    "$env:ProgramFiles\PowerBI Modeling MCP\$McpBinaryName",
    "${env:ProgramFiles(x86)}\PowerBI Modeling MCP\$McpBinaryName",
    "$env:LOCALAPPDATA\Programs\PowerBI Modeling MCP\$McpBinaryName",
    "$env:APPDATA\PowerBI Modeling MCP\$McpBinaryName",
    # NPM global
    "$env:APPDATA\npm\node_modules\*\$McpBinaryName"
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
    Write-Host "`n[$script:SkillName] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  [!] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "  [X] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "      $Message" -ForegroundColor Gray
}

# ============================================================
# PREREQUISITE CHECKS
# ============================================================

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."

    $allPassed = $true

    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -ge 5) {
        Write-Success "PowerShell $($PSVersionTable.PSVersion) - OK"
    } else {
        Write-Error "PowerShell 5.1+ required (found $($PSVersionTable.PSVersion))"
        $allPassed = $false
    }

    # Check if running from skill directory
    $skillMdPath = Join-Path $PSScriptRoot "SKILL.md"
    if (Test-Path $skillMdPath) {
        Write-Success "Running from skill directory"
    } else {
        Write-Warning "Not running from skill directory - some features may not work"
    }

    # Check state manager exists
    if (Test-Path $script:StateManagerPath) {
        Write-Success "State manager found"
    } else {
        Write-Warning "State manager not found at $script:StateManagerPath"
    }

    return $allPassed
}

# ============================================================
# MCP DETECTION
# ============================================================

function Find-McpBinary {
    Write-Step "Searching for Power BI Modeling MCP..."

    # Check PATH first
    $pathResult = Get-Command $script:McpBinaryName -ErrorAction SilentlyContinue
    if ($pathResult) {
        Write-Success "Found in PATH: $($pathResult.Source)"
        return $pathResult.Source
    }

    # Search known locations
    foreach ($pattern in $script:McpSearchPaths) {
        $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        if ($matches) {
            $found = $matches | Select-Object -First 1
            Write-Success "Found: $($found.FullName)"
            return $found.FullName
        }
    }

    Write-Warning "MCP binary not found"
    Write-Info "The skill will run in File-Only mode (limited validation)"
    Write-Info "To enable full features, install Power BI Modeling MCP from:"
    Write-Info "https://github.com/microsoft/powerbi-modeling-mcp"
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

    if ($SkipMcpConfig) {
        Write-Info "Skipping Claude config update (-SkipMcpConfig)"
        return
    }

    Write-Step "Configuring Claude for MCP..."

    $configPath = Get-ClaudeConfigPath

    # Load or create config
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
            Write-Info "Updating existing config: $configPath"
        } catch {
            Write-Warning "Could not parse existing config, creating backup"
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

    # Check if already configured
    if ($config.mcpServers.'powerbi-modeling' -and -not $Force) {
        $existingPath = $config.mcpServers.'powerbi-modeling'.command
        if ($existingPath -eq $McpPath) {
            Write-Success "MCP already configured correctly"
            return
        }
        Write-Warning "MCP already configured with different path"
        Write-Info "Existing: $existingPath"
        Write-Info "New:      $McpPath"
        Write-Info "Use -Force to overwrite"
        return
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
    Write-Success "Claude config updated: $configPath"
}

# ============================================================
# STATE INITIALIZATION
# ============================================================

function Initialize-SkillState {
    Write-Step "Initializing skill state..."

    $stateDir = ".claude"
    $statePath = Join-Path $stateDir "state.json"

    # Create .claude directory if needed
    if (-not (Test-Path $stateDir)) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
        Write-Info "Created $stateDir directory"
    }

    # Initialize state via state manager
    if (Test-Path $script:StateManagerPath) {
        try {
            $result = & $script:StateManagerPath -Summary 2>&1
            Write-Success "State initialized"
        } catch {
            Write-Warning "Could not initialize state via manager"
        }
    } else {
        # Manual initialization
        if (-not (Test-Path $statePath)) {
            $now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            $initialState = @{
                session = @{
                    started = $now
                    last_activity = $now
                    skill_version = $script:SkillVersion
                    state_backend = "powershell"
                    mcp_available = $false
                }
                active_tasks = @{}
                resource_locks = @{}
                archived_tasks = @()
            } | ConvertTo-Json -Depth 5
            Set-Content $statePath $initialState -Encoding UTF8
            Write-Success "State file created"
        } else {
            Write-Success "State file exists"
        }
    }
}

# ============================================================
# SUMMARY REPORT
# ============================================================

function Show-InstallSummary {
    param(
        [bool]$McpAvailable,
        [string]$McpPath
    )

    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
    Write-Host " Power BI Analyst Skill - Installation Complete" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan

    Write-Host "`n Configuration:" -ForegroundColor White
    Write-Host "   Skill Version:  $script:SkillVersion"
    Write-Host "   State Backend:  PowerShell"

    if ($McpAvailable) {
        Write-Host "   MCP Status:     " -NoNewline
        Write-Host "ENABLED" -ForegroundColor Green
        Write-Host "   MCP Path:       $McpPath"
        Write-Host "`n   Mode:           Desktop Mode (full validation)"
    } else {
        Write-Host "   MCP Status:     " -NoNewline
        Write-Host "NOT FOUND" -ForegroundColor Yellow
        Write-Host "`n   Mode:           File-Only Mode (limited validation)"
        Write-Host "   To enable full features, install Power BI Modeling MCP"
    }

    Write-Host "`n Getting Started:" -ForegroundColor White
    Write-Host "   1. Open a Power BI project (.pbip folder)"
    Write-Host "   2. Ask Claude: 'Help me analyze this Power BI project'"
    Write-Host "   3. Or use a workflow: /evaluate-pbi-project-file"

    Write-Host "`n Documentation:" -ForegroundColor White
    Write-Host "   - Getting Started:  references/getting-started.md"
    Write-Host "   - Glossary:         references/glossary.md"
    Write-Host "   - Troubleshooting:  references/troubleshooting-faq.md"

    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
}

# ============================================================
# MAIN
# ============================================================

try {
    Write-Host "`n"
    Write-Host "Power BI Analyst Skill Installer" -ForegroundColor Cyan
    Write-Host "Version $script:SkillVersion" -ForegroundColor Gray
    Write-Host ""

    # Check prerequisites
    $prereqsPassed = Test-Prerequisites

    # Find MCP binary
    $mcpPath = Find-McpBinary
    $mcpAvailable = $null -ne $mcpPath

    # Configure Claude if MCP found
    if ($mcpAvailable) {
        Update-ClaudeConfig -McpPath $mcpPath
    }

    # Initialize state
    Initialize-SkillState

    # Update state with MCP status
    $statePath = ".claude/state.json"
    if (Test-Path $statePath) {
        try {
            $state = Get-Content $statePath -Raw | ConvertFrom-Json
            $state.session.mcp_available = $mcpAvailable
            $state | ConvertTo-Json -Depth 10 | Set-Content $statePath -Encoding UTF8
        } catch {
            Write-Verbose "Could not update MCP status in state"
        }
    }

    # Show summary
    Show-InstallSummary -McpAvailable $mcpAvailable -McpPath $mcpPath

} catch {
    Write-Host "`n[ERROR] Installation failed: $_" -ForegroundColor Red
    exit 1
}
