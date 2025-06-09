# System Imports #
import os
# import json # Removed as it's not used


# Method for getting a global variable by its name #
def get_global_variable(variable_name):
    """
    Retrieves an environment variable by its name.
    Returns the value of the variable, or None if not found.
    """
    return os.environ.get(variable_name)
