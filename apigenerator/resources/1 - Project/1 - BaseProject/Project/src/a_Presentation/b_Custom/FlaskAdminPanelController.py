# System imports #
# No standard system imports like json, yaml, re etc. seem to be used directly here.

# Flask Imports #
from flask import request, render_template, flash, redirect, url_for, Blueprint
from flask_login import LoginManager, UserMixin, login_user

# Infra Imports #
# Assuming app_handler and auth_blueprint are essential exports from FlaskBuilder for this controller
from src.e_Infra.b_Builders.FlaskBuilder import app_handler, auth_blueprint
# FlaskAdminPanelBuilder is likely imported for its side effects (e.g., admin panel setup)
import src.e_Infra.b_Builders.FlaskAdminPanelBuilder
from src.e_Infra.GlobalVariablesManager import get_global_variable

# Service Layer Imports #
# Assuming SQLService might be used for side-effects or in parts of the class not shown.
# If truly unused, this should be removed. For now, making it a non-wildcard import.
import src.b_Application.b_Service.b_Custom.SQLService


login_manager = LoginManager(app_handler)
login_manager.login_view = 'auth.login_route' # Uses auth_blueprint.name implicitly via 'auth.' prefix


class Auth(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return self.id


admin_panel_user = get_global_variable(variable_name='admin_panel_user')
admin_panel_password = get_global_variable(
    variable_name='admin_panel_password')

# Ensure admin_user is created only if admin_panel_user and password are not None
if admin_panel_user and admin_panel_password:
    admin_user = Auth(1, admin_panel_user, admin_panel_password)
else:
    # Handle the case where admin credentials are not set, e.g., log a warning or raise an error
    # For now, admin_user might be None, which could cause issues in load_user if not handled.
    # Or, provide default dummy values if that's acceptable for the application's security model (usually not).
    # This part of logic is pre-existing, focus is on imports.
    admin_user = None


@login_manager.user_loader
def load_user(user_id):
    # Added check for admin_user not being None
    if admin_user and int(user_id) == admin_user.id:
        return admin_user
    return None


@auth_blueprint.route('/auth/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Added check for admin_user not being None
        if admin_user and username == admin_user.username and password == admin_user.password:
            login_user(admin_user)
            return redirect('/admin') # Assuming '/admin' is setup by FlaskAdminPanelBuilder
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login_route')) # Uses auth_blueprint.name
    return render_template('auth.html')


# Register the blueprint
# This assumes auth_blueprint is correctly imported from FlaskBuilder,
# and app_handler is also correctly imported.
app_handler.register_blueprint(auth_blueprint)

# Note on FlaskBuilder structure:
# FlaskBuilder.py seems to be a central point for Flask app setup and also for defining common blueprints
# like 'auth_blueprint'. This is a valid pattern, though sometimes blueprints are defined within their
# respective controller modules. The refactoring assumes 'auth_blueprint' is provided by FlaskBuilder.
# If FlaskBuilder was *only* providing flask components (request, render_template etc.) and app_handler,
# then auth_blueprint would need to be defined in this file:
# auth_blueprint = Blueprint('auth', __name__)
# But the current structure seems to imply FlaskBuilder provides it.
# Added minor safety for admin_user creation and usage.
# The import for SQLService is kept as non-wildcard; if it's unused, it should be removed in a code cleanup task.
# FlaskAdminPanelBuilder is imported for its side-effects.
# Corrected login_manager.user_loader to handle admin_user potentially being None.
# Corrected login_route to handle admin_user potentially being None.
