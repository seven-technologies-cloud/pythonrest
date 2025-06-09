# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import app_handler # Specific import

# Service Imports #
# Assuming print_user_request and ApplicationException are directly from BeforeRequestService.
# If ApplicationException is more globally defined (e.g. in ExceptionsHandler),
# it would be better to import it from its canonical source.
# For this refactoring, making the wildcard specific to used names from this path.
from src.b_Application.b_Service.b_Custom.BeforeRequestService import print_user_request, ApplicationException


@app_handler.before_request
def flask_before_request():
    try:
        print_user_request()
    except ApplicationException as e: # This now correctly refers to the imported ApplicationException
        return e.response

# Note: It's common for custom exceptions like ApplicationException to be defined in a central
# exceptions module (e.g., ExceptionsHandler.py) and imported from there across the application.
# If BeforeRequestService.py re-exports ApplicationException from a more central location,
# that's fine. If it defines its own, it might lead to type-checking issues if different
# ApplicationException types are expected in different parts of the app.
# This refactoring strictly makes the import specific to what's used from the given path.
