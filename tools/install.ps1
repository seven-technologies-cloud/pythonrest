$ErrorActionPreference = 'Stop'; # stop on all errors
$packageName = 'pythonREST'
$url        = 'https://github.com/daflongustavo/pythonrest/releases/download/0.1.0/pythonrest.exe'
$installDir = "C:\Program Files\$packageName"

# Creates Installation path, if it does not exist
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir
}

# Download binary 
Get-ChocolateyWebFile -PackageName $packageName -FileFullPath "$installDir\nomeDoSeuBinario.exe" -Url $url

# Update PATH env
$envPath = [Environment]::GetEnvironmentVariable('Path', [EnvironmentVariableTarget]::Machine)
if (-not ($envPath.Split(';') -contains $installDir)) {
    [Environment]::SetEnvironmentVariable('Path', "$envPath;$installDir", [EnvironmentVariableTarget]::Machine)
}

# Post Installation Message
Write-Host "Successful installation! Try $packageName executing 'pythonrest version' in your terminal"
