# FastMCP with Database Integration

This project provides a FastMCP server with automatic database detection and integration.

## Running the Server

1. Activate the virtual environment and install the requirements:
   ```
   python -m venv venv
   ```
   Then:
   ```
   venv\Scripts\activate
   ```
   And:
   ```
   pip install -r requirements.txt
   ```
2. Start the agent (can also be the Ollama or the OpenAI):
   ```
   python python agent/main-google-ai.py
   ```
3. The server will automatically detect and connect to an available database

## Available Tools

- `get_database_tables_tool`: Gets all tables from the database with their column information and sample data
