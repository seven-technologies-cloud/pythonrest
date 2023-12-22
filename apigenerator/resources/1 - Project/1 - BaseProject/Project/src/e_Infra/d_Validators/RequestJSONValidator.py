# Flask Imports #
from flask import request

# Handler Imports #
from src.e_Infra.a_Handlers.ApplicationExceptionClassHandler import *
from src.e_Infra.a_Handlers.SystemMessagesHandler import *

# Builder Imports #
from src.e_Infra.b_Builders.ProxyResponseBuilder import *


def validate_empty_request_json():
    if request.json is None or request.json == dict() or request.json == list():
        raise ApplicationException(
            build_proxy_response_insert_dumps(
                status_code=406,
                body={
                    get_system_message('error_message'): get_system_message('empty_json')
                }
            )
        )


def validate_invalid_request_json():
    if type(request.json) != dict and type(request.json) != list:
        raise ApplicationException(
            build_proxy_response_insert_dumps(
                status_code=406,
                body={
                    get_system_message('error_message'): get_system_message('malformed_input_data')
                }
            )
        )


def validate_invalid_items_in_request_json_array():
    if type(request.json) == list:
        for i in range(len(request.json)):
            if type(request.json[i]) != dict:
                raise ApplicationException(
                    build_proxy_response_insert_dumps(
                        status_code=406,
                        body={
                            get_system_message('error_message'): get_system_message('malformed_input_data')
                        }
                    )
                )


def validate_request_json():
    try:
        validate_empty_request_json()
        validate_invalid_request_json()
        validate_invalid_items_in_request_json_array()
    except ApplicationException as e:
        raise e
