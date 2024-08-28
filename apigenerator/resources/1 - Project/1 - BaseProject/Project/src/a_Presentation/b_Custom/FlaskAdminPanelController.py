# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *
from src.e_Infra.b_Builders.FlaskAdminPanelBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.b_Custom.SQLService import *

login_manager = LoginManager(app_handler)
login_manager.login_view = 'auth.login_route'  # Rota para a página de login

# Usuário fixo (em produção, utilize uma forma mais segura de armazenar credenciais)


class Auth(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return self.id


username = get_global_variable(variable_name='ADMIN_USER')
password = get_global_variable(variable_name='ADMIN_PASSWORD')
admin_user = Auth(1, username, password)


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
        if username == 'admin' and password == 'admin':
            login_user(admin_user)
            return redirect('/admin')
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login_route'))
    return render_template('auth.html')


# Register the blueprint
app_handler.register_blueprint(auth_blueprint)