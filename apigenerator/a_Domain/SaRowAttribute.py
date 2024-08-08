from parse import parse
from apigenerator.e_Enumerables.Enumerables import *


class SaRowAttribute:

    def __init__(self, row_attr, attr_type, is_primary_key, is_nullable,
                 is_foreign_key, has_default_value, default_value):
        self.row_attr = row_attr
        self.attr_type = attr_type
        self.is_primary_key = is_primary_key
        self.is_nullable = is_nullable
        self.is_foreign_key = is_foreign_key
        self.has_default_value = has_default_value
        self.default_value = default_value


def get_sa_row_attr_object(row_attr, attr_params):
    # Determine attribute type based on the attribute parameters
    attr_type = next((key for key, value_list in {
        'string': get_string_list(),
        'integer': get_integer_list(),
        'number': get_number_list(),
        'boolean': get_boolean_list(),
        'array': get_array_list(),
        'object': []  # default catch-all if no other type matches
    }.items() if ('sa.' not in attr_params[0]) or (list(parse('sa.{}', attr_params[0]))[0].split('(')[0] in value_list)), 'object')

    # Check attribute characteristics
    is_primary_key = any(
        'primary_key' in attr_param for attr_param in attr_params)
    is_nullable = not any(
        'nullable=False' in attr_param or is_primary_key for attr_param in attr_params)
    is_foreign_key = any(
        'ForeignKey' in attr_param for attr_param in attr_params)
    has_default_value = any(
        'default=' in attr_param and 'server_default=' not in attr_param for attr_param in attr_params)

    # Extract default value if present
    if has_default_value:
        default_value_param = next(
            attr_param for attr_param in attr_params if 'default=' in attr_param)
        parsed_value = list(parse('default={}', default_value_param.strip()))
        if parsed_value:
            default_value = parsed_value[0]
        else:
            default_value = None
    else:
        default_value = None

    # Create the attribute object
    attr_object = SaRowAttribute(row_attr, attr_type, is_primary_key, is_nullable,
                                 is_foreign_key, has_default_value, default_value)

    return attr_object
