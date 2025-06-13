#!/bin/bash

# Function to log messages with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Exit on error
set -e

# 0. Define Project Root (assuming script is run from project root)
PROJECT_ROOT=$(pwd)
log "Project root assumed to be: $PROJECT_ROOT"

# 1. Log script start
log "Starting all tests script."

# 2. Dependency Checks
log "Performing dependency checks..."

# Docker version
log "Checking Docker version..."
if ! docker --version > /dev/null 2>&1; then
    log "ERROR: Docker is not installed."
    exit 1
fi
log "Docker installation found."

# Docker daemon running
log "Checking Docker daemon..."
if ! docker info > /dev/null 2>&1; then
    log "ERROR: Docker daemon is not running. Please start Docker."
    exit 1
fi
log "Docker daemon is running."

# Python version check
log "Checking Python version..."
PYTHON_VERSION_OUTPUT=$(python3 --version 2>&1)
if ! [[ "$PYTHON_VERSION_OUTPUT" =~ Python\ 3\.([0-9]+) ]]; then
    log "ERROR: Python 3.x is not installed or not the default python3. Found: $PYTHON_VERSION_OUTPUT"
    exit 1
fi
PYTHON_MINOR_VERSION=${BASH_REMATCH[1]}
if [ "$PYTHON_MINOR_VERSION" -lt 10 ]; then
    log "ERROR: Python version must be 3.10 or higher. Found: $PYTHON_VERSION_OUTPUT"
    exit 1
fi
log "Python version found: $PYTHON_VERSION_OUTPUT"

log "Basic dependency checks passed (Docker, Python 3.11)."

# 3. Manage PythonREST Virtual Environment at Project Root
log "Managing PythonREST virtual environment..."
PYTHONREST_VENV_PATH="$PROJECT_ROOT/venv"

if [ ! -d "$PYTHONREST_VENV_PATH" ]; then
    log "PythonREST virtual environment not found at $PYTHONREST_VENV_PATH. Creating..."
    if ! python3 -m venv "$PYTHONREST_VENV_PATH"; then
        log "ERROR: Failed to create PythonREST virtual environment at $PYTHONREST_VENV_PATH."
        exit 1
    fi
    log "PythonREST virtual environment created at $PYTHONREST_VENV_PATH."
else
    log "PythonREST virtual environment already exists at $PYTHONREST_VENV_PATH."
fi

# Detect OS and set appropriate paths
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_ACTIVATE="$PYTHONREST_VENV_PATH/Scripts/activate"
    PIP_CMD="$PYTHONREST_VENV_PATH/Scripts/pip.exe"
else
    VENV_ACTIVATE="$PYTHONREST_VENV_PATH/bin/activate"
    PIP_CMD="$PYTHONREST_VENV_PATH/bin/pip"
fi

log "Activating PythonREST virtual environment: $VENV_ACTIVATE"
# shellcheck source=/dev/null
source "$VENV_ACTIVATE"
log "PythonREST virtual environment activated."

# Create a temporary log file in the project directory
PIP_LOG_FILE="$PROJECT_ROOT/pip_install.log"

log "Installing/updating PythonREST dependencies from $PROJECT_ROOT/requirements.txt..."
if ! "$PIP_CMD" install -r "$PROJECT_ROOT/requirements.txt" > "$PIP_LOG_FILE" 2>&1; then
    log "ERROR: Failed to install PythonREST dependencies from $PROJECT_ROOT/requirements.txt. See $PIP_LOG_FILE for details."
    cat "$PIP_LOG_FILE"
    deactivate
    log "PythonREST virtual environment deactivated."
    exit 1
fi
log "PythonREST dependencies installed/updated successfully from $PROJECT_ROOT/requirements.txt. Output logged to $PIP_LOG_FILE."

log "Deactivating PythonREST virtual environment (sub-scripts will reactivate as needed)."
deactivate
log "PythonREST virtual environment deactivated."

# 4. Execute Database Test Scripts
log "Proceeding to execute database-specific test scripts..."

# MySQL Tests
log "Starting MySQL tests..."
if ! bash tests/Databases/MySQL/test_mysql.sh; then
    log "MySQL tests failed."
    exit 1
fi
log "MySQL tests completed successfully."

# PostgreSQL Tests
log "Starting PostgreSQL tests..."
if ! bash tests/Databases/PostgreSQL/test_postgresql.sh; then
    log "PostgreSQL tests failed."
    exit 1
fi
log "PostgreSQL tests completed successfully."

# SQLServer Tests
log "Starting SQLServer tests..."
if ! bash tests/Databases/SQLServer/test_sqlserver.sh; then
    log "SQLServer tests failed."
    exit 1
fi
log "SQLServer tests completed successfully."

# 5. All tests completed
log "All tests completed successfully!"

# 6. Log script end
log "All tests script finished."

exit 0
