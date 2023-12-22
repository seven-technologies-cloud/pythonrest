# System Imports #
from datetime import datetime

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *


# Method builds datetime format from system valid masks #
def build_date_time_from_sys_masks(timestamp):
    # Retrieving global datetime valid masks #
    valid_time_stamp_masks = get_global_variable('datetime_valid_masks').replace(' ', '').split(',')

    # Iterating over global datetime valid masks #
    for mask in valid_time_stamp_masks:
        try:
            result = datetime.strptime(timestamp, mask)
            return result
        except:
            continue
    return None
