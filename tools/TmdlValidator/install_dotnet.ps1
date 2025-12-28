# Install .NET 8.0 SDK
Write-Host "Downloading .NET 8.0 SDK..." -ForegroundColor Cyan

$installerPath = "$env:TEMP\dotnet-sdk-8.0-installer.exe"
$downloadUrl = "https://download.visualstudio.microsoft.com/download/pr/93961dfb-d1e0-49c8-9230-abcba1ebab5a/811ed1eb63d7652325727720edda26a8/dotnet-sdk-8.0.404-win-x64.exe"

# Download installer
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($downloadUrl, $installerPath)
    Write-Host "Download complete!" -ForegroundColor Green
}
catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    exit 1
}

# Check if file exists
if (-not (Test-Path $installerPath)) {
    Write-Host "ERROR: Installer not found at $installerPath" -ForegroundColor Red
    exit 1
}

# Run installer
Write-Host "Installing .NET 8.0 SDK..." -ForegroundColor Cyan
Write-Host "This will open an installer window. Please follow the prompts." -ForegroundColor Yellow

Start-Process -FilePath $installerPath -Wait

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Cyan
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$dotnetVersion = & dotnet --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS! .NET SDK version $dotnetVersion installed" -ForegroundColor Green
} else {
    Write-Host "WARNING: dotnet command not found. You may need to restart your terminal." -ForegroundColor Yellow
    Write-Host "After restarting, run: dotnet --version" -ForegroundColor Yellow
}

# Clean up
Remove-Item $installerPath -ErrorAction SilentlyContinue
