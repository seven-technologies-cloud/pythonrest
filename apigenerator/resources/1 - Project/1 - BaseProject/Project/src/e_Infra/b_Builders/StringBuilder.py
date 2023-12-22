# Importing UUID module #
import uuid


# Method that generates a random GUID / UUID #
def generate_guid():
    return str(uuid.uuid4())


# Method that casts any parameter to string #
def stringify(param):
    return str(param)
