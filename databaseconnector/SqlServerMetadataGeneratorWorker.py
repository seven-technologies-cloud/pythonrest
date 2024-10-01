import os
from databaseconnector.SqlServerMetadataGeneratorBuilder import *
from databaseconnector.SqlServerTableColumnFieldData import *
from databaseconnector.SqlServerTableColumnConstraintsData import *
from databaseconnector.JSONDictHelper import *
from databaseconnector.FilesHandler import get_domain_result_files


def generate_sqlserver_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    json_generated_metadata_folder = os.path.join(generated_api_path, "JSONMetadata")
    os.makedirs(json_generated_metadata_folder)

    try:
        if ssh_params_with_password:
            cursor = get_sqlserver_db_connection_with_ssh_password(
                project_database_data[f'{project_database}_host'],
                project_database_data[f'{project_database}_port'],
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'],
                ssh_params_with_password['ssh_host'],
                int(ssh_params_with_password['ssh_port']),
                ssh_params_with_password['ssh_user'],
                ssh_params_with_password['ssh_password'],
                ssh_params_with_password['ssh_local_bind_port'])
        elif ssh_publickey_params:
            cursor = get_sqlserver_db_connection_with_ssh_publickey(
                project_database_data[f'{project_database}_host'],
                project_database_data[f'{project_database}_port'],
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'],
                ssh_publickey_params['ssh_host'],
                int(ssh_publickey_params['ssh_port']),
                ssh_publickey_params['ssh_user'],
                ssh_publickey_params['ssh_key_path'],
                ssh_publickey_params['ssh_local_bind_port'])
        elif ssl_params:
            cursor = get_sqlserver_db_connection_with_ssl(
                project_database_data[f'{project_database}_host'],
                project_database_data[f'{project_database}_port'],
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'],
                ssl_params['ssl_ca'],
                ssl_params['ssl_cert'],
                ssl_params['ssl_key'],
                ssl_params['ssl_hostname'])
        else:
            cursor = get_sqlserver_connection(project_database_data[f'{project_database}_host'],
                                              project_database_data[f'{project_database}_port'],
                                              project_database_data[f'{project_database}_user'],
                                              project_database_data[f'{project_database}_password'],
                                              project_database_data[f'{project_database}_schema'])
    except Exception as e:
        raise e

    table_name_tuple_list = retrieve_table_name_tuple_list_from_connected_database(cursor)

    converted_table_list_name = convert_retrieved_tuple_name_list_from_sqlserver(
        table_name_tuple_list)

    for table_name in converted_table_list_name:
        create_domain_result_file(table_name, json_generated_metadata_folder, use_pascal_case)
        table_columns_metadata = retrieve_table_columns_from_connected_database(table_name, cursor)
        for column_metadata in table_columns_metadata:
            primary_key_column = retrieve_table_primary_key_from_connected_database(
                column_metadata['COLUMN_NAME'], table_name, cursor)
            foreign_key_column = retrieve_table_foreign_key_from_connected_database(
                column_metadata['COLUMN_NAME'], table_name, cursor)
            unique_column = retrieve_table_unique_from_connected_database(
                column_metadata['COLUMN_NAME'], table_name, cursor)
            auto_increment = retrieve_table_auto_incremente_from_connected_database(
                column_metadata['COLUMN_NAME'], table_name, cursor)

            if foreign_key_column == list():
                column_metadata_dto = SqlServerTableColumnFieldData(
                    column_metadata, primary_key_column, unique_column, auto_increment).__dict__
                add_table_column_to_json_domain(
                    table_name, column_metadata_dto, json_generated_metadata_folder)
            else:
                foreign_key_reference = retrieve_references_table_foreign_keys_from_tables_from_connected_database(
                    column_metadata['COLUMN_NAME'], table_name, cursor)
                column_constraint_dto = SqlServerTableColumnConstraintsData(column_metadata, primary_key_column,
                                                                foreign_key_reference, unique_column,
                                                                auto_increment).__dict__
                add_table_constraint_to_json_domain(
                    table_name, column_constraint_dto, json_generated_metadata_folder)

        domain_result_json_files = get_domain_result_files(json_generated_metadata_folder)
        for domain_result_json_file in domain_result_json_files:
            add_referenced_class_name_to_constraints(
                domain_result_json_file, domain_result_json_files, json_generated_metadata_folder)
