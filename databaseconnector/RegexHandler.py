import re


def extract_mysql_params(connection_string):
    pattern = re.compile(r"mysql:\/\/([^:]+):([^@]+)@([^:]+):([^\/]+)\/(.+)")
    match = pattern.match(connection_string)

    if match:
        return {
            "mysql_user": match.group(1),
            "mysql_password": match.group(2),
            "mysql_host": match.group(3),
            "mysql_port": int(match.group(4)),
            "mysql_schema": match.group(5),
        }
    else:
        raise ValueError("Invalid MySQL connection string format.")


def validate_postgres_connection_string(connection_string):
    pattern = re.compile(r"postgresql:\/\/([^:]+):([^@]+)@([^:]+):([^\/]+)\/([^?]+)\?options=-c%20search_path=([^,]+),public")
    match = pattern.match(connection_string)

    if match:
        return True
    else:
        return False


def extract_postgres_params(connection_string):
    if validate_postgres_connection_string(connection_string):
        pattern = re.compile(r"postgresql:\/\/([^:]+):([^@]+)@([^:]+):([^\/]+)\/([^?]+)\?options=-c%20search_path=([^,]+),public")
        match = pattern.match(connection_string)

        return {
            "pgsql_user": match.group(1),
            "pgsql_password": match.group(2),
            "pgsql_host": match.group(3),
            "pgsql_port": int(match.group(4)),
            "pgsql_database_name": match.group(5),
            "pgsql_schema": match.group(6),
        }
    else:
        raise ValueError("Invalid PostgreSQL connection string format. Please use the pattern 'postgresql://{user}:{password}@{host}:{port}/{database}?options=-c%20search_path={schema},public'.")



def extract_sqlserver_params(connection_string):
    pattern = re.compile(r"mssql:\/\/([^\:]+):([^\@]+)@([^\:]+):([^\:]+)\/(.+)")
    match = pattern.match(connection_string)

    if match:
        return {
            "mssql_user": match.group(1),
            "mssql_password": match.group(2),
            "mssql_host": match.group(3),
            "mssql_port": int(match.group(4)),
            "mssql_schema": match.group(5),
        }
    else:
        raise ValueError("Invalid SQL Server connection string format.")


def extract_mariadb_params(connection_string):
    pattern = re.compile(r"mariadb:\/\/([^\:]+):([^\@]+)@([^\:]+):([^\:]+)\/(.+)")
    match = pattern.match(connection_string)

    if match:
        return {
            "mariadb_user": match.group(1),
            "mariadb_password": match.group(2),
            "mariadb_host": match.group(3),
            "mariadb_port": int(match.group(4)),
            "mariadb_schema": match.group(5),
        }
    else:
        raise ValueError("Invalid MariaDB connection string format.")


def transform_table_name_to_pascal_case_class_name(table_name):
    # Remove special characters (including underscores) and split the name into words
    words = re.findall(r'[a-zA-Z0-9]+', table_name)

    # Convert the words to PascalCase
    pascal_case_name = ''.join(word.capitalize() for word in words)

    return pascal_case_name
