import os
from pathlib import Path # Import Path
from databaseconnector.MySqlMetadataGeneratorBuilder import *
from databaseconnector.MySqlTableColumnFieldData import *
from databaseconnector.MySqlTableColumnConstraintsData import *
from databaseconnector.JSONDictHelper import *
from databaseconnector.FilesHandler import get_domain_result_files


def generate_mysql_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path_str, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    generated_api_path = Path(generated_api_path_str) # Convert to Path
    json_generated_metadata_folder_path = generated_api_path / "JSONMetadata" # Use Path object

    # Use pathlib to create directories
    json_generated_metadata_folder_path.mkdir(parents=True, exist_ok=True)

    try:
        if ssh_params_with_password:
            connected_schema = get_mysql_db_connection_with_ssh_password(
                project_database_data[f'{project_database}_host'],
                int(project_database_data[f'{project_database}_port']),
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'],
                ssh_params_with_password['ssh_host'],
                int(ssh_params_with_password['ssh_port']),
                ssh_params_with_password['ssh_user'],
                ssh_params_with_password['ssh_password'],
                ssh_params_with_password['ssh_local_bind_port'])
        elif ssh_publickey_params:
            connected_schema = get_mysql_db_connection_with_ssh_publickey(
                project_database_data[f'{project_database}_host'],
                int(project_database_data[f'{project_database}_port']),
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'],
                ssh_publickey_params['ssh_host'],
                int(ssh_publickey_params['ssh_port']),
                ssh_publickey_params['ssh_user'],
                ssh_publickey_params['ssh_key_path'],
                ssh_publickey_params['ssh_local_bind_port'])
        elif ssl_params:
            connected_schema = get_mysql_db_connection_with_ssl(
                project_database_data[f'{project_database}_host'],
                int(project_database_data[f'{project_database}_port']),
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'],
                ssl_params['ssl_ca'],
                ssl_params['ssl_cert'],
                ssl_params['ssl_key'],
                ssl_params['ssl_hostname'])
        else:
            connected_schema = get_mysql_db_connection(
                project_database_data[f'{project_database}_host'],
                int(project_database_data[f'{project_database}_port']),
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'])
    except Exception as e:
        raise e

    tuple_name_list = retrieve_table_name_tuple_list_from_connected_schema(
        connected_schema)

    converted_table_name_list = convert_retrieved_table_name_tuple_list_from_connected_schema(
        tuple_name_list)

    # Hoist schema name lookup out of the loop
    db_schema_name = project_database_data[f'{project_database}_schema']

    for table_name in converted_table_name_list:
        create_domain_result_file(
            table_name, str(json_generated_metadata_folder_path), use_pascal_case) # Convert Path to string

        table_fields_metadata = retrieve_table_field_metadata(
            table_name, connected_schema)

        for column in table_fields_metadata:
            table_origin_foreign_key = retrieve_table_relative_column_constraints(
                column['Field'], table_name, db_schema_name, connected_schema)

            if column['Field'] == table_origin_foreign_key.get('COLUMN_NAME'):
                # The second call to retrieve_table_relative_column_constraints was redundant
                # as table_origin_foreign_key is already populated with the same data.
                table_constraints_data = MySqlTableColumnConstraintsData(
                    column, table_origin_foreign_key).__dict__
                add_table_constraint_to_json_domain(
                    table_name, table_constraints_data, str(json_generated_metadata_folder_path)) # Convert Path to string

            else:
                mysql_field_data = MySqlTableColumnFieldData(column).__dict__
                add_table_column_to_json_domain(
                    table_name, mysql_field_data, str(json_generated_metadata_folder_path)) # Convert Path to string

    domain_result_json_files = get_domain_result_files(str(json_generated_metadata_folder_path)) # Convert Path to string
    for domain_result_json_file in domain_result_json_files:
        add_referenced_class_name_to_constraints(domain_result_json_file, domain_result_json_files, str(json_generated_metadata_folder_path)) # Convert Path to string
