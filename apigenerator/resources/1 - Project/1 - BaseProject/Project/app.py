from src.a_Presentation.h_McpConfigureController.ConfigureController import mcp_configure_bp
# Infra Imports #
from src.e_Infra.g_Environment.EnvironmentVariables import *

# Controller Imports #
from src.a_Presentation.d_Swagger.SwaggerController import *
from src.a_Presentation.f_Redoc.RedocController import *
from src.a_Presentation.b_Custom.FlaskAdminPanelController import *
from src.a_Presentation.b_Custom.OptionsController import *
from src.a_Presentation.b_Custom.SQLController import *
from src.a_Presentation.b_Custom.BeforeRequestController import *
from src.a_Presentation.b_Custom.ExceptionHandlerController import *
from src.a_Presentation.g_McpController.AskController import ask_bp

# Registering MCP Blueprints
# Assuming 'app_handler' is the Flask app instance from 'EnvironmentVariables.py'
# If 'app_handler' is not the app, or if blueprint registration is centralized elsewhere
# (e.g. inside EnvironmentVariables.py or a factory function), this will need adjustment.
if 'app_handler' in globals() and hasattr(app_handler, 'register_blueprint'):
    app_handler.register_blueprint(ask_bp, url_prefix='/mcp') # for /mcp/ask
    print("INFO: MCP blueprint 'ask_bp' (for /mcp/ask route) registered under /mcp prefix.")
    app_handler.register_blueprint(mcp_configure_bp, url_prefix='/mcp') # for /mcp/ask/configure
    print("INFO: MCP blueprint 'mcp_configure_bp' (for /mcp/ask/configure route) registered under /mcp prefix.")
else:
    # Fallback or warning if app_handler is not found as expected.
    # This indicates a potential misunderstanding of how the app object is exposed.
    # In a real scenario, one would need to trace where 'app_handler' is defined
    # and how blueprints are meant to be registered.
    print("WARNING: Flask app object 'app_handler' not found or does not support 'register_blueprint'. MCP blueprints not registered.")


# LocalHost run #
if __name__ == "__main__":
    app_handler.run(debug=True, use_reloader=False)