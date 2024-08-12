# Importing UUID module #
import uuid6


# Method that generates a random GUID / UUID #
def generate_guid():
    return str(uuid6.uuid7())


# Method that casts any parameter to string #
def stringify(param):
    return str(param)
