def remove_keys_with_null_values(dictionary):
    keys_to_delete = list()
    for key in dictionary:
        if dictionary[key] is None:
            keys_to_delete.append(key)
    for key_to_delete in keys_to_delete:
        del dictionary[key_to_delete]


# Method builds a domain object from a dictionary #
def build_domain_object_from_dict(declarative_meta, dictionary):
    # Remove keys with null values #
    remove_keys_with_null_values(dictionary)
    # Assigning dictionary to __init__ class method #
    class_object = declarative_meta(**dictionary)
    # Returning construct object #
    return class_object


# Method builds an error message from an object and an exception error cause #
def build_object_error_message(object_from_body, validation_error):
    # Constructing empty dictionary object #
    error_dict = dict()
    # Populating body #
    error_dict['body'] = object_from_body
    # Populating error #
    error_dict['error'] = validation_error
    # Returning error object #
    return error_dict
