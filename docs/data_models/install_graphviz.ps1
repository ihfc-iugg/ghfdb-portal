# Install Graphviz to user directory (no admin required)
# This script downloads and installs Graphviz portable version

$ErrorActionPreference = "Stop"

# Configuration
$graphvizVersion = "14.1.2"
$installDir = "$env:USERPROFILE\graphviz"
$downloadUrl = "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/$graphvizVersion/windows_10_cmake_Release_Graphviz-$graphvizVersion-win64.zip"
$tempZip = "$env:TEMP\graphviz-$graphvizVersion.zip"

Write-Host "Installing Graphviz $graphvizVersion to $installDir" -ForegroundColor Cyan
Write-Host ""

# Create installation directory
Write-Host "Creating installation directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

# Download Graphviz
Write-Host "Downloading Graphviz (this may take a minute)..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip -UseBasicParsing
    Write-Host "  Downloaded to: $tempZip" -ForegroundColor Green
} catch {
    Write-Host "  Failed to download. Trying alternate URL..." -ForegroundColor Red
    # Try alternate portable version
    $alternateUrl = "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/$graphvizVersion/portable_windows_10_cmake_Release_Graphviz-$graphvizVersion-win64.zip"
    Invoke-WebRequest -Uri $alternateUrl -OutFile $tempZip -UseBasicParsing
}

# Extract archive
Write-Host "Extracting files..." -ForegroundColor Yellow
Expand-Archive -Path $tempZip -DestinationPath "$installDir\temp" -Force

# Find the bin directory (it might be nested)
$binPath = Get-ChildItem -Path "$installDir\temp" -Recurse -Directory -Filter "bin" | 
    Where-Object { Test-Path (Join-Path $_.FullName "dot.exe") } | 
    Select-Object -First 1 -ExpandProperty FullName

if ($binPath) {
    # Move contents up to install directory
    $parentDir = Split-Path $binPath -Parent
    Get-ChildItem -Path $parentDir | Move-Item -Destination $installDir -Force
    Remove-Item -Path "$installDir\temp" -Recurse -Force
    
    $binPath = Join-Path $installDir "bin"
} else {
    Write-Host "  Error: Could not find bin directory with dot.exe" -ForegroundColor Red
    exit 1
}

# Clean up
Remove-Item $tempZip -Force

# Add to PATH
Write-Host "Adding to user PATH..." -ForegroundColor Yellow
$userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike "*$binPath*") {
    $newPath = if ($userPath) { "$userPath;$binPath" } else { $binPath }
    [System.Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
    $env:Path = "$env:Path;$binPath"
    Write-Host "  Added: $binPath" -ForegroundColor Green
} else {
    Write-Host "  Already in PATH" -ForegroundColor Green
}

# Test installation
Write-Host ""
Write-Host "Testing installation..." -ForegroundColor Yellow
$dotExe = Join-Path $binPath "dot.exe"
if (Test-Path $dotExe) {
    & $dotExe -V
    Write-Host ""
    Write-Host "Graphviz installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation location: $installDir" -ForegroundColor Cyan
    Write-Host "Executables location: $binPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You may need to restart your terminal for PATH changes to take effect." -ForegroundColor Yellow
} else {
    Write-Host "Error: dot.exe not found at $dotExe" -ForegroundColor Red
    exit 1
}
