# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.e_Infra.GlobalVariablesManager import *

# Service Imports #
from src.b_Application.b_Service.b_Custom.ErrorHandlerService import build_error_response

# Flask imports #
from flask import request


@app_handler.after_request
def apply_caching(response):
    if request.method == 'OPTIONS':
        origin = request.headers.get("Origin")
        origins = get_global_variable("origins")

        if origin and origins:
            if origins.strip() == "*":
                response.headers["Access-Control-Allow-Origin"] = origin
            else:
                # Normalize origins by removing trailing slashes for comparison
                normalized_origin = origin.rstrip('/')
                allowed_origins = [o.strip().rstrip('/') for o in origins.split(",")]
                if normalized_origin in allowed_origins:
                    response.headers["Access-Control-Allow-Origin"] = origin
                else:
                    response = build_error_response(f"Access to fetch from origin {origin} has been blocked by CORS policy")
                    return response
        else:
            # Don't set CORS headers if no origin or origins not configured
            pass

        response.headers["Access-Control-Allow-Headers"] = get_global_variable('headers')
        response.headers["Access-Control-Allow-Methods"] = response.allow
        response.content_type = 'application/json'
        response.mimetype = 'application/json'
        response.status_code = 200
        response.data = b'{"Message": "Success"}'
        response.response = list(response.data)
    else:
        # For non-OPTIONS requests, handle CORS properly
        origin = request.headers.get("Origin")
        origins = get_global_variable("origins")
        
        if origin and origins:
            if origins.strip() == "*":
                response.headers["Access-Control-Allow-Origin"] = "*"
            else:
                # Normalize origins by removing trailing slashes for comparison
                normalized_origin = origin.rstrip('/')
                allowed_origins = [o.strip().rstrip('/') for o in origins.split(",")]
                if normalized_origin in allowed_origins:
                    response.headers["Access-Control-Allow-Origin"] = origin
                # If origin not allowed, don't set CORS headers at all
        
        response.headers["Access-Control-Allow-Headers"] = get_global_variable('headers')
    return response