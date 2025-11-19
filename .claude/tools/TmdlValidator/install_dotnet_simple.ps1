# Simple .NET 8.0 SDK Installation Script
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ".NET 8.0 SDK Installation" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$dotnetInstalled = $false
try {
    $version = & dotnet --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $version -like "8.*") {
        Write-Host "SUCCESS: .NET SDK 8.x is already installed (version $version)" -ForegroundColor Green
        $dotnetInstalled = $true
    }
}
catch {
    # Not installed
}

if ($dotnetInstalled) {
    Write-Host ""
    Write-Host "You can proceed to build the TMDL Validator." -ForegroundColor Green
    exit 0
}

# Not installed - open download page
Write-Host "The .NET 8.0 SDK is not installed." -ForegroundColor Yellow
Write-Host ""
Write-Host "Please install it using ONE of these methods:" -ForegroundColor Cyan
Write-Host ""
Write-Host "METHOD 1: Download and Install Manually (Recommended)" -ForegroundColor White
Write-Host "-------------------------------------------------" -ForegroundColor White
Write-Host "1. Opening download page in browser..." -ForegroundColor Yellow
Write-Host "2. Click the 'Download .NET SDK x64' button" -ForegroundColor Yellow
Write-Host "3. Run the downloaded installer" -ForegroundColor Yellow
Write-Host "4. After installation, restart this terminal" -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "https://dotnet.microsoft.com/download/dotnet/8.0"

Write-Host ""
Write-Host "METHOD 2: Install via Command Line (if you have winget)" -ForegroundColor White
Write-Host "--------------------------------------------------------" -ForegroundColor White
Write-Host "Run: winget install Microsoft.DotNet.SDK.8" -ForegroundColor Cyan
Write-Host ""

Write-Host "After installing, verify by running:" -ForegroundColor Yellow
Write-Host "  dotnet --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then build the validator with:" -ForegroundColor Yellow
Write-Host "  cd .claude\tools\TmdlValidator" -ForegroundColor Cyan
Write-Host "  .\build.ps1" -ForegroundColor Cyan
