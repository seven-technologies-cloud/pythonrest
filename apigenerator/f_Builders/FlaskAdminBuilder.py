import os
import re


def parse_model_attributes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    fields_pattern = r"fields = \((.*?)\)"
    fields_match = re.search(fields_pattern, content, re.S)

    if fields_match:
        fields = fields_match.group(1).replace('"', '').replace("'", "").split(",")
        fields = [field.strip() for field in fields]
    else:
        fields = []

    pk_autoincrement = 'primary_key=True' in content and 'autoincrement=True' in content

    return fields, pk_autoincrement


def create_model_view(model_name, fields, pk_autoincrement):
    form_columns = fields if not pk_autoincrement else fields[1:]

    return f"""

class {model_name}ModelView(ModelView):
    column_list = {tuple(fields)}
    column_searchable_list = {tuple(fields)}
    column_filters = {tuple(fields)}
    form_columns = {tuple(form_columns)}
"""


def generate_flask_admin_files(result, project_domain_folder, domain_files):
    views_code = "from flask_admin.contrib.sqla import ModelView\n"
    admin_views = ""
    model_imports = ""

    for domain_file in domain_files:
        model_name = domain_file[:-3]  # Remove .py extension
        fields, pk_autoincrement = parse_model_attributes(f'{project_domain_folder}/{domain_file}')
        views_code += create_model_view(model_name, fields, pk_autoincrement)
        model_imports += f"from src.c_Domain.{model_name} import {model_name}\n"
        admin_views += f"admin.add_view({model_name}ModelView({model_name}, get_mysql_connection_session()))\n"

    # Write FlaskAdminModelViews.py
    with open(os.path.join(project_domain_folder, 'FlaskAdminModelViews.py'), 'w') as file:
        file.write(views_code)

    # Write FlaskAdminPanelBuilder.py
    builder_code = f"""from src.e_Infra.b_Builders.FlaskBuilder import app_handler
from flask_admin import Admin
from src.c_Domain.FlaskAdminModelViews import *
from src.e_Infra.c_Resolvers.MySqlConnectionResolver import get_mysql_connection_session
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


def build_flask_admin_files(result, project_domain_folder):
    print('Adding Flask Admin to API')
    domain_files = [
        f for f in os.listdir(f'{project_domain_folder}')
        if f.endswith('.py') and f not in ['__init__.py', 'FlaskAdminModelViews.py']
    ]
    generate_flask_admin_files(result, project_domain_folder, domain_files)

