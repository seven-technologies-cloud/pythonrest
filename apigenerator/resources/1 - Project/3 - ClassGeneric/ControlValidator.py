# Infra Imports #
from src.e_Infra.CustomVariables import *


# Method validates Control domain attributes from a Control API request item #
def validate_control(control_item):
    # Defining error list to be returned #
    error_list = get_system_empty_list()

    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # return error list if vot valid #
    if error_list == get_system_empty_list():
        return None
    else:
        raise Exception(error_list)
