from flask_swagger_ui import get_swaggerui_blueprint
from flask import redirect, request


# Method to build Swagger Blueprint #
def build_swagger_blueprint(app_handler):

    @app_handler.route('/swagger', methods=['GET'])
    def swagger_redirect():
        return redirect('/swagger/')

    SWAGGER_URL = "/swagger"
    API_URL = "/swaggerdata"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Swagger"
        },
        blueprint_name='Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)
