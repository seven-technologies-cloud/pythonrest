$ErrorActionPreference = 'Stop'; # stop on all errors
$packageName = 'pythonrest'
$url = 'https://github.com/daflongustavo/pythonrest/releases/download/0.1.0/pythonrest.exe'
$installDir = Join-Path -Path 'C:\Program Files' -ChildPath $packageName

# Creates Installation path, if it does not exist
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force
}

# Download binary
Get-ChocolateyWebFile -PackageName $packageName -FileFullPath "$installDir\pythonrest.exe" -Url $url

# Update PATH env
$envPath = [Environment]::GetEnvironmentVariable('Path', [EnvironmentVariableTarget]::Machine)
if (-not ($envPath -split ';' -contains $installDir)) {
    $newPath = "$envPath;$installDir"
    [Environment]::SetEnvironmentVariable('Path', $newPath, [EnvironmentVariableTarget]::Machine)
}

# Post Installation Message
Write-Host "Successful installation! Try $packageName using the command 'pythonrest version' in your terminal."
