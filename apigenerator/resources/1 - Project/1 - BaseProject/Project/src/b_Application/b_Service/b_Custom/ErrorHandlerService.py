# Flask Imports #
from flask import request

# Handler Imports #
from src.e_Infra.a_Handlers.SystemMessagesHandler import *

# Builder Imports #
from src.e_Infra.b_Builders.ProxyResponseBuilder import *


def build_error_response(error):
    return build_proxy_response_insert_dumps(
        status_code='400',
        body=
        {
            get_system_message('error_message'): error
        }
    )


def print_user_request_on_error():
    user_request = {
        "UrlParams": request.args.to_dict(),
        "Payload": request.data,
        "Headers": dict(request.headers)
    }
    print(json.dumps(user_request, default=str))
