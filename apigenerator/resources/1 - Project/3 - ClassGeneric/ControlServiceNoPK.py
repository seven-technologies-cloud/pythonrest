# Domain Imports #
from src.c_Domain.Control import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves Control domain objects by given request_args param #
def get_control_set(request_args, header_args):
    return get_all(
        declarative_meta=Control,
        request_args=request_args,
        header_args=header_args
    )


# Method inserts Control domain objects #
def post_control_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=Control
    )


# Method deletes Control domain object #
def delete_control_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=Control
    )
