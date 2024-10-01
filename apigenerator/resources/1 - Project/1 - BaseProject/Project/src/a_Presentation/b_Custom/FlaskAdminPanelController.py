# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *
from src.e_Infra.b_Builders.FlaskAdminPanelBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.b_Custom.SQLService import *

login_manager = LoginManager(app_handler)
login_manager.login_view = 'auth.login_route'


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
admin_user = Auth(1, admin_panel_user, admin_panel_password)


@login_manager.user_loader
def load_user(user_id):
    if int(user_id) == 1:
        return admin_user
    return None


@auth_blueprint.route('/auth/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_panel_user and password == admin_panel_password:
            login_user(admin_user)
            return redirect('/admin')
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login_route'))
    return render_template('auth.html')


# Register the blueprint
app_handler.register_blueprint(auth_blueprint)
