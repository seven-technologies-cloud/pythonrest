#!/usr/bin/env python

import os
from typing import Optional
import typer
import json
import sys
from databaseconnector.RegexHandler import *
from databaseconnector.FilesHandler import check_if_provided_directory_is_unsafe, check_if_current_working_directory_is_unsafe, check_if_given_result_path_is_unsafe
from databaseconnector.MySqlMetadataGeneratorWorker import generate_mysql_database_metadata
from databaseconnector.PostgreSqlMetadataGeneratorWorker import generate_postgresql_database_metadata
from databaseconnector.SqlServerMetadataGeneratorWorker import generate_sqlserver_database_metadata
from domaingenerator.DomainFilesGeneratorWorker import generate_domain_files
from apigenerator.b_Workers.DirectoryManager import check_if_base_project_exists
from apigenerator.b_Workers.ApiGeneratorWorker import generate_python_rest_api
from apigenerator.e_Enumerables.Enumerables import get_directory_data


app = typer.Typer()
pythonrest_version = "0.3.7"


@app.command()
def generate(
    result_path: Optional[str] = None,
    use_pascal_case: Optional[bool] = True,
    us_datetime: Optional[bool] = False,
    project_name: Optional[str] = "PythonREST",
    uid_type: Optional[str] = "uuid",
    mysql_connection_parameters: Optional[str] = None,
    mysql_connection_string: Optional[str] = None,
    postgres_connection_parameters: Optional[str] = None,
    postgres_connection_string: Optional[str] = None,
    sqlserver_connection_parameters: Optional[str] = None,
    sqlserver_connection_string: Optional[str] = None,
    mariadb_connection_parameters: Optional[str] = None,
    mariadb_connection_string: Optional[str] = None,
    ssh_password_authentication_string: Optional[str] = None,
    ssh_publickey_authentication_string: Optional[str] = None,
    ssl_authentication_string: Optional[str] = None,
):
    # Application start and database connection
    if (mysql_connection_string or mysql_connection_parameters) and (postgres_connection_string or postgres_connection_parameters) and (sqlserver_connection_string or sqlserver_connection_parameters) and (mariadb_connection_string or mariadb_connection_parameters):
        typer.echo("Please specify only one of: MySQL, PostgreSQL, SQLServer, or MariaDB.")
        return

    if result_path:
        if check_if_given_result_path_is_unsafe(result_path):
            typer.echo(f"Error: Given result path {result_path} is unsafe to generate API on, please provide another result path, API generation aborted!")
            return
        if not result_path.endswith('\\'):
            result_path = os.path.join(result_path, get_directory_data()['result_path_suffix'])
        else:
            result_path = result_path + get_directory_data()['result_path_suffix']
    else:
        result_path = get_directory_data()['result_path_suffix']

    result_full_path = os.path.abspath(os.path.join(os.getenv('PWD', os.getcwd()), result_path))

    if check_if_current_working_directory_is_unsafe(os.getenv('PWD', os.getcwd())):
        typer.echo(f"Error: pythonrest is running from an unsafe directory: {os.getenv('PWD', os.getcwd())}, please run from another directory, API generation aborted!")
        return

    if check_if_provided_directory_is_unsafe(result_full_path):
        typer.echo(f"Error: Unsafe directory {result_full_path} was provided as creation path, API generation aborted!")
        return

    typer.echo(f"API will be generated on this path: {result_full_path}")

    # Create folder for API Generation if it does not exist
    if not os.path.exists(result_full_path):
        os.makedirs(result_full_path)
        base_project_exists = False

    else:
        base_project_exists = check_if_base_project_exists(result_full_path)
        if not base_project_exists:
            if len(os.listdir(result_full_path)) != 0:
                typer.echo(f"Folder {result_full_path} that was specified to generate the api is not empty, these files and/or folders are present: "
                           f"\n{json.dumps(os.listdir(result_full_path), indent=4)}")
                return

    if mysql_connection_parameters:
        try:
            mysql_params = json.loads(mysql_connection_parameters)
            generate_mysql_database_metadata('mysql', mysql_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing MySQL connection parameters: {e}")
            return
 
    elif mysql_connection_string:
        try:
            mysql_params = extract_mysql_params(mysql_connection_string)
            if ssh_password_authentication_string:
                ssh_params = extract_ssh_params(ssh_password_authentication_string)
                generate_mysql_database_metadata(
                    'mysql', mysql_params, use_pascal_case, result_full_path, ssh_params
                )
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mysql', mysql_params,
                                         base_project_exists, project_name, uid_type, ssh_params, 'ssh_password_authentication')
            elif ssh_publickey_authentication_string:
                ssh_publickey_params = extract_ssh_publickey_params(ssh_publickey_authentication_string)
                generate_mysql_database_metadata(
                    'mysql', mysql_params, use_pascal_case, result_full_path, ssh_publickey_params=ssh_publickey_params
                )
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mysql', mysql_params,
                                         base_project_exists, project_name, uid_type, ssh_publickey_params, 'ssh_publickey_authentication')
            elif ssl_authentication_string:
                ssl_params = extract_ssl_params(ssl_authentication_string)
                generate_mysql_database_metadata(
                    'mysql', mysql_params, use_pascal_case, result_full_path, ssl_params=ssl_params
                )
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mysql', mysql_params,
                                         base_project_exists, project_name, uid_type, ssl_params, 'ssl_authentication')
            else:
                generate_mysql_database_metadata('mysql', mysql_params, use_pascal_case, result_full_path)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mysql', mysql_params,
                                         base_project_exists, project_name, uid_type, db_authentication_method='direct_connection')
        except Exception as e:
            typer.echo(e)
            return

    elif postgres_connection_parameters:
        try:
            postgres_params = json.loads(postgres_connection_parameters)
            generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing PostgreSQL connection parameters: {e}")
            return

    elif postgres_connection_string:
        try:
            postgres_params = extract_postgres_params(postgres_connection_string)
            if ssh_password_authentication_string:
                ssh_params = extract_ssh_params(ssh_password_authentication_string)
                generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path, ssh_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'pgsql',
                                         postgres_params,
                                         base_project_exists, project_name, uid_type, ssh_params, 'ssh_password_authentication')
            elif ssh_publickey_authentication_string:
                ssh_publickey_params = extract_ssh_publickey_params(ssh_publickey_authentication_string)
                generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path,
                                                      ssh_publickey_params=ssh_publickey_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'pgsql',
                                         postgres_params,
                                         base_project_exists, project_name, uid_type, ssh_publickey_params, 'ssh_publickey_authentication')
            elif ssl_authentication_string:
                ssl_params = extract_ssl_params(ssl_authentication_string)
                generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path,
                                                      ssl_params=ssl_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'pgsql',
                                         postgres_params,
                                         base_project_exists, project_name, uid_type, ssl_params, 'ssl_authentication')
            else:
                generate_postgresql_database_metadata('pgsql', postgres_params, use_pascal_case, result_full_path)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'pgsql', postgres_params,
                                         base_project_exists, project_name, uid_type, db_authentication_method='direct_connection')
        except Exception as e:
            typer.echo(repr(e))
            return

    elif sqlserver_connection_parameters:
        try:
            sqlserver_params = json.loads(sqlserver_connection_parameters)
            generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing SQLServer connection parameters: {e}")
            return

    elif sqlserver_connection_string:
        try:
            sqlserver_params = extract_sqlserver_params(sqlserver_connection_string)
            if ssh_password_authentication_string:
                ssh_params = extract_ssh_params(ssh_password_authentication_string)
                generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path, ssh_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mssql',
                                         sqlserver_params,
                                         base_project_exists, project_name, uid_type, ssh_params, 'ssh_password_authentication')
            elif ssh_publickey_authentication_string:
                ssh_publickey_params = extract_ssh_publickey_params(ssh_publickey_authentication_string)
                generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path,
                                                     ssh_publickey_params=ssh_publickey_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mssql',
                                         sqlserver_params,
                                         base_project_exists, project_name, uid_type, ssh_publickey_params, 'ssh_publickey_authentication')
            elif ssl_authentication_string:
                ssl_params = extract_ssl_params(ssl_authentication_string)
                generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path,
                                                     ssl_params=ssl_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mssql',
                                         sqlserver_params,
                                         base_project_exists, project_name, uid_type, ssl_params, 'ssl_authentication')
            else:
                generate_sqlserver_database_metadata('mssql', sqlserver_params, use_pascal_case, result_full_path)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mssql', sqlserver_params,
                                         base_project_exists, project_name, uid_type, db_authentication_method='direct_connection')
        except Exception as e:
            typer.echo(e)
            return

    elif mariadb_connection_parameters:
        try:
            mariadb_params = json.loads(mariadb_connection_parameters)
            generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path)
        except Exception as e:
            typer.echo(f"Error parsing MariaDB connection parameters: {e}")
            return

    elif mariadb_connection_string:
        try:
            mariadb_params = extract_mariadb_params(mariadb_connection_string)
            if ssh_password_authentication_string:
                ssh_params = extract_ssh_params(ssh_password_authentication_string)
                generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path, ssh_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mariadb',
                                         mariadb_params,
                                         base_project_exists, project_name, uid_type, ssh_params, 'ssh_password_authentication')
            elif ssh_publickey_authentication_string:
                ssh_publickey_params = extract_ssh_publickey_params(ssh_publickey_authentication_string)
                generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path,
                                                 ssh_publickey_params=ssh_publickey_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mariadb',
                                         mariadb_params,
                                         base_project_exists, project_name, uid_type, ssh_publickey_params, 'ssh_publickey_authentication')
            elif ssl_authentication_string:
                ssl_params = extract_ssl_params(ssl_authentication_string)
                generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path,
                                                 ssl_params=ssl_params)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mariadb',
                                         mariadb_params,
                                         base_project_exists, project_name, uid_type, ssl_params, 'ssl_authentication')
            else:
                generate_mysql_database_metadata('mariadb', mariadb_params, use_pascal_case, result_full_path)
                # Python Domain Files Generation
                generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
                os.makedirs(generated_domains_path)
                generate_domain_files(result_full_path, generated_domains_path)
                # PythonRest API Generation
                generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, 'mariadb', mariadb_params,
                                         base_project_exists, project_name, uid_type, db_authentication_method='direct_connection')
        except Exception as e:
            typer.echo(e)
            return
    else:
        typer.echo("Please provide either MySQL, PostgreSQL, SQLServer, or MariaDB connection parameters or a connection string.")
        return


@app.command()
def version():
    typer.echo(f"pythonrest v{pythonrest_version}")


if __name__ == "__main__":
    app()
