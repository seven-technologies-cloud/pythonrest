function Write-Log($message) {
    Write-Host "$message"
}

function Run-Command($command) {
    Write-Log "Running command: $command"
    try {
        Invoke-Expression $command
    } catch {
        Write-Host "Error: $_"
        exit 1
    }
}

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition

try {
    Set-Location "$scriptPath"
} catch {
    Write-Host "Error: $_"
    exit 1
}

Run-Command "pyinstaller --onefile --add-data '../pythonrest.py;.' --add-data '../databaseconnector;databaseconnector' --add-data '../domaingenerator;domaingenerator' --add-data '../apigenerator;apigenerator' --collect-submodules typing --collect-submodules re --collect-submodules typer --collect-submodules yaml --collect-submodules parse --collect-submodules mergedeep --collect-submodules site --collect-submodules pymysql --collect-submodules psycopg2 --collect-submodules psycopg2-binary --collect-submodules pymssql --icon=../pythonrestlogo.ico --version-file=version_information.txt ../pythonrest.py"

try {
    Move-Item "$scriptPath\dist\pythonrest.exe" "$scriptPath" -Force
} catch {
    Write-Host "Error: $_"
    exit 1
}

Run-Command "pyinstaller --onefile --add-data 'pythonrest.exe;.' --add-data 'install_pythonrest.py;.' --add-data 'addpythonresttouserpath.ps1;.' --add-data 'script_hashs.json;.' --icon=../pythonrestlogo.ico --name PythonRESTInstaller --version-file=version_information.txt install_pythonrest.py"

Run-Command "pyinstaller --onefile --add-data 'uninstall_pythonrest.py;.' --add-data 'removepythonrestfromuserpath.ps1;.' --add-data 'script_hashs.json;.' --icon=../pythonrestlogo.ico --name PythonRESTUninstaller --version-file=version_information.txt uninstall_pythonrest.py"

$executablesDir = "$scriptPath\PythonRestExecutables"
if (-not (Test-Path -Path $executablesDir -PathType Container)) {
    Write-Log "Creating PythonRestExecutables directory..."
    try {
        New-Item -ItemType Directory -Force -Path $executablesDir
    } catch {
        Write-Host "Error: $_"
        exit 1
    }
} else {
    Write-Log "Cleaning PythonRestExecutables directory..."
    try {
        Remove-Item -Path "$executablesDir\*" -Force
    } catch {
        Write-Host "Error: $_"
        exit 1
    }
}

try {
    Move-Item "$scriptPath\dist\PythonRESTInstaller.exe" "$executablesDir" -Force
    Move-Item "$scriptPath\dist\PythonRESTUninstaller.exe" "$executablesDir" -Force
} catch {
    Write-Host "Error: $_"
    exit 1
}

try {
    Remove-Item -Path "$scriptPath\build" -Recurse -Force
    Remove-Item -Path "$scriptPath\dist" -Recurse -Force
    Remove-Item -Path "$scriptPath\*.spec" -Force
    Remove-Item -Path "$scriptPath\*.exe" -Force
} catch {
    Write-Host "Error: $_"
    exit 1
}

Write-Log "PythonRestExecutables successfully generated on path $executablesDir"
