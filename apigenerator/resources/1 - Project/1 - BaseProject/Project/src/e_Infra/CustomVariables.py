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

# Path to the OpenAPI specification file for the generated API
# This path is typically relative to the root of the generated project.
OPENAPI_SPEC_PATH = os.getenv('OPENAPI_SPEC_PATH', 'openapi.yaml')

# --- LLM Provider Configuration ---
# Specifies which LLM provider to use for the MCP /ask functionality.
# Expected values: "gemini", "openai", "anthropic".
# This MUST be set in the environment for the service to work.
LLM_PROVIDER = os.getenv('LLM_PROVIDER')

# API Key for OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# API Key for Anthropic
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# (Optional - for future use if specific model names are needed per provider)
# GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-pro')
# OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')
# ANTHROPIC_MODEL_NAME = os.getenv('ANTHROPIC_MODEL_NAME', 'claude-3-haiku-20240307')
