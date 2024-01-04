from apigenerator.b_Workers.ModifierHandler import *
from apigenerator.b_Workers.DirectoryManager import *

directories = get_directory_data()

db_dependencies = directories['db_dependencies']
db_conn_files = directories['db_conn_files']
db_conn_resolvers = directories['db_conn_resolvers']


def install_database_files(result_full_path, db, script_absolute_path):
# Install database dependencies files, configures the database connection inside the application and their resolvers.

    print('installing selected database files and adding library to requirements...')

    copy_database_files(os.path.join(script_absolute_path, '{}/{}'.format(db_conn_files, db)),
                        os.path.join(result_full_path, 'src', 'd_Repository', 'd_DbConnection'))

    copy_database_files(os.path.join(script_absolute_path, '{}/{}'.format(db_conn_resolvers, db)),
                        os.path.join(result_full_path, 'src', 'e_Infra', 'c_Resolvers'))

    if db == 'mysql':
        append_database_library_to_requirements_file(os.path.join(result_full_path, "requirements.txt"), "pymysql")
        modify_main_conn_resolver(result_full_path, "MySql", "mysql")

    if db == 'pgsql':
        append_database_library_to_requirements_file(os.path.join(result_full_path, "requirements.txt"), "psycopg2")
        modify_main_conn_resolver(result_full_path, "PgSql", "pgsql")

    if db == 'mssql':
        append_database_library_to_requirements_file(os.path.join(result_full_path, "requirements.txt"), "pymssql")
        modify_main_conn_resolver(result_full_path, "MsSql", "mssql")

    if db == 'mariadb':
        append_database_library_to_requirements_file(os.path.join(result_full_path, "requirements.txt"), "pymysql")
        modify_main_conn_resolver(result_full_path, "MariaDb", "mariadb")
