# System Imports #
import json

# Flask Imports #
from flask import request

# Handler Imports #
from src.e_Infra.a_Handlers.ApplicationExceptionClassHandler import *
from src.e_Infra.a_Handlers.SystemMessagesHandler import *
from src.e_Infra.a_Handlers.ExceptionsHandler import *


def print_user_request():
    try:
        json_payload = request.json if request.content_type == 'application/json' else None
    except Exception as e:
        del e
        raise ApplicationException(build_proxy_response_insert_dumps(
            status_code=406,
            body={
                get_system_message('error_message'): get_system_message('malformed_input_data')
            }
        )
        )
    user_request = {
        "UrlParams": request.args.to_dict(),
        "JsonPayload": json_payload,
        "Headers": dict(request.headers)
    }
    print(json.dumps(user_request, default=str))
