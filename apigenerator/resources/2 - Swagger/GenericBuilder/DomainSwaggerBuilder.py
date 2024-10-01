

# Method to build declarative_meta Swagger Blueprint #
def build_meta_string_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/meta_string', methods=['GET'])
    def swagger_meta_string_redirect():
        return redirect('/swagger/meta_string/')

    SWAGGER_URL = "/swagger/meta_string"
    API_URL = "/swaggerdata/meta_string"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "declarative_meta Swagger"
        },
        blueprint_name='declarative_meta Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)
