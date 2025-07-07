import os
import ast # For ast.literal_eval if used for other variables like ENDPOINTS from snippet

# Flask App Handler (Assuming this is where it's typically defined or imported)
# This is a placeholder. The actual app creation/import needs to be confirmed
# from your project's structure. For instance, it might be:
# from flask import Flask
# app_handler = Flask(__name__)
# Or imported from a factory if you use one:
# from src.app_factory import create_app # Example
# app_handler = create_app(os.getenv('FLASK_CONFIG') or 'default')

# For now, to avoid breaking if app_handler isn't the focus of this step:
app_handler = None
# TODO: Ensure 'app_handler' is correctly initialized with the Flask app instance.
# This might involve moving app instantiation here or importing it.


# --- LLM Configuration Variables ---

# This variable will decide which of the following model stacks will be used by default
# if not overridden by llm_config.json or X-Provider header.
SELECTED_LLM_PROVIDER = os.getenv("SELECTED_LLM_PROVIDER", "gemini").lower()

# --- Gemini (Google) Variables ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY_PLACEHOLDER")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
_gemini_temp_str = os.getenv("GEMINI_TEMPERATURE", "0.4")
try:
    GEMINI_TEMPERATURE = float(_gemini_temp_str)
except ValueError:
    logger.warning(f"Invalid GEMINI_TEMPERATURE '{_gemini_temp_str}'. Using default 0.4.")
    GEMINI_TEMPERATURE = 0.4
_gemini_max_tokens_str = os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048")
try:
    GEMINI_MAX_OUTPUT_TOKENS = int(_gemini_max_tokens_str)
except ValueError:
    logger.warning(f"Invalid GEMINI_MAX_OUTPUT_TOKENS '{_gemini_max_tokens_str}'. Using default 2048.")
    GEMINI_MAX_OUTPUT_TOKENS = 2048


# --- OpenAI Variables ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "OPENAI_API_KEY_PLACEHOLDER")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
_openai_temp_str = os.getenv("OPENAI_TEMPERATURE", "0.2")
try:
    OPENAI_TEMPERATURE = float(_openai_temp_str)
except ValueError:
    logger.warning(f"Invalid OPENAI_TEMPERATURE '{_openai_temp_str}'. Using default 0.2.")
    OPENAI_TEMPERATURE = 0.2
_openai_max_tokens_str = os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2000") # User snippet had 2000, typically 2048 or 4096
try:
    OPENAI_MAX_OUTPUT_TOKENS = int(_openai_max_tokens_str)
except ValueError:
    logger.warning(f"Invalid OPENAI_MAX_OUTPUT_TOKENS '{_openai_max_tokens_str}'. Using default 2000.")
    OPENAI_MAX_OUTPUT_TOKENS = 2000


# --- Anthropic Variables ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_PLACEHOLDER")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
_anthropic_temp_str = os.getenv("ANTHROPIC_TEMPERATURE", "0.7") # Best guess default
try:
    ANTHROPIC_TEMPERATURE = float(_anthropic_temp_str)
except ValueError:
    logger.warning(f"Invalid ANTHROPIC_TEMPERATURE '{_anthropic_temp_str}'. Using default 0.7.")
    ANTHROPIC_TEMPERATURE = 0.7
_anthropic_max_tokens_str = os.getenv("ANTHROPIC_MAX_OUTPUT_TOKENS", "2048") # Best guess default
try:
    ANTHROPIC_MAX_OUTPUT_TOKENS = int(_anthropic_max_tokens_str)
except ValueError:
    logger.warning(f"Invalid ANTHROPIC_MAX_OUTPUT_TOKENS '{_anthropic_max_tokens_str}'. Using default 2048.")
    ANTHROPIC_MAX_OUTPUT_TOKENS = 2048

# LLM_CONFIG_FILE_PATH is removed as llm_config.json is no longer used in this agent-based approach.

# --- Agent/Tools Specific Variables ---
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
# Ensure ast is imported if not already at the top of the file for ENDPOINTS
try:
    ENDPOINTS = ast.literal_eval(os.getenv("ENDPOINTS", "[]"))
    if not isinstance(ENDPOINTS, list):
        logger.warning(f"ENDPOINTS environment variable did not evaluate to a list (got {type(ENDPOINTS)}). Defaulting to empty list.")
        ENDPOINTS = []
except (ValueError, SyntaxError) as e:
    logger.error(f"Error parsing ENDPOINTS environment variable: {e}. Defaulting to empty list. Ensure it's a valid Python list string e.g., '[\"/api/v1/users\", \"/api/v1/items\"]'")
    ENDPOINTS = []


# --- Logging setup (basic, if not already handled elsewhere more centrally) ---
import logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__) # Logger for this file, used above for temp/token conversion warnings

# TODO: Review if app_handler is correctly defined/imported for your project.
# The Flask app instance is needed for blueprint registration in app.py.
# If app.py itself creates the app, then this file might not need to define app_handler,
# but app.py would import these config variables.
# If this file (EnvironmentVariables.py) is where the app instance is created or configured,
# ensure it's done correctly. The placeholder `app_handler = None` will cause issues
# if app.py relies on it being the Flask app.
# Based on app.py structure: `from src.e_Infra.g_Environment.EnvironmentVariables import *`
# it's likely app_handler IS expected to be defined here.
# A common pattern is:
# from flask import Flask
# app_handler = Flask(__name__)
# # ... then further app configurations ...
# And app.py would use this app_handler.
# For now, I'm keeping it as None and highlighting this as a critical point for the user to verify.

if app_handler is None:
    logger.critical("Flask 'app_handler' is not initialized in EnvironmentVariables.py! Blueprint registration will fail.")

# It's important that this file is imported early in your application's lifecycle,
# especially if 'app_handler' is defined here and used by app.py for blueprint registrations.
