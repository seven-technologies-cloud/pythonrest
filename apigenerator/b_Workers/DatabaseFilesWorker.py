from pathlib import Path
from apigenerator.b_Workers.ModifierHandler import *
from apigenerator.b_Workers.DirectoryManager import *

directories = get_directory_data()

db_dependencies = directories['db_dependencies']
db_conn_files = directories['db_conn_files']
db_conn_resolvers = directories['db_conn_resolvers']

DB_CONFIG = {
    'mysql': {
        'ssh_libs': "pymysql==1.1.0\nsshtunnel==0.4.0",
        'libs': "pymysql==1.1.0",
        'resolver_name': "MySql",
        'resolver_arg': "mysql"
    },
    'pgsql': {
        'ssh_libs': "psycopg2-binary==2.9.9\nsshtunnel==0.4.0",
        'libs': "psycopg2-binary==2.9.9",
        'resolver_name': "PgSql",
        'resolver_arg': "pgsql"
    },
    'mssql': {
        'ssh_libs': "pymssql==2.2.11\nsshtunnel==0.4.0",
        'libs': "pymssql==2.2.11",
        'resolver_name': "MsSql",
        'resolver_arg': "mssql"
    },
    'mariadb': { # Shares mysql libs for pymysql driver
        'ssh_libs': "pymysql==1.1.0\nsshtunnel==0.4.0",
        'libs': "pymysql==1.1.0",
        'resolver_name': "MariaDb",
        'resolver_arg': "mariadb"
    }
}

def install_database_files(result_full_path, db, script_absolute_path, db_authentication_method=None):
# Install database dependencies files, configures the database connection inside the application and their resolvers.

    print('installing selected database files and adding library to requirements...')

    # Define base paths
    src_repo_conn_path = Path(result_full_path) / 'src' / 'd_Repository' / 'd_DbConnection'
    src_infra_resolvers_path = Path(result_full_path) / 'src' / 'e_Infra' / 'c_Resolvers'

    # Determine source path for connection files based on auth method
    if db_authentication_method:
        db_conn_source_path = Path(script_absolute_path) / db_conn_files / db / db_authentication_method
    else:
        # Ensure auth_path_segment is empty if db_authentication_method is None or empty
        auth_path_segment = db_authentication_method if db_authentication_method else ''
        db_conn_source_path = Path(script_absolute_path) / db_conn_files / db / auth_path_segment

    copy_database_files(str(db_conn_source_path), str(src_repo_conn_path))

    # Resolver files path
    db_resolver_source_path = Path(script_absolute_path) / db_conn_resolvers / db
    copy_database_files(str(db_resolver_source_path), str(src_infra_resolvers_path))

    requirements_path_obj = Path(result_full_path) / "requirements.txt" # Keep as Path object for now

    if db in DB_CONFIG:
        config = DB_CONFIG[db]
        # Check for SSH; ensure db_authentication_method is not None before 'in' check
        is_ssh = bool(db_authentication_method and 'ssh' in db_authentication_method)

        lib_to_add = config['ssh_libs'] if is_ssh else config['libs']
        # append_database_library_to_requirements_file expects a string path
        append_database_library_to_requirements_file(str(requirements_path_obj), lib_to_add)

        # modify_main_conn_resolver expects result_full_path as string
        modify_main_conn_resolver(str(result_full_path), config['resolver_name'], config['resolver_arg'])
    else:
        # Optional: handle unknown db type, though original code didn't explicitly
        print(f"Warning: Database type '{db}' not configured for requirements or resolver modification.")
