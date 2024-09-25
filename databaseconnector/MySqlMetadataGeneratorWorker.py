import os
from databaseconnector.MySqlMetadataGeneratorBuilder import *
from databaseconnector.MySqlTableColumnFieldData import *
from databaseconnector.MySqlTableColumnConstraintsData import *
from databaseconnector.JSONDictHelper import *
from databaseconnector.FilesHandler import get_domain_result_files


def generate_mysql_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    json_generated_metadata_folder = os.path.join(generated_api_path, "JSONMetadata")
    os.makedirs(json_generated_metadata_folder)

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

    for table_name in converted_table_name_list:
        create_domain_result_file(
            table_name, json_generated_metadata_folder, use_pascal_case)

        table_fields_metadata = retrieve_table_field_metadata(
            table_name, connected_schema)

        for column in table_fields_metadata:
            table_origin_foreign_key = retrieve_table_relative_column_constraints(
                column['Field'], table_name, project_database_data[f'{project_database}_schema'], connected_schema)

            if column['Field'] == table_origin_foreign_key.get('COLUMN_NAME'):
                table_origin_foreign_key = retrieve_table_relative_column_constraints(
                    column['Field'], table_name, project_database_data[f'{project_database}_schema'], connected_schema)
                table_constraints_data = MySqlTableColumnConstraintsData(
                    column, table_origin_foreign_key).__dict__
                add_table_constraint_to_json_domain(
                    table_name, table_constraints_data, json_generated_metadata_folder)

            else:
                mysql_field_data = MySqlTableColumnFieldData(column).__dict__
                add_table_column_to_json_domain(
                    table_name, mysql_field_data, json_generated_metadata_folder)
    domain_result_json_files = get_domain_result_files(json_generated_metadata_folder)
    for domain_result_json_file in domain_result_json_files:
        add_referenced_class_name_to_constraints(domain_result_json_file, domain_result_json_files, json_generated_metadata_folder)
