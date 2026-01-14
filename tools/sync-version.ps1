#Requires -Version 5.1
<#
.SYNOPSIS
    Syncs version across all version locations in the plugin.

.DESCRIPTION
    This script ensures version consistency between:
    - tools/core/version.txt (source of truth)
    - .claude-plugin/plugin.json (plugin metadata)

    Can also bump the version when a new version is provided.

.PARAMETER Version
    New version to set (e.g., "1.3.0"). If not provided, syncs current version.txt to plugin.json.

.PARAMETER Check
    Only check if versions are in sync, don't modify files.

.EXAMPLE
    .\sync-version.ps1
    # Syncs current version.txt value to plugin.json

.EXAMPLE
    .\sync-version.ps1 -Version "1.3.0"
    # Sets version to 1.3.0 in all locations

.EXAMPLE
    .\sync-version.ps1 -Check
    # Checks if versions are in sync (exit code 1 if out of sync)
#>

[CmdletBinding()]
param(
    [string]$Version,
    [switch]$Check
)

$ErrorActionPreference = "Stop"

# Determine paths relative to script location
$scriptDir = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path "$scriptDir\.claude-plugin")) {
    $scriptDir = $PSScriptRoot
    if (-not (Test-Path "$scriptDir\..\..\.claude-plugin")) {
        Write-Error "Cannot find plugin root directory"
        exit 1
    }
    $scriptDir = Resolve-Path "$scriptDir\..\.."
}

$versionTxtPath = Join-Path $scriptDir "tools\core\version.txt"
$pluginJsonPath = Join-Path $scriptDir ".claude-plugin\plugin.json"

# Read current versions
function Get-VersionFromTxt {
    if (Test-Path $versionTxtPath) {
        return (Get-Content $versionTxtPath -Raw).Trim()
    }
    return $null
}

function Get-VersionFromJson {
    if (Test-Path $pluginJsonPath) {
        $json = Get-Content $pluginJsonPath -Raw | ConvertFrom-Json
        return $json.version
    }
    return $null
}

$txtVersion = Get-VersionFromTxt
$jsonVersion = Get-VersionFromJson

Write-Host "Current versions:" -ForegroundColor Cyan
Write-Host "  version.txt:  $txtVersion"
Write-Host "  plugin.json:  $jsonVersion"

# Check mode - just report sync status
if ($Check) {
    if ($txtVersion -eq $jsonVersion) {
        Write-Host "`nVersions are in sync." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "`nVersions are OUT OF SYNC!" -ForegroundColor Red
        Write-Host "Run '.\sync-version.ps1' to sync them."
        exit 1
    }
}

# Determine target version
$targetVersion = if ($Version) { $Version } else { $txtVersion }

if (-not $targetVersion) {
    Write-Error "No version found in version.txt and no -Version provided"
    exit 1
}

# Validate version format (semver)
if ($targetVersion -notmatch '^\d+\.\d+\.\d+$') {
    Write-Error "Invalid version format: $targetVersion (expected: X.Y.Z)"
    exit 1
}

Write-Host "`nTarget version: $targetVersion" -ForegroundColor Yellow

# Update version.txt if new version provided
if ($Version -and $Version -ne $txtVersion) {
    Write-Host "Updating version.txt..." -ForegroundColor Cyan
    Set-Content -Path $versionTxtPath -Value $targetVersion -NoNewline
    # Add newline
    Add-Content -Path $versionTxtPath -Value ""
    Write-Host "  Updated: $txtVersion -> $targetVersion" -ForegroundColor Green
}

# Update plugin.json
if ($targetVersion -ne $jsonVersion) {
    Write-Host "Updating plugin.json..." -ForegroundColor Cyan
    $json = Get-Content $pluginJsonPath -Raw | ConvertFrom-Json
    $json.version = $targetVersion
    $json | ConvertTo-Json -Depth 10 | Set-Content $pluginJsonPath -Encoding UTF8
    Write-Host "  Updated: $jsonVersion -> $targetVersion" -ForegroundColor Green
} else {
    Write-Host "plugin.json already at $targetVersion" -ForegroundColor Green
}

Write-Host "`nVersion sync complete!" -ForegroundColor Green
Write-Host @"

Next steps:
  1. Review changes: git diff
  2. Commit: git add tools/core/version.txt .claude-plugin/plugin.json
  3. Commit: git commit -m "Bump version to $targetVersion"
  4. If on main, merge to pro: git checkout pro && git merge main
"@
