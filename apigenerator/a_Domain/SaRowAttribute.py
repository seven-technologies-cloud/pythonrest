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
    if list(parse('sa.{}', attr_params[0]))[0].split('(')[0] in get_string_list():
        # --------------------- OBJECT ATTR --------------------- #
        attr_type = 'string'
    elif list(parse('sa.{}', attr_params[0]))[0].split('(')[0] in get_integer_list():
        # --------------------- OBJECT ATTR --------------------- #
        attr_type = 'integer'
    elif list(parse('sa.{}', attr_params[0]))[0].split('(')[0] in get_number_list():
        # --------------------- OBJECT ATTR --------------------- #
        attr_type = 'number'
    elif list(parse('sa.{}', attr_params[0]))[0].split('(')[0] in get_boolean_list():
        # --------------------- OBJECT ATTR --------------------- #
        attr_type = 'boolean'
    elif list(parse('sa.{}', attr_params[0]))[0].split('(')[0] in get_array_list():
        # --------------------- OBJECT ATTR --------------------- #
        attr_type = 'array'
    else:
        # --------------------- OBJECT ATTR --------------------- #
        attr_type = 'object'

    is_primary_key = next((True for attr_param in attr_params if 'primary_key' in attr_param), False)

    is_nullable = next((False for attr_param in attr_params if 'nullable=False' in attr_param or is_primary_key), True)

    is_foreign_key = next((True for attr_param in attr_params if 'ForeignKey' in attr_param), False)

    has_default_value = next((True for attr_param in attr_params if 'default=' in attr_param), False)

    default_value = next((list(parse('default={}', attr_param.strip()))[0]
                          for attr_param in attr_params if has_default_value and 'default=' in attr_param), None)

    exec('default_value = {}'.format(default_value))

    attr_object = SaRowAttribute(row_attr, attr_type, is_primary_key, is_nullable,
                                 is_foreign_key, has_default_value, default_value)

    return attr_object
