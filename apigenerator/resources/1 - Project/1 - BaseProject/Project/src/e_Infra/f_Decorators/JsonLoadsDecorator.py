# System Imports #
from functools import wraps

# Flask Imports #
from flask import request

# Infra Imports #
from src.e_Infra.b_Builders.ProxyResponseBuilder import *
from src.e_Infra.a_Handlers.SystemMessagesHandler import *


def validate_json_loads_request_data(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            result = json.loads(request.data)
            if type(result) != dict and type(result) != list:
                raise Exception
        except Exception as e:
            del e
            return build_proxy_response_insert_dumps(
                401, {
                    get_system_message('error_message'): get_system_message('malformed_input_data')
                }
            )

        return f(*args, **kwargs)

    return wrapped
