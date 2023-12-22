# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Imports #
from src.b_Application.b_Service.b_Custom.BeforeRequestService import *


@app_handler.before_request
def flask_before_request():
    try:
        print_user_request()
    except ApplicationException as e:
        return e.response
