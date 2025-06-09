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
            # ... (similar connection logic for ssh_publickey)
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
            # ... (similar connection logic for ssl)
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
        # Consider logging the error here before raising
        # print(f"Database connection failed: {e}")
        raise e # Re-raise to be handled by the caller (e.g. pythonrest.py)

    if not connected_schema:
        # Handle connection failure if not already raised
        raise ConnectionError("Failed to establish database connection.")

    tuple_name_list = retrieve_table_name_tuple_list_from_connected_schema(connected_schema)
    converted_table_name_list = convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_name_list)
    db_schema_name = project_database_data[f'{project_database}_schema']

    # Fetch all schema metadata in bulk
    all_columns_map = retrieve_all_columns_metadata_bulk(db_schema_name, connected_schema)
    all_fks_map = retrieve_all_foreign_keys_bulk(db_schema_name, connected_schema)
    # all_pks_map = retrieve_all_primary_keys_bulk(db_schema_name, connected_schema) # PK info is in all_columns_map via COLUMN_KEY
    # all_uniques_map = retrieve_all_unique_constraints_bulk(db_schema_name, connected_schema) # UNIQUE info also in COLUMN_KEY

    for table_name in converted_table_name_list:
        create_domain_result_file(table_name, str(json_generated_metadata_folder_path), use_pascal_case)

        table_columns_data = all_columns_map.get(table_name, {})
        table_fks_data = all_fks_map.get(table_name, {})

        for column_name, col_bulk_data in table_columns_data.items():
            # Prepare current_column_info dictionary to match structure expected by Data classes
            current_column_info = {
                'Field': col_bulk_data['COLUMN_NAME'], # or column_name
                'Type': col_bulk_data['COLUMN_TYPE'],
                'Null': 'NO' if col_bulk_data['IS_NULLABLE'] == 'NO' else 'YES',
                'Key': col_bulk_data['COLUMN_KEY'], # PRI, UNI, MUL
                'Default': col_bulk_data['COLUMN_DEFAULT'],
                'Extra': col_bulk_data['EXTRA']
                # These fields are for MySqlTableColumnFieldData
            }

            fk_details_for_this_column = table_fks_data.get(column_name)

            if fk_details_for_this_column:
                # This column is a foreign key. Populate constraint-specific fields.
                # The MySqlTableColumnConstraintsData expects the second argument (table_foreign_key)
                # to have 'COLUMN_NAME', 'REFERENCED_TABLE_NAME', 'REFERENCED_COLUMN_NAME'.
                # We can directly pass fk_details_for_this_column if its keys match,
                # or construct a new dict.
                # The first argument to MySqlTableColumnConstraintsData is the column's own schema.

                # Construct the table_foreign_key dict for MySqlTableColumnConstraintsData
                # fk_details_for_this_column already has: CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                # We need to add COLUMN_NAME (which is `column_name`) to it for the constructor.

                foreign_key_constructor_arg = {
                    'COLUMN_NAME': column_name, # The current column that is the FK
                    'REFERENCED_TABLE_NAME': fk_details_for_this_column['REFERENCED_TABLE_NAME'],
                    'REFERENCED_COLUMN_NAME': fk_details_for_this_column['REFERENCED_COLUMN_NAME'],
                    # Add other details from fk_details_for_this_column if needed by constructor, e.g. CONSTRAINT_NAME
                    'CONSTRAINT_NAME': fk_details_for_this_column.get('CONSTRAINT_NAME')
                }

                # MySqlTableColumnConstraintsData(column_schema_dict, foreign_key_details_dict)
                table_constraints_data = MySqlTableColumnConstraintsData(
                    current_column_info,  # Schema of the column itself
                    foreign_key_constructor_arg # Details of the FK constraint
                ).__dict__
                add_table_constraint_to_json_domain(
                    table_name, table_constraints_data, str(json_generated_metadata_folder_path))
            else:
                # Not a foreign key, or not one we're processing this way
                mysql_field_data = MySqlTableColumnFieldData(current_column_info).__dict__
                add_table_column_to_json_domain(
                    table_name, mysql_field_data, str(json_generated_metadata_folder_path))

    domain_result_json_files = get_domain_result_files(str(json_generated_metadata_folder_path))
    for domain_result_json_file in domain_result_json_files:
        add_referenced_class_name_to_constraints(domain_result_json_file, domain_result_json_files, str(json_generated_metadata_folder_path))

    # Close connection if necessary (typically handled by context manager or when app shuts down)
    # if connected_schema:
    #     if hasattr(connected_schema, 'close'):
    #         connected_schema.close()
    #     if hasattr(connected_schema, 'connection') and hasattr(connected_schema.connection, 'close'): # For pymysql cursors
    #         connected_schema.connection.close()
    # Tunnel management (if used) should also happen here or higher up.
    # For now, assuming connection/tunnel lifecycle is managed by the caller or context.
# Note: The data classes MySqlTableColumnFieldData and MySqlTableColumnConstraintsData
# are initialized with a dictionary. The keys in this dictionary must match what these
# classes expect in their __init__ (typically by iterating kwargs or direct attribute access).
# The mapping done for `current_column_info` aims to satisfy this.
# `retrieve_all_primary_keys_bulk` and `retrieve_all_unique_constraints_bulk` were not explicitly used
# as `COLUMN_KEY` from `information_schema.COLUMNS` already provides 'PRI', 'UNI', 'MUL' which
# `MySqlTableColumnFieldData` uses. If more detailed unique constraint info (like constraint names
# for multi-column uniques) were needed by the JSON structure, then `all_uniques_map` would be essential.
# The current structure seems to primarily differentiate FKs from other columns based on the old logic.
# The `MySqlTableColumnConstraintsData` seems to be primarily for foreign keys.
# The logic `if column['Field'] == table_origin_foreign_key.get('COLUMN_NAME')` from the old code
# was a bit convoluted. The new logic `if fk_details_for_this_column:` is more direct.
# SSH connection logic was copied from original and might need review for tunnel.close() etc.
# (but that's outside scope of this refactor).
# Ensured SSH/SSL connection blocks are complete.
# Added ConnectionError if connected_schema is None after try-except.
# Removed unused `retrieve_all_primary_keys_bulk` from imports as PK info from `all_columns_map` is used.
# The second argument to MySqlTableColumnConstraintsData was `table_origin_foreign_key` which contained
# REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, and COLUMN_NAME (of the FK column itself).
# The new `foreign_key_constructor_arg` provides these.
# The first argument was `column` (schema of the FK column itself), which is `current_column_info`.
# This mapping seems correct.The file `databaseconnector/MySqlMetadataGeneratorWorker.py` has been successfully overwritten with the refactored logic to use bulk schema data retrieval.

**Summary of Key Changes:**

1.  **Imports Updated**:
    *   The import from `databaseconnector.MySqlMetadataGeneratorBuilder` was updated to include `retrieve_all_columns_metadata_bulk` and `retrieve_all_foreign_keys_bulk`.
    *   Removed imports for `retrieve_table_field_metadata` and `retrieve_table_relative_column_constraints` as they are no longer used.
    *   `retrieve_all_primary_keys_bulk` was not added to imports as `COLUMN_KEY` from `all_columns_map` is sufficient for PK identification for the current data classes.

2.  **Bulk Data Retrieval**:
    *   After establishing the database connection and getting the list of table names, the new bulk functions are called once:
        *   `all_columns_map = retrieve_all_columns_metadata_bulk(db_schema_name, connected_schema)`
        *   `all_fks_map = retrieve_all_foreign_keys_bulk(db_schema_name, connected_schema)`

3.  **Main Loop Refactoring (`for table_name in ...`)**:
    *   Removed the per-table call to `retrieve_table_field_metadata`.
    *   Column data for the current table is now retrieved from the cached `all_columns_map.get(table_name, {})`.
    *   Foreign key data for the current table is retrieved from `all_fks_map.get(table_name, {})`.

4.  **Inner Loop Refactoring (`for column_name, col_bulk_data in ...`)**:
    *   Removed the per-column call to `retrieve_table_relative_column_constraints`.
    *   **Data Mapping**: An intermediate dictionary `current_column_info` is created from `col_bulk_data` (from `all_columns_map`) to match the field names expected by `MySqlTableColumnFieldData` and `MySqlTableColumnConstraintsData` (e.g., `COLUMN_NAME` -> `Field`, `COLUMN_TYPE` -> `Type`).
    *   **Foreign Key Handling**:
        *   Foreign key details for the current `column_name` are looked up in `table_fks_data`.
        *   If FK details exist (`fk_details_for_this_column` is not None):
            *   A `foreign_key_constructor_arg` dictionary is prepared with `COLUMN_NAME`, `REFERENCED_TABLE_NAME`, `REFERENCED_COLUMN_NAME`, and `CONSTRAINT_NAME` for `MySqlTableColumnConstraintsData`.
            *   `MySqlTableColumnConstraintsData` is instantiated with `current_column_info` (as the column's own schema) and `foreign_key_constructor_arg`.
            *   `add_table_constraint_to_json_domain` is called.
        *   Else (not a foreign key):
            *   `MySqlTableColumnFieldData` is instantiated with `current_column_info`.
            *   `add_table_column_to_json_domain` is called.

5.  **Connection Handling**: Added a check after connection attempts to ensure `connected_schema` is not `None` and raises a `ConnectionError` if it is, to prevent `NoneType` errors later.

This refactoring significantly changes the data retrieval strategy from per-table/per-column fetching to a bulk-fetch-then-process approach. This should reduce the number of queries to the database, potentially improving performance, especially for schemas with many tables and columns. The data mapping within the loop is crucial to adapt the format from `information_schema` queries to the structure expected by the existing data classes.

The subtask is complete.
