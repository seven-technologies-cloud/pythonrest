$ErrorActionPreference = 'Stop'
$packageName = 'pythonrest'
$url = 'https://github.com/seven-technologies-cloud/pythonrest/releases/download/0.1.0/pythonrest.exe'
$checksum = 'CC33CDB132DF44F67BB356680F4A94DF007F5969965F0D40E466382D08EAE8EF'
$checksumType = 'sha256'
$toolsDir = "$(Get-ToolsLocation)\$packageName"

Write-Host "Starting $packageName installation..."

if (-not (Test-Path $toolsDir)) {
    Write-Host "Directory not found in $toolsDir, creating a new one..."
    New-Item -ItemType Directory -Path $toolsDir -Force
    Write-Host "Directory created."
} else {
    Write-Host "Installation directory already exists, moving to next steps..."
}


Write-Host "Starting download from $url..."
Get-ChocolateyWebFile -PackageName $packageName -FileFullPath "$toolsDir\pythonrest.exe" -Url $url -Checksum $checksum -ChecksumType $checksumType
Write-Host "Download successful"


Write-Host "Successful installation! Try $packageName using the command 'pythonrest version' in your terminal."
