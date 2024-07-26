from flask import render_template


def build_redoc_blueprint(app_handler, redoc_blueprint):
    @redoc_blueprint.route('/redoc')
    def redoc():
        return render_template('redoc.html')

    # Register the blueprint
    app_handler.register_blueprint(redoc_blueprint)
