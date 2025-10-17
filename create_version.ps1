$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$originalPath = "C:\Users\anorthrup\Desktop\pssr comms proj pbip"
$originalName = Split-Path $originalPath -Leaf
$parentPath = Split-Path $originalPath -Parent
$newProjectName = "${originalName}_${timestamp}"
$newProjectPath = Join-Path $parentPath $newProjectName

Write-Host "Creating versioned copy..."
Write-Host "Original: $originalPath"
Write-Host "New: $newProjectPath"

Copy-Item -Path $originalPath -Destination $newProjectPath -Recurse -Force

if (Test-Path $newProjectPath) {
    Write-Host "Successfully created versioned copy at: $newProjectPath"
    Set-Content -Path "C:\Users\anorthrup\Documents\power_bi_analyst\temp_new_path.txt" -Value $newProjectPath
    Write-Host "Path saved to temp_new_path.txt"
} else {
    Write-Host "Failed to create versioned copy"
    exit 1
}
