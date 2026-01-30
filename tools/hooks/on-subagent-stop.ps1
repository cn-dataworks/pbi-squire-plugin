<#
.SYNOPSIS
    Hook script executed when a Power BI subagent stops.

.DESCRIPTION
    This script is invoked by Claude Code when a powerbi-* subagent completes.
    It can be used to:
    - Record completion time
    - Clean up temporary resources
    - Calculate duration metrics
    - Trigger follow-up actions

.PARAMETER AgentName
    The name of the subagent that stopped (e.g., powerbi-code-locator)

.PARAMETER ExitCode
    The exit code from the subagent (0 = success, non-zero = failure)

.EXAMPLE
    .\on-subagent-stop.ps1 powerbi-code-locator 0
#>

param(
    [Parameter(Position=0)]
    [string]$AgentName = "unknown",

    [Parameter(Position=1)]
    [int]$ExitCode = 0
)

# Get current timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Determine status
$status = if ($ExitCode -eq 0) { "SUCCESS" } else { "FAILED" }

# Log subagent completion
$logEntry = @{
    event = "subagent_stop"
    agent = $AgentName
    timestamp = $timestamp
    exitCode = $ExitCode
    status = $status
}

# Write to console for debugging
Write-Host "[HOOK] Subagent stopped: $AgentName at $timestamp ($status)"

# Optional: Write to log file
$logDir = Join-Path $env:TEMP "powerbi-analyst-logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$logFile = Join-Path $logDir "subagent-events.log"
$logLine = "[$timestamp] STOP: $AgentName (exit: $ExitCode, status: $status)"
Add-Content -Path $logFile -Value $logLine -ErrorAction SilentlyContinue

# Optional: Clean up agent-specific temp files
# (Add cleanup logic here if needed)

# Return success regardless of agent exit code (hook itself succeeded)
exit 0
