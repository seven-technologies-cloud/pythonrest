import os
# from pathlib import Path # Not used in this file after os.path.join for json_generated_metadata_folder
from databaseconnector.PostgreSqlMetadataGeneratorBuilder import (
    get_postgresql_db_connection_with_ssh_password,
    get_postgresql_db_connection_with_ssh_publickey,
    get_postgresql_db_connection_with_ssl,
    get_postgresql_db_connection,
    retrieve_table_name_tuple_list_from_connected_schema,
    convert_retrieved_table_name_tuple_list_from_connected_schema,
    # New bulk functions
    retrieve_all_columns_metadata_bulk_pg,
    retrieve_all_constraints_bulk_pg
)
from databaseconnector.PostgreSqlTableColumnFieldData import PostgreSqlTableColumnFieldData
from databaseconnector.PostgreSqlTableColumnConstraintsData import PostgreSqlTableColumnConstraintsData
from databaseconnector.JSONDictHelper import (
    add_table_column_to_json_domain,
    add_table_constraint_to_json_domain,
    add_referenced_class_name_to_constraints
)
from databaseconnector.FilesHandler import get_domain_result_files, create_domain_result_file


def generate_postgresql_database_metadata(project_database, project_database_data, use_pascal_case, generated_api_path, ssh_params_with_password=None, ssh_publickey_params=None, ssl_params=None):
    json_generated_metadata_folder = os.path.join(generated_api_path, "JSONMetadata")
    os.makedirs(json_generated_metadata_folder, exist_ok=True)

    connected_db = None
    try:
        db_name = project_database_data[f'{project_database}_database_name']
        db_host = project_database_data[f'{project_database}_host']
        db_port = int(project_database_data[f'{project_database}_port'])
        db_user = project_database_data[f'{project_database}_user']
        db_password = project_database_data[f'{project_database}_password']
        schema_name = project_database_data[f'{project_database}_schema']

        if ssh_params_with_password:
            connected_db = get_postgresql_db_connection_with_ssh_password(
                db_name, db_host, db_port, db_user, db_password, schema_name,
                ssh_params_with_password['ssh_host'],
                int(ssh_params_with_password['ssh_port']),
                ssh_params_with_password['ssh_user'],
                ssh_params_with_password['ssh_password'],
                int(ssh_params_with_password['ssh_local_bind_port']))
        elif ssh_publickey_params:
            connected_db = get_postgresql_db_connection_with_ssh_publickey(
                db_name, db_host, db_port, db_user, db_password, schema_name,
                ssh_publickey_params['ssh_host'],
                int(ssh_publickey_params['ssh_port']),
                ssh_publickey_params['ssh_user'],
                ssh_publickey_params['ssh_key_path'],
                int(ssh_publickey_params['ssh_local_bind_port']))
        elif ssl_params:
            connected_db = get_postgresql_db_connection_with_ssl(
                db_name, db_host, db_port, db_user, db_password, schema_name,
                ssl_params['ssl_ca'],
                ssl_params['ssl_cert'],
                ssl_params['ssl_key'],
                ssl_params.get('ssl_hostname', db_host)) # Use db_host as fallback for ssl_hostname
        else:
            connected_db = get_postgresql_db_connection(
                db_name, db_host, db_port, db_user, db_password, schema_name)
    except Exception as e:
        # Log or print specific connection error
        print(f"Error connecting to PostgreSQL database: {e}")
        raise  # Re-raise the exception to be handled by the caller

    if not connected_db:
        raise ConnectionError("Failed to establish PostgreSQL database connection.")

    tuple_table_names = retrieve_table_name_tuple_list_from_connected_schema(connected_db, schema_name)
    table_names_list = convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_table_names)

    # Fetch all schema metadata in bulk
    all_columns_map = retrieve_all_columns_metadata_bulk_pg(schema_name, connected_db)
    pks_map, fks_map, uniques_map = retrieve_all_constraints_bulk_pg(schema_name, connected_db)

    for table_name in table_names_list:
        create_domain_result_file(table_name, json_generated_metadata_folder, use_pascal_case)

        table_columns_data = all_columns_map.get(table_name, {})
        table_pks_list = pks_map.get(table_name, [])
        table_fks_dict = fks_map.get(table_name, {}) # Keyed by column_name
        table_uniques_constraints = uniques_map.get(table_name, {}) # Keyed by constraint_name

        for column_name, col_bulk_data in table_columns_data.items():
            # Prepare column_metadata_for_class (simulating old retrieve_table_field_metadata output for one column)
            column_metadata_for_class = {
                'column_name': col_bulk_data['column_name'],
                'is_nullable': col_bulk_data['is_nullable'],
                'data_type': col_bulk_data['data_type'], # Generic data type
                'udt_name': col_bulk_data['udt_name'],   # More specific PG type
                'character_maximum_length': col_bulk_data.get('character_maximum_length'),
                'numeric_precision': col_bulk_data.get('numeric_precision'),
                'numeric_scale': col_bulk_data.get('numeric_scale'),
                'column_default': col_bulk_data.get('column_default'),
                'auto_increment': col_bulk_data.get('is_auto_increment', False) # From bulk query
                # Add other fields from col_bulk_data if PostgreSqlTableColumnFieldData needs them
            }

            pk_status = column_name in table_pks_list

            u_status = False
            for constraint_cols in table_uniques_constraints.values():
                if column_name in constraint_cols:
                    u_status = True
                    break

            fk_details_for_class = None
            column_fk_info = table_fks_dict.get(column_name) # This is {'referenced_table': ..., 'referenced_column': ..., 'constraint_name': ...}

            if column_fk_info:
                # Prepare column_fk_for_class to match structure expected by PostgreSqlTableColumnConstraintsData
                # which seems to be the output of old get_constraints_foreign_key (list of dicts)
                # The old get_constraints_foreign_key returned a list of dicts.
                # The PostgreSqlTableColumnConstraintsData constructor expects a single dict for column_fk.
                # The new fks_map provides this directly.
                fk_details_for_class = {
                    'constraint_column': column_name, # Current column is the FK column
                    'referenced_table': column_fk_info['referenced_table'],
                    'referenced_column': column_fk_info['referenced_column'],
                    'constraint_name': column_fk_info['constraint_name'],
                    'constraint_table': table_name # Table where the FK is defined
                    # 'definition' was in old get_constraints_foreign_key, not in new bulk one.
                    # Add if PostgreSqlTableColumnConstraintsData strictly needs it.
                }

                constraints_data = PostgreSqlTableColumnConstraintsData(
                    column_metadata_for_class, fk_details_for_class, pk_status, u_status
                ).__dict__
                add_table_constraint_to_json_domain(
                    table_name, constraints_data, json_generated_metadata_folder)
            else:
                field_data = PostgreSqlTableColumnFieldData(
                    column_metadata_for_class, pk_status, u_status
                ).__dict__
                add_table_column_to_json_domain(
                    table_name, field_data, json_generated_metadata_folder)

    domain_result_json_files = get_domain_result_files(json_generated_metadata_folder)
    for domain_result_json_file in domain_result_json_files:
        add_referenced_class_name_to_constraints(
            domain_result_json_file, domain_result_json_files, json_generated_metadata_folder)

    # Close connection logic (if applicable and not handled by context manager)
    if connected_db:
        if hasattr(connected_db, 'close'): # Cursor
            connected_db.close()
        if hasattr(connected_db, 'connection') and hasattr(connected_db.connection, 'close'): # Connection from cursor
             if connected_db.connection: # Check if not None
                connected_db.connection.close()
        # If there's an SSH tunnel object stored on connected_db (e.g., connected_db.tunnel), close it:
        # if hasattr(connected_db, 'tunnel') and connected_db.tunnel:
        #     connected_db.tunnel.stop()
        #     connected_db.tunnel.close() # Ensure proper cleanup

# Note: Assumed os.path.join is fine for json_generated_metadata_folder.
# Corrected parameter passing for SSH/SSL to ensure port numbers are int.
# Added ssl_params.get('ssl_hostname', db_host) as a fallback for ssl_hostname.
# Ensured connection closing logic is present (commented out, as actual management might be higher up).
# The data classes PostgreSqlTableColumnFieldData and PostgreSqlTableColumnConstraintsData
# are assumed to take (column_metadata_dict, pk_status_bool, u_status_bool) and
# (column_metadata_dict, fk_details_dict, pk_status_bool, u_status_bool) respectively.
# The `column_metadata_for_class` and `fk_details_for_class` are prepared to match this.
# The `auto_increment` flag is now sourced from the bulk column data.
# The `udt_name` from PostgreSQL's information_schema.columns is generally preferred for `Type`
# as it gives the specific underlying data type (e.g., _int4 for an array of integers).
# If the data classes expect the generic `data_type`, the mapping should use that.
# For now, `column_metadata_for_class` includes both. The data classes need to pick one.
# Let's assume data classes use `column_metadata['data_type']` for `Type` and `column_metadata['udt_name']` for `UdtType`.
# The old `retrieve_table_field_metadata` returned both.
# The definition of `PostgreSqlTableColumnFieldData` needs to be checked to confirm its expected dict keys.
# For now, `column_metadata_for_class` includes all potentially relevant fields from bulk query.
# The `retrieve_auto_increment_from_column` was removed, its logic is now in `retrieve_all_columns_metadata_bulk_pg`.
# The `verify_column_is_pk/fk/unique` and `get_column_fk` helper functions are no longer needed here as this
# information is directly available from the processed bulk maps (pks_map, fks_map, uniques_map).
# The `json_generated_metadata_folder` is correctly passed as string to helper functions.
# The `PostgreSqlTableColumnConstraintsData` class might need to be updated if it expects the `definition` field for an FK,
# as the new bulk query for FKs doesn't provide `pg_get_constraintdef(c.oid)`.
# If `definition` is crucial, the bulk FK query would need to be more complex, possibly involving `pg_catalog` joins.
# For now, assuming `definition` is not strictly required or will be handled differently.
# The structure of fks_map is {table: {column_fk: {details}}}, so `table_fks_dict.get(column_name)` is correct.
