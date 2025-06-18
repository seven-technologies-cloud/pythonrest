# Function to log messages with timestamp
function Write-Log {
    param($Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
}

# Exit on error
$ErrorActionPreference = "Stop"

# 0. Define Project Root (assuming script is run from project root)
$PROJECT_ROOT = Get-Location
Write-Log "Project root assumed to be: $PROJECT_ROOT"

# 1. Log script start
Write-Log "Starting all tests script."

# 2. Dependency Checks
Write-Log "Performing dependency checks..."

# Docker version
Write-Log "Checking Docker version..."
try {
    $null = docker --version
    Write-Log "Docker installation found."
} catch {
    Write-Log "ERROR: Docker is not installed."
    exit 1
}

# Docker daemon running
Write-Log "Checking Docker daemon..."
try {
    $null = docker info
    Write-Log "Docker daemon is running."
} catch {
    Write-Log "ERROR: Docker daemon is not running. Please start Docker."
    exit 1
}

# Python version check
Write-Log "Checking Python version..."
try {
    $pythonVersion = python --version
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$Matches[1]
        if ($minorVersion -lt 10) {
            Write-Log "ERROR: Python version must be 3.10 or higher. Found: $pythonVersion"
            exit 1
        }
        Write-Log "Python version found: $pythonVersion"
    } else {
        Write-Log "ERROR: Python 3.x is not installed or not the default python. Found: $pythonVersion"
        exit 1
    }
} catch {
    Write-Log "ERROR: Python is not installed or not in PATH."
    exit 1
}

Write-Log "Basic dependency checks passed (Docker, Python 3.11)."

# 3. Manage PythonREST Virtual Environment at Project Root
Write-Log "Managing PythonREST virtual environment..."
$PYTHONREST_VENV_PATH = Join-Path $PROJECT_ROOT "venv"

if (-not (Test-Path $PYTHONREST_VENV_PATH)) {
    Write-Log "PythonREST virtual environment not found at $PYTHONREST_VENV_PATH. Creating..."
    try {
        python -m venv $PYTHONREST_VENV_PATH
        Write-Log "PythonREST virtual environment created at $PYTHONREST_VENV_PATH."
    } catch {
        Write-Log "ERROR: Failed to create PythonREST virtual environment at $PYTHONREST_VENV_PATH."
        exit 1
    }
} else {
    Write-Log "PythonREST virtual environment already exists at $PYTHONREST_VENV_PATH."
}

# Activate virtual environment
$VENV_ACTIVATE = Join-Path $PYTHONREST_VENV_PATH "Scripts\Activate.ps1"
Write-Log "Activating PythonREST virtual environment: $VENV_ACTIVATE"
try {
    & $VENV_ACTIVATE
    Write-Log "PythonREST virtual environment activated."
} catch {
    Write-Log "ERROR: Failed to activate virtual environment."
    exit 1
}

# Create a temporary log file in the project directory
$PIP_LOG_FILE = Join-Path $PROJECT_ROOT "pip_install.log"

Write-Log "Installing/updating PythonREST dependencies from $PROJECT_ROOT\requirements.txt..."
try {
    pip install -r (Join-Path $PROJECT_ROOT "requirements.txt") | Tee-Object -FilePath $PIP_LOG_FILE
    Write-Log "PythonREST dependencies installed/updated successfully from $PROJECT_ROOT\requirements.txt. Output logged to $PIP_LOG_FILE."
} catch {
    Write-Log "ERROR: Failed to install PythonREST dependencies from $PROJECT_ROOT\requirements.txt. See $PIP_LOG_FILE for details."
    Get-Content $PIP_LOG_FILE
    deactivate
    Write-Log "PythonREST virtual environment deactivated."
    exit 1
}

Write-Log "Deactivating PythonREST virtual environment (sub-scripts will reactivate as needed)."
deactivate
Write-Log "PythonREST virtual environment deactivated."

# 4. Execute Database Test Scripts
Write-Log "Proceeding to execute database-specific test scripts..."

# MySQL Tests
Write-Log "Starting MySQL tests..."
try {
    & (Join-Path $PROJECT_ROOT "tests\Databases\MySQL\test_mysql.ps1")
    Write-Log "MySQL tests completed successfully."
} catch {
    Write-Log "MySQL tests failed."
    exit 1
}

# PostgreSQL Tests
Write-Log "Starting PostgreSQL tests..."
try {
    & (Join-Path $PROJECT_ROOT "tests\Databases\PostgreSQL\test_postgresql.ps1")
    Write-Log "PostgreSQL tests completed successfully."
} catch {
    Write-Log "PostgreSQL tests failed."
    exit 1
}

# SQLServer Tests
Write-Log "Starting SQLServer tests..."
try {
    & (Join-Path $PROJECT_ROOT "tests\Databases\SQLServer\test_sqlserver.ps1")
    Write-Log "SQLServer tests completed successfully."
} catch {
    Write-Log "SQLServer tests failed."
    exit 1
}

# 5. All tests completed
Write-Log "All tests completed successfully!"

# 6. Log script end
Write-Log "All tests script finished." 