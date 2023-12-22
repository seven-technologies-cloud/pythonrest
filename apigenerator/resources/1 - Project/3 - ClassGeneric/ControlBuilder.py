# Domain Imports #
from src.c_Domain.Control import *
from sqlalchemy import inspect

# Builder Imports #
from src.e_Infra.b_Builders.StringBuilder import *
from src.e_Infra.b_Builders.DomainBuilder import *


# Method builds a Control instance from an incoming API body request object #
def build_control_from_request_body(control_from_body):

    # Initializing new Control instance from generic builder #
    control = build_domain_object_from_dict(Control, control_from_body)

    ins = inspect(Control)
    for column in ins.tables[0].columns:
        if column.primary_key:
            if column.name not in control_from_body:
                if str(column.type) == 'CHAR(36)':
                    exec(('control.{} = generate_guid()'.format(column.name)))

    # Returning assembled Control object #
    return control
