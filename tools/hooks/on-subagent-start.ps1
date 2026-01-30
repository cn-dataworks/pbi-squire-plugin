<#
.SYNOPSIS
    Hook script executed when a Power BI subagent starts.

.DESCRIPTION
    This script is invoked by Claude Code when a pbi-squire-* subagent starts.
    It can be used to:
    - Initialize logging
    - Set up shared resources
    - Record start time for metrics

.PARAMETER AgentName
    The name of the subagent that started (e.g., pbi-squire-code-locator)

.EXAMPLE
    .\on-subagent-start.ps1 pbi-squire-code-locator
#>

param(
    [Parameter(Position=0)]
    [string]$AgentName = "unknown"
)

# Get current timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log subagent start
$logEntry = @{
    event = "subagent_start"
    agent = $AgentName
    timestamp = $timestamp
}

# Write to console for debugging
Write-Host "[HOOK] Subagent started: $AgentName at $timestamp"

# Optional: Write to log file if needed
$logDir = Join-Path $env:TEMP "pbi-squire-logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$logFile = Join-Path $logDir "subagent-events.log"
$logLine = "[$timestamp] START: $AgentName"
Add-Content -Path $logFile -Value $logLine -ErrorAction SilentlyContinue

# Return success
exit 0
