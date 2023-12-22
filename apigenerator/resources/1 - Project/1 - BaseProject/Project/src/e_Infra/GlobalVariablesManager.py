# System Imports #
import os
import json


# Method for getting a global variable by its name #
def get_global_variable(variable_name):
    try:
        return os.environ[variable_name] if os.environ[variable_name] is not None else None
    except Exception:
        return None
