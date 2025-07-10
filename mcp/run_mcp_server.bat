@echo off
REM Get the directory where this batch script is located
set SCRIPT_DIR=%~dp0

REM Construct the path to the activate script
set VENV_ACTIVATE=%SCRIPT_DIR%venv\Scripts\activate.bat

REM Define the relative path to the MCP server script for the mcp command
set MCP_SCRIPT_REL=mcp_servers/mcp_server.py

REM Activate the virtual environment
call "%VENV_ACTIVATE%"

REM Check if activation worked (optional: mcp command might fail otherwise)
where mcp >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: 'mcp' command not found after activating environment. Check installation.
    pause
    exit /b 1
)

REM Run the server using the 'mcp dev' command
echo "Starting MCP Server in DEV mode: %MCP_SCRIPT_REL%"
mcp dev "%MCP_SCRIPT_REL%"

REM The server process will keep running, so no 'pause' is typically needed here.