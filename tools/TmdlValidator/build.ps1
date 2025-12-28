# Build script for TMDL Validator
# This compiles the C# TMDL validator into a standalone executable

Write-Host "Building TMDL Validator..." -ForegroundColor Cyan

# Check if dotnet is installed
if (-not (Get-Command "dotnet" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: .NET SDK is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install .NET 8.0 SDK from: https://dotnet.microsoft.com/download" -ForegroundColor Yellow
    exit 1
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Clean previous build
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path "bin") {
    Remove-Item -Recurse -Force "bin"
}
if (Test-Path "obj") {
    Remove-Item -Recurse -Force "obj"
}

# Restore dependencies
Write-Host "Restoring NuGet packages..." -ForegroundColor Yellow
dotnet restore

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to restore packages" -ForegroundColor Red
    exit 1
}

# Build and publish
Write-Host "Publishing self-contained executable..." -ForegroundColor Yellow
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=false

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    exit 1
}

# Copy executable to tools directory
$ExePath = "bin\Release\net8.0\win-x64\publish\TmdlValidator.exe"
$DestPath = "..\TmdlValidator.exe"

if (Test-Path $ExePath) {
    Write-Host "Copying executable to tools directory..." -ForegroundColor Yellow
    Copy-Item $ExePath $DestPath -Force

    $FileSize = (Get-Item $DestPath).Length / 1MB
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable: $DestPath (${FileSize:N2} MB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  ..\TmdlValidator.exe ""C:\path\to\project.SemanticModel""" -ForegroundColor White
} else {
    Write-Host "ERROR: Executable not found at $ExePath" -ForegroundColor Red
    exit 1
}
