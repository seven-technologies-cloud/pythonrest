# PythonREST Test Automation Scripts

This directory contains scripts to automate the testing of PythonREST against different database systems: MySQL, PostgreSQL, and SQLServer.

## Prerequisites

Before running the main test script, ensure you have the following installed and configured on your system:

1.  **Docker**: The scripts use Docker and Docker Compose to set up database instances. Ensure Docker is installed and the Docker daemon is running.
    *   [Install Docker](https://docs.docker.com/get-docker/)
2.  **Python 3.11**: The API generation and execution rely on Python 3.11.
    *   [Install Python](https://www.python.org/downloads/)

## IF RUNNING LOCALLY
- Always remember to delete the PythonRestAPI after running one db test to then run another one
- When running a test, you end up at the ps1 file of that database folder, to go back to project root, just run `Set-Location ..\..\..\`

## Individual Database Test Scripts

To run each database script, call the test script from root folder:

```powershell
.\tests\Databases\MySQL\test_mysql.ps1
```

```powershell
.\tests\Databases\PostgreSQL\test_postgresql.ps1
```

```powershell
.\tests\Databases\SQLServer\test_sqlserver.ps1
```

When running these scripts directly, ensure prerequisites are met and Docker is running. The individual scripts also expect the shared PythonREST virtual environment at `./venv` (relative to project root) to be set up and populated as they will activate it for running `pythonrest.py`.

## TBD
- When all data types of sqlserver have been validated to not fix errors on API generation, uncomment commented tables on the database_mapper_sqlserver.sql for a more thorough test
- Tests will only go up to the point of validating the API is running and main Swagger route is accessible, tests of GET POST PATCH PUT DELETE on the generated API routes must be added in the future for checking if changes did not break any functionality
- It is unknown whether any of the .sh versions of the tests work. This must be checked and fixed if necessary
- Each test will need to include a check to ensure that Docker is running and that the shared PythonREST virtual environment located at ./venv in the project root is properly set up
- Running these tests inside a pipeline that runs when a PR is created/a commit is added to a PR

## Logging

Detailed logs for API server outputs, PythonREST generation, and dependency installations are temporarily stored in `/tmp/` during script execution (e.g., `/tmp/api_output_mysql.log`, `/tmp/pythonrest_generate_mysql.log`, etc.) and are not cleaned up by these scripts, allowing for post-run inspection if needed.
