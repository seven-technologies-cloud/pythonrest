# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Imports #
from src.b_Application.b_Service.b_Custom.ErrorHandlerService import *


@app_handler.errorhandler(Exception)
def handle_flask_exception(error):
    print_user_request_on_error()
    response = build_error_response(error)
    return response
