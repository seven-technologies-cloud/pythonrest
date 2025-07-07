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

# Any other non-LLM-related custom variables defined by the framework/user would remain here.
# All LLM-related configurations (API keys, default provider, models, temperatures, llm_config.json path)
# are now managed in src.e_Infra.g_Environment.EnvironmentVariables.py
