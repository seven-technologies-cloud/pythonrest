import os
# from pathlib import Path # Not used
from databaseconnector.SqlServerMetadataGeneratorBuilder import (
    get_sqlserver_db_connection_with_ssl,
    get_sqlserver_db_connection_with_ssh_publickey,
    get_sqlserver_db_connection_with_ssh_password,
    get_sqlserver_connection,
    convert_retrieved_tuple_name_list_from_sqlserver,
    retrieve_table_name_tuple_list_from_connected_database,
    # New bulk functions
    retrieve_all_columns_metadata_bulk_sqlserver,
    retrieve_all_constraints_bulk_sqlserver
)
from databaseconnector.SqlServerTableColumnFieldData import SqlServerTableColumnFieldData
from databaseconnector.SqlServerTableColumnConstraintsData import SqlServerTableColumnConstraintsData
from databaseconnector.JSONDictHelper import (
    add_table_column_to_json_domain,
    add_table_constraint_to_json_domain,
    add_referenced_class_name_to_constraints
)
from databaseconnector.FilesHandler import get_domain_result_files, create_domain_result_file


def generate_sqlserver_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    json_generated_metadata_folder = os.path.join(generated_api_path, "JSONMetadata")
    os.makedirs(json_generated_metadata_folder, exist_ok=True)

    cursor = None
    try:
        db_server = project_database_data[f'{project_database}_host']
        db_port = project_database_data[f'{project_database}_port'] # Should be int for connect
        db_user = project_database_data[f'{project_database}_user']
        db_password = project_database_data[f'{project_database}_password']
        # SQL Server uses "database" for catalog, "schema" for schema (e.g., dbo)
        db_database_name = project_database_data[f'{project_database}_schema'] # This is likely the DB name (catalog)
        # Schema for SQL Server (like 'dbo') needs to be determined or passed if not default
        # For INFORMATION_SCHEMA queries, TABLE_SCHEMA is used.
        # Assuming project_database_data[f'{project_database}_schema_name'] or a default like 'dbo'
        db_schema_name = project_database_data.get(f'{project_database}_schema_name', 'dbo')


        if ssh_params_with_password:
            cursor = get_sqlserver_db_connection_with_ssh_password(
                db_server, db_port, db_user, db_password, db_database_name,
                ssh_params_with_password['ssh_host'],
                ssh_params_with_password['ssh_port'], # Already int in builder
                ssh_params_with_password['ssh_user'],
                ssh_params_with_password['ssh_password'],
                ssh_params_with_password['ssh_local_bind_port']) # Already int
        elif ssh_publickey_params:
            cursor = get_sqlserver_db_connection_with_ssh_publickey(
                db_server, db_port, db_user, db_password, db_database_name,
                ssh_publickey_params['ssh_host'],
                ssh_publickey_params['ssh_port'], # Already int
                ssh_publickey_params['ssh_user'],
                ssh_publickey_params['ssh_key_path'],
                ssh_publickey_params['ssh_local_bind_port']) # Already int
        elif ssl_params:
            cursor = get_sqlserver_db_connection_with_ssl(
                db_server, db_port, db_user, db_password, db_database_name,
                ssl_params.get('ssl_ca'), # Pass as None if not present
                ssl_params.get('ssl_cert'),
                ssl_params.get('ssl_key'),
                ssl_params.get('ssl_hostname', db_server)) # Use db_server if specific ssl_hostname not given
        else:
            cursor = get_sqlserver_connection(db_server, db_port, db_user, db_password, db_database_name)
    except Exception as e:
        print(f"Error connecting to SQL Server database: {e}")
        raise

    if not cursor:
        raise ConnectionError("Failed to establish SQL Server database connection.")

    table_name_list_of_dicts = retrieve_table_name_tuple_list_from_connected_database(cursor)
    converted_table_list_name = convert_retrieved_tuple_name_list_from_sqlserver(table_name_list_of_dicts)

    # Fetch all schema metadata in bulk
    all_columns_map = retrieve_all_columns_metadata_bulk_sqlserver(db_schema_name, cursor)
    pks_map, fks_map, uniques_map = retrieve_all_constraints_bulk_sqlserver(db_schema_name, cursor)

    for table_name in converted_table_list_name:
        create_domain_result_file(table_name, json_generated_metadata_folder, use_pascal_case)

        table_columns_data = all_columns_map.get(table_name, {})
        table_pks_list = pks_map.get(table_name, []) # List of PK column names for this table
        table_fks_dict = fks_map.get(table_name, {}) # Dict of {column_name: fk_details} for this table
        table_uniques_constraints = uniques_map.get(table_name, {}) # Dict of {constraint_name: [columns]}

        for column_name_key, col_bulk_data in table_columns_data.items():
            # Ensure column_name_key is actual column name, col_bulk_data is its dict
            actual_column_name = col_bulk_data['COLUMN_NAME']

            # 1. Prepare `column_metadata_for_class` (simulating old `column_metadata` structure)
            column_metadata_for_class = {
                'COLUMN_NAME': actual_column_name,
                'DATA_TYPE': col_bulk_data['DATA_TYPE'],
                'IS_NULLABLE': col_bulk_data['IS_NULLABLE'],
                'COLUMN_DEFAULT': col_bulk_data['COLUMN_DEFAULT'],
                'CHARACTER_MAXIMUM_LENGTH': col_bulk_data['CHARACTER_MAXIMUM_LENGTH'],
                'NUMERIC_PRECISION': col_bulk_data['NUMERIC_PRECISION'],
                'NUMERIC_SCALE': col_bulk_data['NUMERIC_SCALE'],
                'DATETIME_PRECISION': col_bulk_data['DATETIME_PRECISION']
                # IS_IDENTITY is in col_bulk_data directly from the bulk query
            }

            # 2. Prepare `primary_key_arg` (simulating old `primary_key_column`)
            # Old functions returned a list of dicts, or empty list.
            # The data class likely checks if this list is non-empty.
            is_primary = actual_column_name in table_pks_list
            primary_key_arg = [{'COLUMN_NAME': actual_column_name}] if is_primary else []

            # 3. Prepare `unique_arg` (simulating old `unique_column`)
            is_unique = False
            for unique_constraint_columns in table_uniques_constraints.values():
                if actual_column_name in unique_constraint_columns:
                    is_unique = True
                    break
            unique_arg = [{'COLUMN_NAME': actual_column_name}] if is_unique else []

            # 4. Prepare `identity_arg` (simulating old `auto_increment`)
            identity_arg = col_bulk_data.get('is_auto_increment', False) # Derived in bulk query

            # 5. Foreign Key Logic
            fk_details_from_bulk = table_fks_dict.get(actual_column_name)

            if fk_details_from_bulk:
                # Prepare `foreign_key_ref_arg` to match expected structure by SqlServerTableColumnConstraintsData
                # Old `retrieve_references_table_foreign_keys_from_tables_from_connected_database` returned a dict like:
                # {'FK_NAME': ..., 'table': ..., 'column': ..., 'referenced_table': ..., 'referenced_column': ...}
                # The new `fk_details_from_bulk` is:
                # {'referenced_table': ..., 'referenced_column': ..., 'constraint_name': ...}
                # We need to map this.
                foreign_key_ref_arg = {
                    'FK_NAME': fk_details_from_bulk['constraint_name'],
                    'table': table_name, # Current table
                    'column': actual_column_name, # Current column
                    'referenced_table': fk_details_from_bulk['referenced_table'],
                    'referenced_column': fk_details_from_bulk['referenced_column']
                    # Add 'schema_name' and 'referenced_schema_name' if SqlServerTableColumnConstraintsData needs them
                }

                column_constraint_dto = SqlServerTableColumnConstraintsData(
                    column_metadata_for_class,  # column_metadata
                    primary_key_arg,            # primary_key_column (list)
                    foreign_key_ref_arg,        # foreign_key_reference (dict)
                    unique_arg,                 # unique_column (list)
                    identity_arg                # auto_increment (bool)
                ).__dict__
                add_table_constraint_to_json_domain(
                    table_name, column_constraint_dto, json_generated_metadata_folder)
            else:
                column_metadata_dto = SqlServerTableColumnFieldData(
                    column_metadata_for_class,  # column_metadata
                    primary_key_arg,            # primary_key (list)
                    unique_arg,                 # unique (list)
                    identity_arg                # identity (bool)
                ).__dict__
                add_table_column_to_json_domain(
                    table_name, column_metadata_dto, json_generated_metadata_folder)

    domain_result_json_files = get_domain_result_files(json_generated_metadata_folder)
    for domain_result_json_file in domain_result_json_files:
        add_referenced_class_name_to_constraints(
            domain_result_json_file, domain_result_json_files, json_generated_metadata_folder)

    if cursor:
        if hasattr(cursor, 'close'):
            cursor.close()
        conn = getattr(cursor, 'connection', None)
        if conn and hasattr(conn, 'close'):
            conn.close()
        # SSH Tunnel closing logic would be needed here if tunnel object was stored and returned by connection functions
        # e.g., if hasattr(cursor, 'tunnel') and cursor.tunnel: cursor.tunnel.stop(); cursor.tunnel.close()
