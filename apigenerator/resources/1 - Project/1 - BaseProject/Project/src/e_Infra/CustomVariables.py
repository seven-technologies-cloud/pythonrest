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
