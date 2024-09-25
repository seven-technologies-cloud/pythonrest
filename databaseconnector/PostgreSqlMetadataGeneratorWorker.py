import os
from databaseconnector.PostgreSqlMetadataGeneratorBuilder import *
from databaseconnector.PostgreSqlTableColumnFieldData import *
from databaseconnector.PostgreSqlTableColumnConstraintsData import *
from databaseconnector.JSONDictHelper import *
from databaseconnector.FilesHandler import get_domain_result_files


def generate_postgresql_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    json_generated_metadata_folder = os.path.join(generated_api_path, "JSONMetadata")
    os.makedirs(json_generated_metadata_folder)

    try:
        if ssh_params_with_password:
            connected_db = get_postgresql_db_connection_with_ssh_password(
                project_database_data[f'{project_database}_database_name'],
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
            connected_db = get_postgresql_db_connection_with_ssh_publickey(
                project_database_data[f'{project_database}_database_name'],
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
            connected_db = get_postgresql_db_connection_with_ssl(
                project_database_data[f'{project_database}_database_name'],
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
            connected_db = get_postgresql_db_connection(
                project_database_data[f'{project_database}_database_name'],
                project_database_data[f'{project_database}_host'],
                project_database_data[f'{project_database}_port'],
                project_database_data[f'{project_database}_user'],
                project_database_data[f'{project_database}_password'],
                project_database_data[f'{project_database}_schema'])
    except Exception as e:
        raise e

    tuple_table_names = retrieve_table_name_tuple_list_from_connected_schema(
        connected_db, project_database_data[f'{project_database}_schema'])

    table_names_list = convert_retrieved_table_name_tuple_list_from_connected_schema(
        tuple_table_names)

    for table in table_names_list:
        # Retrieving all column metadata
        columns_metadata = retrieve_table_field_metadata(
            table, project_database_data[f'{project_database}_schema'], connected_db)

        # All PK
        columns_constraint_primary_key = get_constraints_primary_keys(
            table, project_database_data[f'{project_database}_schema'], connected_db)

        # All FK
        columns_constraint_foreign_key = get_constraints_foreign_key(
            table, project_database_data[f'{project_database}_schema'], connected_db)

        # ALL UNIQUE
        columns_constraint_unique = get_constraints_unique(
            table, project_database_data[f'{project_database}_schema'], connected_db)

        create_domain_result_file(table, json_generated_metadata_folder, use_pascal_case)

        # Filling auto increment
        for column_metadata in columns_metadata:

            auto_increment_value = retrieve_auto_increment_from_column(
                column_metadata['column_name'], table, connected_db)

            column_metadata["auto_increment"] = auto_increment_value[0]['count']

        # Adding column to file
        for column_metadata in columns_metadata:
            pk_status = verify_column_is_pk(
                table, column_metadata, columns_constraint_primary_key)
            fk_status = verify_column_is_fk(
                table, column_metadata, columns_constraint_foreign_key)
            u_status = verify_column_is_unique(
                table, column_metadata, columns_constraint_unique)

            if fk_status:
                column_fk = get_column_fk(
                    table, column_metadata, columns_constraint_foreign_key)

                field_constraint = PostgreSqlTableColumnConstraintsData(
                    column_metadata, column_fk, pk_status, u_status).__dict__
                add_table_constraint_to_json_domain(
                    table, field_constraint, json_generated_metadata_folder)

            else:
                field_metadata_dict = PostgreSqlTableColumnFieldData(
                    column_metadata, pk_status, u_status).__dict__
                add_table_column_to_json_domain(
                    table, field_metadata_dict, json_generated_metadata_folder)

        domain_result_json_files = get_domain_result_files(
            json_generated_metadata_folder)
        for domain_result_json_file in domain_result_json_files:
            add_referenced_class_name_to_constraints(
                domain_result_json_file, domain_result_json_files, json_generated_metadata_folder)
