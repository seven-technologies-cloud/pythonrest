from flask import Flask
# Assuming a config.py file exists as per the structure: from app.main.config import config_by_name
# For this placeholder, we'll define a simple config if that import fails
try:
    from pythonrest.apigenerator.resources.app.main.config import config_by_name
except ImportError:
    # Fallback for environments where config might not be fully set up or named differently
    class BaseConfig:
        DEBUG = False
        # Add other common configs if needed
        GEMINI_API_KEY = None # To be loaded from environment or other config files
        SWAGGER_SPEC_PATH = "swagger.yaml" # Default path

    config_by_name = {
        "dev": BaseConfig,
        "prod": BaseConfig,
        # Add other environments as needed
    }
    # Ensure GEMINI_API_KEY and SWAGGER_SPEC_PATH are available
    # In a real app, these would be loaded from environment variables or secure configs
    import os
    config_by_name["dev"].GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    config_by_name["prod"].GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # SWAGGER_SPEC_PATH could also be an environment variable
    config_by_name["dev"].SWAGGER_SPEC_PATH = os.getenv("SWAGGER_SPEC_PATH", "swagger.yaml")
    config_by_name["prod"].SWAGGER_SPEC_PATH = os.getenv("SWAGGER_SPEC_PATH", "swagger.yaml")


# Import blueprints
# Assuming a default blueprint exists, e.g., app.api.default.routes
# from app.api.default.routes import bp as default_bp # Placeholder for actual default blueprint
# Import the new ask blueprint
try:
    # Path assuming 'pythonrest/apigenerator/resources/' is in PYTHONPATH
    from pythonrest.apigenerator.resources.app.api.ask import bp as ask_bp
except ImportError:
    # Fallback for local testing or different path configurations during generation
    try:
        from app.api.ask import bp as ask_bp
    except ImportError as e:
        # If this fails, it means the blueprint isn't found, which is an issue.
        # For the template, we'll let it pass, but a real app would need this.
        print(f"Warning: Could not import ask_bp: {e}")
        ask_bp = None # So app registration doesn't fail catastrophically here

def create_app(config_name: str = "dev"):
    """
    Creates and configures the Flask application.

    Args:
        config_name (str): The configuration environment (e.g., 'dev', 'prod').

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    selected_config = config_by_name.get(config_name)
    if not selected_config:
        print(f"Warning: Configuration '{config_name}' not found. Using default dev config.")
        selected_config = config_by_name.get("dev")

    app.config.from_object(selected_config)

    # Setup logging
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        # Example logging setup, adjust as needed
        file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    # Register blueprints
    # app.register_blueprint(default_bp, url_prefix='/api/default') # Example for a default blueprint

    if ask_bp:
        app.register_blueprint(ask_bp, url_prefix='/api') # Root prefix for /ask
    else:
        app.logger.warning("Ask blueprint (ask_bp) not registered as it could not be imported.")

    # Other app initializations (e.g., database, extensions) would go here

    return app

# Note: The import paths like 'pythonrest.apigenerator.resources.app.api.ask'
# are based on the assumption that 'pythonrest/apigenerator/resources/' directory
# will be part of the PYTHONPATH or the project root when the generated app runs.
# If the generation process alters the structure, these imports might need adjustment.
# The try-except blocks are to make the template more resilient if paths change
# or if it's used in an environment where the full structure isn't immediately available.
