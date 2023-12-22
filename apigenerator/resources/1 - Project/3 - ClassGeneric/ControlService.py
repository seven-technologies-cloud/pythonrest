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


# Method retrieves Control domain objects by given id and request_args params #
def get_control_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=Control,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=id_name_list,
        header_args=header_args
    )


# Method inserts Control domain objects #
def post_control_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=Control
    )


# Method updates Control domain objects #
def patch_control_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=Control,
        id_name_list=id_name_list
    )


# Method inserts and/or updates Control domain objects #
def put_control_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=Control,
        id_name_list=id_name_list
    )


# Method deletes Control domain object #
def delete_control_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=Control
    )


# Method deletes Control domain objects by given id params #
def delete_control_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=Control,
        id_value_list=id_value_list,
        id_name_list=id_name_list
    )
