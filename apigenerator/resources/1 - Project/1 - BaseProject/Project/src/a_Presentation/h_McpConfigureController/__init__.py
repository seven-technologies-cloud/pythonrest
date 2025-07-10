# This file makes 'h_McpConfigureController' a Python package.

from flask import Blueprint

# Define the Blueprint for MCP configuration routes
# The URL prefix will be set when registering with the app, e.g., /mcp
mcp_configure_bp = Blueprint('mcp_configure_bp', __name__)

# Import routes after blueprint definition to avoid circular dependencies if routes use the bp
from . import ConfigureController
