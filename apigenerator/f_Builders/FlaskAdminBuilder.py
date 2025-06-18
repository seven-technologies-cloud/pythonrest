# System Imports #
import os
import re
import shutil
from pathlib import Path


# This function will check for column types that can't use flask admin filters, to then remove them on the build of column_filters
def extract_columns_to_exclude_from_column_filters(file_path: Path): # Expect Path object
    types_to_exclude_from_column_filters_patterns = [
        r"^.*\bsa\.JSON\b.*$", r"^.*\bSET\b.*?\)$", r"^.*\bsa\.BINARY\b.*$",
        r"^.*\bsa\.VARBINARY\b.*$", r"^.*\bsa\.BLOB\b.*$", r"^.*\bMONEY\b.*?\)$",
        r"^.*\bsa\.Interval\b.*$", r"^.*\bsa\.ARRAY\b.*$"
    ]
    # Compile regex patterns for efficiency
    compiled_type_patterns = [re.compile(pattern) for pattern in types_to_exclude_from_column_filters_patterns]
    column_name_capture_pattern = re.compile(r"^\s*(\w+)\s*:\s*")

    content = file_path.read_text()

    # Use a list comprehension with an assignment expression (Python 3.8+)
    columns = [
        column_match.group(1)
        for compiled_pattern in compiled_type_patterns
        for match in compiled_pattern.findall(content, re.M)
        if (column_match := column_name_capture_pattern.match(match))
    ]
    return columns


def parse_model_attributes(file_path: Path): # Expect Path object
    content = file_path.read_text()

    fields_pattern = r"fields = \((.*?)\)" # Regex seems fine
    fields_match = re.search(fields_pattern, content, re.S)

    if fields_match:
        fields_str = fields_match.group(1)
        # Efficiently split and strip, then filter out empty strings
        fields_list = [field.strip().replace('"', '').replace("'", "") for field in fields_str.split(",")]
        fields = tuple(field for field in fields_list if field)
    else:
        fields = ()

    pk_autoincrement = 'primary_key=True' in content and 'autoincrement=True' in content

    return fields, pk_autoincrement


def create_model_view(model_name, fields, pk_autoincrement, file_path: Path): # Expect Path object
    # Ensure form_columns is also a list/tuple as expected by the f-string formatting later
    form_columns_list = list(fields) if not pk_autoincrement else list(fields[1:])

    return f"""

class {model_name}ModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    column_list = {tuple(fields)}
    column_searchable_list = {tuple(fields)}
    form_columns = {tuple(form_columns_list)}
"""


def generate_flask_admin_files(result_path_str, project_domain_folder_str, domain_files, script_absolute_path_str, database):
    result_path = Path(result_path_str)
    project_domain_path = Path(project_domain_folder_str)
    script_absolute_path = Path(script_absolute_path_str)

    # Initialize lists to store parts of the code to be joined later
    views_code_list = ["from flask_admin.contrib.sqla import ModelView\nfrom flask_login import login_required, current_user\n"]
    model_imports_list = []
    admin_views_list = []

    database_mapper = {
        "mysql": "MySql",
        "pgsql": "PgSql",
        "mssql": "MsSql",
        "mariadb": "MariaDb"
    }

    for domain_file_name in domain_files:
        model_name = domain_file_name[:-3]  # Remove .py extension
        current_model_file_path = project_domain_path / domain_file_name
        fields, pk_autoincrement = parse_model_attributes(current_model_file_path)

        # Append to lists
        views_code_list.append(create_model_view(model_name, fields, pk_autoincrement, current_model_file_path))
        model_imports_list.append(f"from src.c_Domain.{model_name} import {model_name}\n")
        admin_views_list.append(f"admin.add_view({model_name}ModelView({model_name}, get_{database}_connection_session()))\n")

    # Join the lists to form the final code strings
    views_code = "".join(views_code_list)
    model_imports = "".join(model_imports_list)
    admin_views = "".join(admin_views_list)

    # Write FlaskAdminModelViews.py
    flask_admin_panel_path = project_domain_path / 'a_FlaskAdminPanel'
    if not flask_admin_panel_path.exists():
        flask_admin_panel_path.mkdir(parents=True, exist_ok=True)

    auth_html_config_path = result_path / 'config' / 'auth.html'
    auth_html_source_path = script_absolute_path / 'apigenerator/resources/1 - Project/1 - BaseProject/Project/config/auth.html'

    if not auth_html_config_path.exists():
        auth_html_config_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(auth_html_source_path), str(auth_html_config_path))

    flask_admin_model_views_path = flask_admin_panel_path / 'FlaskAdminModelViews.py'
    flask_admin_model_views_path.write_text(views_code)

    # Write FlaskAdminPanelBuilder.py
    # database_mapper[database] is used here, ensure `database` is a valid key
    db_resolver_name = database_mapper.get(database)
    if not db_resolver_name:
        # Handle error: unknown database type or provide a default
        # For now, let's assume 'database' will always be a valid key as per original code logic
        pass

    builder_code = f"""from src.e_Infra.b_Builders.FlaskBuilder import app_handler
from flask_admin import Admin, BaseView, expose
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user
from src.c_Domain.a_FlaskAdminPanel.FlaskAdminModelViews import *
from src.e_Infra.c_Resolvers.{db_resolver_name}ConnectionResolver import get_{database}_connection_session
{model_imports}

admin = Admin(app_handler)
app_handler.secret_key = '1234'

{admin_views}
"""
    flask_admin_panel_builder_path = result_path / 'src' / 'e_Infra' / 'b_Builders' / 'FlaskAdminPanelBuilder.py'
    flask_admin_panel_builder_path.write_text(builder_code)

    # Modify app.py
    app_py_path = result_path / 'app.py'
    content = app_py_path.read_text()
    import_statement = "from src.e_Infra.b_Builders.FlaskAdminPanelBuilder import *"
    if import_statement not in content:
        content = content.replace('# Infra Imports #\nfrom src.e_Infra.g_Environment.EnvironmentVariables import *',
                                  f'# Infra Imports #\nfrom src.e_Infra.g_Environment.EnvironmentVariables import *\n{import_statement}')
        app_py_path.write_text(content)


def build_flask_admin_files(result, project_domain_folder, script_absolute_path, database):
    print('Adding Flask Admin to API')

    p_project_domain_folder = Path(project_domain_folder)

    # This list comprehension is already efficient and readable.
    domain_files = [
        p.name for p in p_project_domain_folder.iterdir()
        if p.is_file() and p.name.endswith('.py') and p.name not in ['__init__.py', 'FlaskAdminModelViews.py']
    ]
    generate_flask_admin_files(
        str(result), str(project_domain_folder), domain_files, str(script_absolute_path), database)
