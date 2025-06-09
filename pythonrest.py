#!/usr/bin/env python

import os
from typing import Optional
import typer
import json
import sys
from databaseconnector.RegexHandler import (
    extract_mysql_params, extract_postgres_params,
    extract_sqlserver_params, extract_mariadb_params,
    extract_ssh_params, extract_ssh_publickey_params, extract_ssl_params
) # Assuming these are correctly imported now
from databaseconnector.FilesHandler import check_if_provided_directory_is_unsafe, check_if_current_working_directory_is_unsafe, check_if_given_result_path_is_unsafe
from databaseconnector.MySqlMetadataGeneratorWorker import generate_mysql_database_metadata
from databaseconnector.PostgreSqlMetadataGeneratorWorker import generate_postgresql_database_metadata
from databaseconnector.SqlServerMetadataGeneratorWorker import generate_sqlserver_database_metadata
from domaingenerator.DomainFilesGeneratorWorker import generate_domain_files
from apigenerator.b_Workers.DirectoryManager import check_if_base_project_exists
from apigenerator.b_Workers.ApiGeneratorWorker import generate_python_rest_api
from apigenerator.e_Enumerables.Enumerables import get_directory_data


app = typer.Typer()
pythonrest_version = "0.3.2"


def _execute_generation_workflow(
    project_database_for_metadata: str,
    db_type_for_api_gen: str,
    db_connection_params: dict,
    metadata_generator_func,
    use_pascal_case: bool,
    result_full_path: str,
    us_datetime: bool,
    base_project_exists: bool,
    project_name: str,
    uid_type: str,
    ssh_password_params: Optional[dict] = None,
    ssh_publickey_params: Optional[dict] = None,
    ssl_params: Optional[dict] = None,
    # secure_connection_params_for_api_gen will be one of the above ssh/ssl_params
    secure_connection_params_for_api_gen: Optional[dict] = None,
    db_authentication_method_for_api_gen: str = 'direct_connection'
):
    """
    Internal helper to encapsulate the common API generation steps.
    """
    # 1. Call metadata generator
    # The metadata_generator_func needs specific keyword arguments for ssh/ssl
    if ssh_password_params:
        metadata_generator_func(
            project_database_for_metadata, db_connection_params, use_pascal_case, result_full_path,
            ssh_params_with_password=ssh_password_params # Specific kwarg for metadata generator
        )
    elif ssh_publickey_params:
        metadata_generator_func(
            project_database_for_metadata, db_connection_params, use_pascal_case, result_full_path,
            ssh_publickey_params=ssh_publickey_params # Specific kwarg for metadata generator
        )
    elif ssl_params:
        metadata_generator_func(
            project_database_for_metadata, db_connection_params, use_pascal_case, result_full_path,
            ssl_params=ssl_params # Specific kwarg for metadata generator
        )
    else: # Direct connection
        metadata_generator_func(project_database_for_metadata, db_connection_params, use_pascal_case, result_full_path)

    # 2. Create PythonGeneratedDomain directory
    generated_domains_path = os.path.join(result_full_path, 'PythonGeneratedDomain')
    os.makedirs(generated_domains_path, exist_ok=True)

    # 3. Call generate_domain_files
    generate_domain_files(result_full_path, generated_domains_path)

    # 4. Call generate_python_rest_api
    generate_python_rest_api(
        result_full_path,
        generated_domains_path,
        us_datetime,
        db_type_for_api_gen,
        db_connection_params,
        base_project_exists,
        project_name,
        uid_type,
        secure_connection_params_for_api_gen, # This will be the dict for ssh_params or ssl_params
        db_authentication_method_for_api_gen
    )


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
    # Initial path and safety checks (remains the same)
    if sum(bool(p) for p in [
        (mysql_connection_string or mysql_connection_parameters),
        (postgres_connection_string or postgres_connection_parameters),
        (sqlserver_connection_string or sqlserver_connection_parameters),
        (mariadb_connection_string or mariadb_connection_parameters)
    ]) > 1:
        typer.echo("Please specify only one of: MySQL, PostgreSQL, SQLServer, or MariaDB.")
        return

    if result_path:
        if check_if_given_result_path_is_unsafe(result_path):
            typer.echo(f"Error: Given result path {result_path} is unsafe, API generation aborted!")
            return
        # Correct path joining, ensuring only one suffix is added
        if not result_path.endswith(get_directory_data()['result_path_suffix']):
            result_path = os.path.join(result_path, get_directory_data()['result_path_suffix'])
    else:
        result_path = get_directory_data()['result_path_suffix']

    result_full_path = os.path.abspath(os.path.join(os.getenv('PWD', os.getcwd()), result_path))

    if check_if_current_working_directory_is_unsafe(os.getenv('PWD', os.getcwd())):
        typer.echo(f"Error: pythonrest is running from an unsafe directory: {os.getenv('PWD', os.getcwd())}, API generation aborted!")
        return
    if check_if_provided_directory_is_unsafe(result_full_path): # Check after abspath
        typer.echo(f"Error: Unsafe directory {result_full_path} was provided, API generation aborted!")
        return

    typer.echo(f"API will be generated on this path: {result_full_path}")

    if not os.path.exists(result_full_path):
        os.makedirs(result_full_path)
        base_project_exists = False
    else:
        base_project_exists = check_if_base_project_exists(result_full_path)
        if not base_project_exists and len(os.listdir(result_full_path)) != 0:
            typer.echo(f"Folder {result_full_path} is not empty: {json.dumps(os.listdir(result_full_path), indent=4)}")
            return

    # Consolidate parameter extraction and workflow call
    db_params = None
    metadata_generator = None
    project_db_for_meta = None # For metadata func (e.g. 'mysql', 'mariadb', 'pgsql', 'mssql')
    db_type_for_api = None   # For API generator (e.g. 'mysql', 'mariadb', 'pgsql', 'mssql')

    # Secure connection parameters
    ssh_pwd_params = None
    ssh_key_params = None
    ssl_gen_params = None

    # These will be passed to the workflow helper for metadata generation step
    active_ssh_password_params_for_metadata = None
    active_ssh_publickey_params_for_metadata = None
    active_ssl_params_for_metadata = None

    # This will be the one active set of SSH/SSL params for API generation step
    active_secure_connection_params_for_api_gen = None
    api_gen_auth_method_string = 'direct_connection'

    try:
        if ssh_password_authentication_string:
            ssh_pwd_params = extract_ssh_params(ssh_password_authentication_string)
            active_ssh_password_params_for_metadata = ssh_pwd_params
            active_secure_connection_params_for_api_gen = ssh_pwd_params
            api_gen_auth_method_string = 'ssh_password_authentication'
        elif ssh_publickey_authentication_string:
            ssh_key_params = extract_ssh_publickey_params(ssh_publickey_authentication_string)
            active_ssh_publickey_params_for_metadata = ssh_key_params
            active_secure_connection_params_for_api_gen = ssh_key_params
            api_gen_auth_method_string = 'ssh_publickey_authentication'
        elif ssl_authentication_string:
            ssl_gen_params = extract_ssl_params(ssl_authentication_string)
            active_ssl_params_for_metadata = ssl_gen_params
            active_secure_connection_params_for_api_gen = ssl_gen_params
            api_gen_auth_method_string = 'ssl_authentication'

        if mysql_connection_parameters:
            db_params = json.loads(mysql_connection_parameters)
            metadata_generator = generate_mysql_database_metadata
            project_db_for_meta = 'mysql'
            db_type_for_api = 'mysql'
        elif mysql_connection_string:
            db_params = extract_mysql_params(mysql_connection_string)
            metadata_generator = generate_mysql_database_metadata
            project_db_for_meta = 'mysql'
            db_type_for_api = 'mysql'
        elif postgres_connection_parameters:
            db_params = json.loads(postgres_connection_parameters)
            metadata_generator = generate_postgresql_database_metadata
            project_db_for_meta = 'pgsql'
            db_type_for_api = 'pgsql'
        elif postgres_connection_string:
            db_params = extract_postgres_params(postgres_connection_string)
            metadata_generator = generate_postgresql_database_metadata
            project_db_for_meta = 'pgsql'
            db_type_for_api = 'pgsql'
        elif sqlserver_connection_parameters:
            db_params = json.loads(sqlserver_connection_parameters)
            metadata_generator = generate_sqlserver_database_metadata
            project_db_for_meta = 'mssql'
            db_type_for_api = 'mssql'
        elif sqlserver_connection_string:
            db_params = extract_sqlserver_params(sqlserver_connection_string)
            metadata_generator = generate_sqlserver_database_metadata
            project_db_for_meta = 'mssql'
            db_type_for_api = 'mssql'
        elif mariadb_connection_parameters:
            db_params = json.loads(mariadb_connection_parameters)
            metadata_generator = generate_mysql_database_metadata # Uses MySQL metadata generator
            project_db_for_meta = 'mariadb' # But identifies as MariaDB for the function
            db_type_for_api = 'mariadb'     # And for API generation
        elif mariadb_connection_string:
            db_params = extract_mariadb_params(mariadb_connection_string)
            metadata_generator = generate_mysql_database_metadata # Uses MySQL metadata generator
            project_db_for_meta = 'mariadb' # But identifies as MariaDB for the function
            db_type_for_api = 'mariadb'     # And for API generation
        else:
            typer.echo("Please provide database connection parameters or a connection string.")
            return

        # Call the centralized workflow
        _execute_generation_workflow(
            project_database_for_metadata=project_db_for_meta,
            db_type_for_api_gen=db_type_for_api,
            db_connection_params=db_params,
            metadata_generator_func=metadata_generator,
            use_pascal_case=use_pascal_case,
            result_full_path=result_full_path,
            us_datetime=us_datetime,
            base_project_exists=base_project_exists,
            project_name=project_name,
            uid_type=uid_type,
            ssh_password_params=active_ssh_password_params_for_metadata, # Pass specific for metadata
            ssh_publickey_params=active_ssh_publickey_params_for_metadata, # Pass specific for metadata
            ssl_params=active_ssl_params_for_metadata, # Pass specific for metadata
            secure_connection_params_for_api_gen=active_secure_connection_params_for_api_gen, # Pass generic for API
            db_authentication_method_for_api_gen=api_gen_auth_method_string
        )
        typer.echo(f"PythonREST API '{project_name}' for {db_type_for_api.upper()} generated successfully at {result_full_path}!")

    except Exception as e:
        typer.echo(f"An error occurred: {repr(e)}") # Use repr(e) for more details potentially
        # Consider removing result_full_path if generation failed partway
        # shutil.rmtree(result_full_path, ignore_errors=True) # Example cleanup
        return


@app.command()
def version():
    typer.echo(f"pythonrest v{pythonrest_version}")


if __name__ == "__main__":
    app()
