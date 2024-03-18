# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.e_Infra.GlobalVariablesManager import *

# Flask imports #
from flask import request


@app_handler.after_request
def apply_caching(response):
    if request.method == 'OPTIONS':
        response.headers["Access-Control-Allow-Origin"] = get_global_variable('origins')
        response.headers["Access-Control-Allow-Headers"] = get_global_variable('headers')
        response.headers["Access-Control-Allow-Methods"] = response.allow
        response.content_type = 'application/json'
        response.mimetype = 'application/json'
        response.status_code = 200
        response.data = b'{"Message": "Success"}'
        response.response = list(response.data)
    else:
        response.headers["Access-Control-Allow-Origin"] = get_global_variable('origins')
        response.headers["Access-Control-Allow-Headers"] = get_global_variable('headers')
    return response
