import os
from typing import Optional
import typer
import json
from databaseconnector.RegexHandler import *
from databaseconnector.FilesHandler import clean_directory
from databaseconnector.MySqlMetadataGeneratorWorker import generate_mysql_database_metadata
from databaseconnector.PostgreSqlMetadataGeneratorWorker import generate_postgresql_database_metadata
from databaseconnector.SqlServerMetadataGeneratorWorker import generate_sqlserver_database_metadata
from domaingenerator.DomainFilesGeneratorWorker import generate_domain_files
from apigenerator.b_Workers.ApiGeneratorWorker import generate_python_rest_api

app = typer.Typer()


@app.command()
def generate(
    result_path: Optional[str] = None,
    use_pascal_case: Optional[bool] = True,
    us_datetime: Optional[bool] = False,
    mysql_connection_parameters: Optional[str] = None,
    mysql_connection_string: Optional[str] = None,
    postgres_connection_parameters: Optional[str] = None,
    postgres_connection_string: Optional[str] = None,
    sqlserver_connection_parameters: Optional[str] = None,
    sqlserver_connection_string: Optional[str] = None,
    mariadb_connection_parameters: Optional[str] = None,
    mariadb_connection_string: Optional[str] = None,
):
    # Application start and database connection
    if (mysql_connection_string or mysql_connection_parameters) and (postgres_connection_string or postgres_connection_parameters) and (sqlserver_connection_string or sqlserver_connection_parameters) and (mariadb_connection_string or mariadb_connection_parameters):
        typer.echo("Please specify only one of: MySQL, PostgreSQL, SQLServer, or MariaDB.")
        return

    if not result_path:
        result_path = "PythonRestAPI"

    result_full_path = os.path.abspath(os.path.join(os.getcwd(), result_path))

    # Check if the folder exists
    if os.path.exists(result_full_path):
        typer.echo(f"Cleaning up existing folder: {result_full_path}")
        clean_directory(result_full_path)

    else:
        # Create folder for API Generation if it does not exist
        os.makedirs(result_full_path)

    if mysql_connection_parameters:
        try:
            mysql_params = eval(mysql_connection_parameters)
            generate_mysql_database_metadata('mysql', mysql_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing MySQL connection parameters: {e}")

    elif mysql_connection_string:
        try:
            mysql_params = extract_mysql_params(mysql_connection_string)
            generate_mysql_database_metadata('mysql', mysql_params, use_pascal_case, result_full_path)
            # Python Domain Files Generation
            generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
            os.makedirs(generated_domains_path)
            generate_domain_files(result_full_path, generated_domains_path)
            # PythonRest API Generation
            generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mysql', mysql_params)
        except Exception as e:
            typer.echo(e)

    elif postgres_connection_parameters:
        try:
            postgres_params = json.loads(postgres_connection_parameters)
            generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing PostgreSQL connection parameters: {e}")

    elif postgres_connection_string:
        try:
            postgres_params = extract_postgres_params(postgres_connection_string)
            generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path)
            # Python Domain Files Generation
            generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
            os.makedirs(generated_domains_path)
            generate_domain_files(result_full_path, generated_domains_path)
            # PythonRest API Generation
            generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'pgsql', postgres_params)
        except Exception as e:
            typer.echo(e)

    elif sqlserver_connection_parameters:
        try:
            sqlserver_params = eval(sqlserver_connection_parameters)
            generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing SQLServer connection parameters: {e}")

    elif sqlserver_connection_string:
        try:
            sqlserver_params = extract_sqlserver_params(sqlserver_connection_string)
            generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path)
            # Python Domain Files Generation
            generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
            os.makedirs(generated_domains_path)
            generate_domain_files(result_full_path, generated_domains_path)
            # PythonRest API Generation
            generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mssql', sqlserver_params)
        except Exception as e:
            typer.echo(e)

    elif mariadb_connection_parameters:
        try:
            mariadb_params = eval(mariadb_connection_parameters)
            generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing MariaDB connection parameters: {e}")

    elif mariadb_connection_string:
        try:
            mariadb_params = extract_mariadb_params(mariadb_connection_string)
            generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path)
            # Python Domain Files Generation
            generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
            os.makedirs(generated_domains_path)
            generate_domain_files(result_full_path, generated_domains_path)
            # PythonRest API Generation
            generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mariadb', mariadb_params)
        except Exception as e:
            typer.echo(e)
    else:
        typer.echo("Please provide either MySQL, PostgreSQL, SQLServer, or MariaDB connection parameters or a connection string.")


@app.command()
def version():
    typer.echo("pythonrest v1.0")


if __name__ == "__main__":
    app()
