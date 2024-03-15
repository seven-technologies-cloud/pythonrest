$ErrorActionPreference = 'Stop';

$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url64 = 'https://github.com/daflongustavo/pythonrest/releases/download/0.1.0/pythonrest.exe'
$checksum64 = 'zDPNsTLfRPZ7s1ZoD0qU3wB/WWmWXw1A5GY4LQjq6O8='

$packageArgs = @{
  packageName    = $env:ChocolateyPackageName
  unzipLocation  = $toolsDir
  fileType       = 'exe'
  url64bit       = $url64
  softwareName   = 'pythonREST Command Line Interface*'
  checksum64     = $checksum64
  checksumType64 = 'sha256'
  silentArgs     = "/qn /norestart /l*v `"$($env:TEMP)\$($packageName).$($env:chocolateyPackageVersion).ExeInstall.log`""
  validExitCodes = @(0, 3010, 1641)
}

Install-ChocolateyPackage @packageArgs
