# Importing UUID module #
import os
import uuid6
import datetime
from ulid import ULID


# Method that generates a random GUID / UUID / ULID #
def generate_guid():
    # lambda expressions are used below because the functions will only be executed if the ID is actually needed, as
    # opposed to being executed when the dictionary is defined. Also, everytime the dictionary is accessed, a new id is
    # generated, as opposed to storing the same precomputed one.
    id_generators = {
        'ulid': lambda: str(ULID.from_datetime(datetime.datetime.now())),
        'uuid': lambda: str(uuid6.uuid7()),
    }
    # tries to get environment variable, otherwise defaults to uuid
    id_generation_method = os.environ.get('id_generation_method', 'uuid')
    # tries to get the key of the variable, otherwise defaults to getting the uuid key
    return id_generators.get(id_generation_method, id_generators['uuid'])()


def generate_uuidv7():
    return str(uuid6.uuid7())


# Method that casts any parameter to string #
def stringify(param):
    return str(param)
