# System Imports #
import os
import re
import shutil


# This function will check for column types that can't use flask admin filters, to then remove them on the build of column_filters
def extract_columns_to_exclude_from_column_filters(file_path):
    types_to_exclude_from_column_filters = [r"^.*\bsa\.JSON\b.*$", r"^.*\bSET\b.*?\)$", r"^.*\bsa\.BINARY\b.*$",
                                            r"^.*\bsa\.VARBINARY\b.*$", r"^.*\bsa\.BLOB\b.*$",r"^.*\bMONEY\b.*?\)$",
                                            r"^.*\bsa\.Interval\b.*$", r"^.*\bsa\.ARRAY\b.*$"]

    columns = []

    with open(file_path, 'r') as file:
        content = file.read()

    for type_pattern in types_to_exclude_from_column_filters:
        # Find all matches in the file content
        matches = re.findall(type_pattern, content, re.M)

        for match in matches:
            # Regular expression to capture the column name
            column_pattern = r"^\s*(\w+)\s*:\s*"
            column_match = re.match(column_pattern, match)
            if column_match:
                columns.append(column_match.group(1))

    return columns


def parse_model_attributes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    fields_pattern = r"fields = \((.*?)\)"
    fields_match = re.search(fields_pattern, content, re.S)

    if fields_match:
        fields = fields_match.group(1).replace(
            '"', '').replace("'", "").split(",")
        fields = tuple(field.strip() for field in fields if field.strip())
    else:
        fields = ()

    pk_autoincrement = 'primary_key=True' in content and 'autoincrement=True' in content

    return fields, pk_autoincrement


def create_model_view(model_name, fields, pk_autoincrement, file_path):
    fields_to_remove = extract_columns_to_exclude_from_column_filters(
        file_path)
    if fields_to_remove:
        column_filters = [
            field for field in fields if field not in fields_to_remove]
    else:
        column_filters = fields
    form_columns = fields if not pk_autoincrement else fields[1:]

    return f"""

class {model_name}ModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    column_list = {tuple(fields)}
    column_searchable_list = {tuple(fields)}
    column_filters = {tuple(column_filters)}
    form_columns = {tuple(form_columns)}
"""


def generate_flask_admin_files(result, project_domain_folder, domain_files, script_absolute_path, database):
    views_code = "from flask_admin.contrib.sqla import ModelView\nfrom flask_login import login_required, current_user\n"
    admin_views = ""
    model_imports = ""
    database_mapper = {
        "mysql": "MySql",
        "pgsql": "PgSql",
        "mssql": "MsSql",
        "mariadb": "MariaDb"
    }

    for domain_file in domain_files:
        model_name = domain_file[:-3]  # Remove .py extension
        fields, pk_autoincrement = parse_model_attributes(
            os.path.join(project_domain_folder, domain_file))
        views_code += create_model_view(model_name, fields, pk_autoincrement,
                                        os.path.join(project_domain_folder, domain_file))
        model_imports += f"from src.c_Domain.{model_name} import {model_name}\n"
        admin_views += f"admin.add_view({model_name}ModelView({model_name}, get_{database}_connection_session()))\n"

    # Write FlaskAdminModelViews.py
    if not os.path.exists(os.path.join(project_domain_folder, 'a_FlaskAdminPanel')):
        os.makedirs(os.path.join(project_domain_folder, 'a_FlaskAdminPanel'))

    if not os.path.exists(os.path.join(result, 'config', 'auth.html')):
        shutil.copy(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/config/auth.html'),
                        os.path.join(result, 'config', 'auth.html'))

    with open(os.path.join(project_domain_folder, 'a_FlaskAdminPanel', 'FlaskAdminModelViews.py'), 'w') as file:
        file.write(views_code)

    # Write FlaskAdminPanelBuilder.py
    builder_code = f"""from src.e_Infra.b_Builders.FlaskBuilder import app_handler
from flask_admin import Admin, BaseView, expose
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user
from src.c_Domain.a_FlaskAdminPanel.FlaskAdminModelViews import *
from src.e_Infra.c_Resolvers.{database_mapper[database]}ConnectionResolver import get_{database}_connection_session
{model_imports}

admin = Admin(app_handler)
app_handler.secret_key = '1234'

{admin_views}
"""
    with open(os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskAdminPanelBuilder.py'), 'w') as file:
        file.write(builder_code)

    # Modify app.py
    with open(os.path.join(result, 'app.py'), 'r+') as file:
        content = file.read()
        import_statement = "from src.e_Infra.b_Builders.FlaskAdminPanelBuilder import *"
        if import_statement not in content:
            content = content.replace('# Infra Imports #\nfrom src.e_Infra.g_Environment.EnvironmentVariables import *',
                                      f'# Infra Imports #\nfrom src.e_Infra.g_Environment.EnvironmentVariables import *\n{import_statement}')
            file.seek(0)
            file.write(content)
            file.truncate()


def build_flask_admin_files(result, project_domain_folder, script_absolute_path, database):
    print('Adding Flask Admin to API')
    domain_files = [
        f for f in os.listdir(f'{project_domain_folder}')
        if f.endswith('.py') and f not in ['__init__.py', 'FlaskAdminModelViews.py']
    ]
    generate_flask_admin_files(
        result, project_domain_folder, domain_files, script_absolute_path, database)
