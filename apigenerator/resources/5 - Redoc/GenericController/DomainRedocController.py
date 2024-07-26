
# Method to build declarative_meta Redoc Blueprint #
def build_meta_string_redoc_blueprint(app_handler, redoc_blueprint):
    @redoc_blueprint.route('/redoc/meta_string')
    def redoc():
        return render_template('declarative_meta.html')

    app_handler.register_blueprint(redoc_blueprint)