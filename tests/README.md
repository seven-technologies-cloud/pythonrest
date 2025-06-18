# PythonREST Test Automation Scripts

This directory contains scripts to automate the testing of PythonREST against different database systems: MySQL, PostgreSQL, and SQLServer.

## Prerequisites

Before running the main test script, ensure you have the following installed and configured on your system:

1.  **Docker**: The scripts use Docker and Docker Compose to set up database instances. Ensure Docker is installed and the Docker daemon is running.
    *   [Install Docker](https://docs.docker.com/get-docker/)
2.  **Python 3.11**: The API generation and execution rely on Python 3.11.
    *   [Install Python](https://www.python.org/downloads/)

## Running All Tests

The main script `run_all_tests.sh` orchestrates the entire testing process. It performs basic dependency checks (Docker, Python 3.11) and then runs individual test suites for each database.

To execute all tests:

1.  Navigate to the root of the repository. This script must be run from the root directory of the PythonREST repository.
2.  Ensure the script has execute permissions:
    ```bash
    chmod +x tests/run_all_tests.sh
    ```
    (This should already be set if you pulled the latest changes including this script).
3.  Run the script:
    ```bash
    bash tests/run_all_tests.sh
    ```
    The script will use a Python virtual environment located at `./venv` (relative to the project root) for PythonREST. It will attempt to create this virtual environment if it doesn't exist and will install or update dependencies from `./requirements.txt` within it.

The script will output logs for each step, indicating the progress and success or failure of each database test. If any dependency check or test fails, the script will exit with an error message.

## Individual Database Test Scripts

While `run_all_tests.sh` is the recommended way, individual scripts can be run from the project root for debugging if needed:

For example, to run only the MySQL tests from the project root:
```bash
bash tests/Databases/MySQL/test_mysql.sh
```
When running these scripts directly, ensure prerequisites are met and Docker is running. The individual scripts also expect the shared PythonREST virtual environment at `./venv` (relative to project root) to be set up and populated as they will activate it for running `pythonrest.py`.

## Logging

Each script generates logs to standard output, prefixed with timestamps. The main script `run_all_tests.sh` will indicate which database's tests are currently running. Detailed logs for API server outputs, PythonREST generation, and dependency installations are temporarily stored in `/tmp/` during script execution (e.g., `/tmp/api_output_mysql.log`, `/tmp/pythonrest_generate_mysql.log`, etc.) and are not cleaned up by these scripts, allowing for post-run inspection if needed.
