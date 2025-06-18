#!/bin/bash

# Function to log messages with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Exit on error
set -e

# Function to handle deactivation of PythonREST venv on exit
cleanup_pythonrest_venv() {
    if [ -n "$PYTHONREST_VENV_ACTIVATED" ]; then
        log "Deactivating PythonREST virtual environment due to script exit..."
        deactivate
        log "PythonREST virtual environment deactivated."
        unset PYTHONREST_VENV_ACTIVATED
    fi
}
# Trap EXIT signal to ensure PythonREST venv is deactivated
trap cleanup_pythonrest_venv EXIT

# 0. Determine Project Root and Script Directory
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../../" && pwd)
log "Script directory: $SCRIPT_DIR"
log "Project root: $PROJECT_ROOT"

# Change to script's directory for local operations (like docker-compose)
cd "$SCRIPT_DIR" || exit
log "Changed directory to $(pwd) for local operations."

# 1. Log script start
log "Starting MySQL integration test script."

# 2. Start MySQL Docker container
log "Starting MySQL Docker container..."
docker-compose up -d
if [ $? -ne 0 ]; then
    log "ERROR: Failed to start MySQL Docker container."
    exit 1 # Trap will handle venv deactivation if it was activated
fi
log "MySQL Docker container started."

# 3. Wait for MySQL container to be healthy
MYSQL_CONTAINER_NAME="pythonrest-mysql-1" # Adjust if your container name is different in docker-compose.yml
log "Waiting for MySQL container ($MYSQL_CONTAINER_NAME) to be healthy..."
TIMEOUT_SECONDS=120
SECONDS_WAITED=0
while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $MYSQL_CONTAINER_NAME 2>/dev/null || echo "checking")
    if [ "$STATUS" == "healthy" ]; then
        log "MySQL container is healthy."
        break
    fi
    if [ "$STATUS" == "unhealthy" ]; then
        log "ERROR: MySQL container is unhealthy. Exiting."
        docker-compose logs $MYSQL_CONTAINER_NAME
        docker-compose down
        exit 1 # Trap will handle venv deactivation
    fi
    if [ $SECONDS_WAITED -ge $TIMEOUT_SECONDS ]; then
        log "ERROR: Timeout waiting for MySQL container to become healthy. Last status: $STATUS. Exiting."
        docker-compose logs $MYSQL_CONTAINER_NAME
        docker-compose down
        exit 1 # Trap will handle venv deactivation
    fi
    sleep 5
    SECONDS_WAITED=$((SECONDS_WAITED + 5))
    log "Still waiting for MySQL container... ($SECONDS_WAITED/$TIMEOUT_SECONDS seconds)"
done

# 4. Activate Shared PythonREST Venv
log "Activating shared PythonREST virtual environment: $PROJECT_ROOT/venv/bin/activate"
if [ ! -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    log "ERROR: PythonREST venv activate script not found at $PROJECT_ROOT/venv/bin/activate"
    docker-compose down
    exit 1 # Trap will handle venv deactivation if it was activated (though unlikely here)
fi
# shellcheck source=/dev/null
source "$PROJECT_ROOT/venv/bin/activate"
PYTHONREST_VENV_ACTIVATED=true # Mark as activated for trap
log "Shared PythonREST virtual environment activated."

# 5. Run PythonREST generation
log "Running PythonREST generation using $PROJECT_ROOT/pythonrest.py..."
python "$PROJECT_ROOT/pythonrest.py" generate --mysql-connection-string mysql://admin:adminuserdb@localhost:3306/database_mapper_mysql > /tmp/pythonrest_generate_mysql.log 2>&1
GENERATION_STATUS=$?
if [ $GENERATION_STATUS -ne 0 ]; then
    log "ERROR: PythonREST generation failed. See /tmp/pythonrest_generate_mysql.log for details."
    cat /tmp/pythonrest_generate_mysql.log
    # Deactivation will be handled by trap
    docker-compose down
    exit 1
fi
log "PythonREST generation output logged to /tmp/pythonrest_generate_mysql.log."

# 6. Log PythonREST generation status and check for generated_api folder
# generated_api folder will be created in the current directory ($SCRIPT_DIR)
if [ ! -d "generated_api" ]; then
    log "ERROR: 'generated_api' folder not found in $SCRIPT_DIR after PythonREST generation."
    # Deactivation will be handled by trap
    docker-compose down
    exit 1
fi
log "PythonREST generation successful. 'generated_api' folder found in $SCRIPT_DIR."

# 7. Change directory to generated_api
cd generated_api || exit
log "Changed directory to $(pwd)."

# 8. Create Python virtual environment for the generated API
log "Creating Python virtual environment for generated API..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    log "ERROR: Failed to create Python virtual environment for generated API."
    cd .. # Back to $SCRIPT_DIR
    # Deactivation of PythonREST venv will be handled by trap
    docker-compose down
    exit 1
fi
log "Python virtual environment for generated API created."

# 9. Activate virtual environment for the generated API
log "Activating virtual environment for generated API..."
# shellcheck source=/dev/null
source venv/bin/activate
log "Virtual environment for generated API activated."

# 10. Install dependencies for the generated API
log "Installing dependencies from requirements.txt for generated API..."
pip install -r requirements.txt > /tmp/pip_install_mysql_api.log 2>&1
INSTALL_STATUS=$?
if [ $INSTALL_STATUS -ne 0 ]; then
    log "ERROR: Failed to install dependencies for generated API. See /tmp/pip_install_mysql_api.log for details."
    cat /tmp/pip_install_mysql_api.log
    deactivate # Deactivate generated API venv
    log "Virtual environment for generated API deactivated."
    cd .. # Back to $SCRIPT_DIR
    # Deactivation of PythonREST venv will be handled by trap
    docker-compose down
    exit 1
fi
log "Dependencies for generated API installed successfully. Output logged to /tmp/pip_install_mysql_api.log."

# 11. Start the Flask API in the background
log "Starting Flask API in the background..."
python app.py > /tmp/api_output_mysql.log 2>&1 &
API_PID=$!
log "Flask API started with PID $API_PID. Output logged to /tmp/api_output_mysql.log."

# 12. Wait for API to start and check
log "Waiting for API to start (5 seconds)..."
sleep 5
curl -f http://localhost:5000 > /tmp/curl_check_mysql.log 2>&1
CURL_STATUS=$?
if [ $CURL_STATUS -ne 0 ]; then
    log "ERROR: API failed to start or is not responding. Curl check failed. See /tmp/curl_check_mysql.log."
    cat /tmp/curl_check_mysql.log
    log "API logs (/tmp/api_output_mysql.log):"
    cat /tmp/api_output_mysql.log
    kill $API_PID
    deactivate # Deactivate generated API venv
    log "Virtual environment for generated API deactivated."
    cd .. # Back to $SCRIPT_DIR
    # Deactivation of PythonREST venv will be handled by trap
    docker-compose down
    exit 1
fi
log "API started and responding."
rm /tmp/curl_check_mysql.log # Clean up successful check log

# 13. Perform a sample curl GET request
log "Performing sample GET request to http://localhost:5000/ (actual table endpoint might differ)..."
curl http://localhost:5000/ > /tmp/curl_test_mysql.log 2>&1
if [ $? -ne 0 ]; then
    log "WARNING: Sample curl GET request failed. This might indicate an issue or no default route. See /tmp/curl_test_mysql.log."
    cat /tmp/curl_test_mysql.log
else
    log "Sample curl GET request successful. Response logged to /tmp/curl_test_mysql.log."
fi

# 14. Kill the Flask API process
log "Killing Flask API (PID $API_PID)..."
kill $API_PID
wait $API_PID 2>/dev/null # Suppress "Terminated" message
log "Flask API process killed."

# 15. Deactivate virtual environment for the generated API
log "Deactivating virtual environment for generated API..."
deactivate
log "Virtual environment for generated API deactivated."

# 16. Change directory back to $SCRIPT_DIR
cd ..
log "Changed directory to $(pwd)."

# 17. Deactivate Shared PythonREST Venv (explicitly, trap will also try but that's fine)
log "Deactivating shared PythonREST virtual environment (explicitly)..."
deactivate
PYTHONREST_VENV_ACTIVATED=false # Mark as explicitly deactivated
log "Shared PythonREST virtual environment deactivated."

# 18. Stop and remove Docker container
log "Stopping and removing MySQL Docker container..."
docker-compose down
if [ $? -ne 0 ]; then
    log "WARNING: docker-compose down command failed. Manual cleanup might be required."
fi
log "MySQL Docker container stopped and removed."

# 19. Log script completion
# Unset trap before successful exit to avoid double deactivation message if it was already explicitly done
trap - EXIT
log "MySQL integration test script completed successfully."
exit 0