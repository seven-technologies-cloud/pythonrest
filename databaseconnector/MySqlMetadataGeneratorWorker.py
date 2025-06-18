import os
from pathlib import Path
from databaseconnector.MySqlMetadataGeneratorBuilder import (
    get_mysql_db_connection_with_ssh_password,
    get_mysql_db_connection_with_ssh_publickey,
    get_mysql_db_connection_with_ssl,
    get_mysql_db_connection,
    retrieve_table_name_tuple_list_from_connected_schema,
    convert_retrieved_table_name_tuple_list_from_connected_schema,
    # New bulk functions
    retrieve_all_columns_metadata_bulk,
    retrieve_all_foreign_keys_bulk,
    retrieve_all_primary_keys_bulk
    # retrieve_all_unique_constraints_bulk # Not strictly needed if COLUMN_KEY from COLUMNS is sufficient
)
from databaseconnector.MySqlTableColumnFieldData import MySqlTableColumnFieldData
from databaseconnector.MySqlTableColumnConstraintsData import MySqlTableColumnConstraintsData
from databaseconnector.JSONDictHelper import (
    add_table_column_to_json_domain,
    add_table_constraint_to_json_domain,
    add_referenced_class_name_to_constraints
)
from databaseconnector.FilesHandler import get_domain_result_files, create_domain_result_file


def generate_mysql_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path_str, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    generated_api_path = Path(generated_api_path_str)
    json_generated_metadata_folder_path = generated_api_path / "JSONMetadata"
    json_generated_metadata_folder_path.mkdir(parents=True, exist_ok=True)

    connected_schema = None # Ensure it's defined for finally block if needed
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

    if not connected_schema:
        raise ConnectionError("Failed to establish database connection.")

    tuple_name_list = retrieve_table_name_tuple_list_from_connected_schema(connected_schema)
    converted_table_name_list = convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_name_list)
    db_schema_name = project_database_data[f'{project_database}_schema']

    # Fetch all schema metadata in bulk
    all_columns_map = retrieve_all_columns_metadata_bulk(db_schema_name, connected_schema)
    all_fks_map = retrieve_all_foreign_keys_bulk(db_schema_name, connected_schema)

    for table_name in converted_table_name_list:
        create_domain_result_file(table_name, str(json_generated_metadata_folder_path), use_pascal_case)

        table_columns_data = all_columns_map.get(table_name, {})
        table_fks_data = all_fks_map.get(table_name, {})

        for column_name, col_bulk_data in table_columns_data.items():
            # Prepare current_column_info dictionary to match structure expected by Data classes
            current_column_info = {
                'Field': col_bulk_data['COLUMN_NAME'],
                'Type': col_bulk_data['COLUMN_TYPE'],
                'Null': 'NO' if col_bulk_data['IS_NULLABLE'] == 'NO' else 'YES',
                'Key': col_bulk_data['COLUMN_KEY'],
                'Default': col_bulk_data['COLUMN_DEFAULT'],
                'Extra': col_bulk_data['EXTRA']
            }

            fk_details_for_this_column = table_fks_data.get(column_name)

            if fk_details_for_this_column:
                foreign_key_constructor_arg = {
                    'COLUMN_NAME': column_name,
                    'REFERENCED_TABLE_NAME': fk_details_for_this_column['REFERENCED_TABLE_NAME'],
                    'REFERENCED_COLUMN_NAME': fk_details_for_this_column['REFERENCED_COLUMN_NAME'],
                    'CONSTRAINT_NAME': fk_details_for_this_column.get('CONSTRAINT_NAME')
                }

                table_constraints_data = MySqlTableColumnConstraintsData(
                    current_column_info,
                    foreign_key_constructor_arg
                ).__dict__
                add_table_constraint_to_json_domain(
                    table_name, table_constraints_data, str(json_generated_metadata_folder_path))
            else:
                mysql_field_data = MySqlTableColumnFieldData(current_column_info).__dict__
                add_table_column_to_json_domain(
                    table_name, mysql_field_data, str(json_generated_metadata_folder_path))

    domain_result_json_files = get_domain_result_files(str(json_generated_metadata_folder_path))
    for domain_result_json_file in domain_result_json_files:
        add_referenced_class_name_to_constraints(domain_result_json_file, domain_result_json_files, str(json_generated_metadata_folder_path))
