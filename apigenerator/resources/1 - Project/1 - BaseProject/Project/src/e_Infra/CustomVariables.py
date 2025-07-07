import os

# Method returns a definition of an empty python dictionary #
def get_system_null():
    return None


# Method returns a definition of an empty python dictionary #
def get_system_empty_dict():
    return {}


# Method returns a definition of an empty python dictionary cast to string #
def get_system_empty_dict_str():
    return '{}'


# Method returns a definition of an empty python list #
def get_system_empty_list():
    return []


# Method returns a definition of an empty python list cast to string #
def get_system_empty_list_str():
    return '[]'

# Gemini API Key for MCP functionality
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- LLM Provider Configuration ---

# --- Core API Keys (set via environment variables) ---
# These are essential and should not be changed by the /configure API.
# GEMINI_API_KEY is already defined above.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# --- Initial Default Settings (set via environment variables, can be overridden by llm_config.json) ---
# Specifies the system-wide default LLM provider if not overridden by runtime configuration.
# Expected values: "gemini", "openai", "anthropic".
ENV_DEFAULT_LLM_PROVIDER = os.getenv('ENV_DEFAULT_LLM_PROVIDER') # No app-level default, must be configured if no runtime default.

# Default model names for each provider (can be overridden by runtime config or service defaults)
ENV_DEFAULT_GEMINI_MODEL_NAME = os.getenv('ENV_DEFAULT_GEMINI_MODEL_NAME') # e.g., 'gemini-pro'
ENV_DEFAULT_OPENAI_MODEL_NAME = os.getenv('ENV_DEFAULT_OPENAI_MODEL_NAME') # e.g., 'gpt-3.5-turbo'
ENV_DEFAULT_ANTHROPIC_MODEL_NAME = os.getenv('ENV_DEFAULT_ANTHROPIC_MODEL_NAME') # e.g., 'claude-3-haiku-20240307'

# Default temperature settings for each provider (can be overridden by runtime config or service defaults)
# Temperature is usually a float (e.g., 0.7). os.getenv returns string, so conversion is needed where used.
ENV_DEFAULT_GEMINI_TEMPERATURE = os.getenv('ENV_DEFAULT_GEMINI_TEMPERATURE')
ENV_DEFAULT_OPENAI_TEMPERATURE = os.getenv('ENV_DEFAULT_OPENAI_TEMPERATURE')
ENV_DEFAULT_ANTHROPIC_TEMPERATURE = os.getenv('ENV_DEFAULT_ANTHROPIC_TEMPERATURE')

# --- Runtime Configuration File ---
# Path to the JSON file that stores dynamic LLM configurations set via the API.
LLM_CONFIG_FILE_PATH = os.getenv('LLM_CONFIG_FILE_PATH', 'llm_config.json')
