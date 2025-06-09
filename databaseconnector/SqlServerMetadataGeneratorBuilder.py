import pymssql # Changed from `from pymssql import *` for clarity
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
from collections import defaultdict # Added

def get_sqlserver_db_connection_with_ssl(
        server, port, user, password, database, ssl_ca, ssl_cert, ssl_key, ssl_hostname
):
    # pymssql's SSL handling is different from psycopg2 or MySQL Connector/Python.
    # It typically relies on the underlying FreeTDS configuration for SSL,
    # or connection string parameters if the driver/library supports them directly.
    # The `ssl` dict is not a standard parameter for pymssql.connect().
    # This function would need significant changes if SSL is to be properly supported with pymssql.
    # For now, assuming this configuration was intended for a different driver or needs external setup.
    # Returning a normal connection for now, ignoring SSL params for pymssql.connect.
    try:
        conn = pymssql.connect(
            server=server, # Or ssl_hostname if that's the connect target
            port=int(port) if port else 1433,
            user=user,
            password=password,
            database=database
            # SSL parameters would typically be part of the DSN or handled by FreeTDS config
        )
        cursor = conn.cursor(as_dict=True)
        return cursor
    except Exception as e:
        print(f"Failed to connect (SSL params ignored by pymssql.connect): {e}")
        raise

def get_sqlserver_db_connection_with_ssh_publickey(
        server, port, user, password, database, ssh_host, ssh_port, ssh_user, ssh_key_path, ssh_local_bind_port
):
    try:
        ssh_key_path_str = Path(ssh_key_path).as_posix()
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, int(ssh_port)),
            ssh_username=ssh_user,
            ssh_pkey=ssh_key_path_str,
            remote_bind_address=(server, int(port)),
            local_bind_address=('127.0.0.1', int(ssh_local_bind_port)), # Corrected
            set_keepalive=10
        )
        tunnel.start()
        conn = pymssql.connect(
            server='127.0.0.1', # Corrected
            port=tunnel.local_bind_port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor(as_dict=True)
        # Store tunnel with cursor or connection if it needs to be closed later
        # cursor.tunnel = tunnel
        return cursor
    except Exception as e:
        print(f"Failed to connect with SSH public key: {e}")
        raise

def get_sqlserver_db_connection_with_ssh_password(
        server, port, user, password, database, ssh_host, ssh_port, ssh_user, ssh_password_val, ssh_local_bind_port # Renamed ssh_password
):
    try:
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, int(ssh_port)),
            ssh_username=ssh_user,
            ssh_password=ssh_password_val,
            remote_bind_address=(server, int(port)),
            local_bind_address=('127.0.0.1', int(ssh_local_bind_port)), # Corrected
            set_keepalive=10
        )
        tunnel.start()
        conn = pymssql.connect(
            server='127.0.0.1', # Corrected
            port=tunnel.local_bind_port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor(as_dict=True)
        return cursor
    except Exception as e:
        print(f"Failed to connect with SSH password: {e}")
        raise

def get_sqlserver_connection(server, port, user, password, database):
    try:
        conn = pymssql.connect(
            server=server,
            port=int(port) if port else 1433, # Default SQL Server port
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor(as_dict=True)
        return cursor
    except Exception as e:
        print(f"Failed to connect: {e}")
        raise

def convert_retrieved_tuple_name_list_from_sqlserver(table_name_tuple_list):
    return [table['TABLE_NAME'] for table in table_name_tuple_list] if table_name_tuple_list else []

def retrieve_table_name_tuple_list_from_connected_database(connected_database_cursor):
    connected_database_cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = DB_NAME() -- Filter by current database
        ORDER BY TABLE_NAME;
    """)
    return connected_database_cursor.fetchall()

def retrieve_table_columns_from_connected_database(table_name, schema_name, connected_database_cursor):
    # schema_name is often 'dbo' for SQL Server if not specified otherwise.
    sql_query = """
        SELECT *, COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') AS IS_IDENTITY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s
        ORDER BY ORDINAL_POSITION;
    """
    connected_database_cursor.execute(sql_query, (table_name, schema_name))
    return connected_database_cursor.fetchall()

# Existing per-column PK/FK/Unique/AutoIncrement functions are kept for now.
# They use a mix of INFORMATION_SCHEMA and sys.objects, and are per-column.
def retrieve_table_primary_key_from_connected_database(column, table_name, schema_name, connected_database_cursor):
    sql_query = """
    SELECT Col.Column_Name
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS Tab
    JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE Col
        ON Col.Constraint_Name = Tab.Constraint_Name AND Col.Table_Name = Tab.Table_Name AND Col.TABLE_SCHEMA = Tab.TABLE_SCHEMA
    WHERE Tab.Constraint_Type = 'PRIMARY KEY'
      AND Col.Table_Name = %s
      AND Col.Column_Name = %s
      AND Tab.TABLE_SCHEMA = %s;
    """
    connected_database_cursor.execute(sql_query, (table_name, column, schema_name))
    return connected_database_cursor.fetchall()

def retrieve_table_foreign_key_from_connected_database(column, table_name, schema_name, connected_database_cursor):
    sql_query = """
    SELECT Col.Column_Name
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS Tab
    JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE Col
        ON Col.Constraint_Name = Tab.Constraint_Name AND Col.Table_Name = Tab.Table_Name AND Col.TABLE_SCHEMA = Tab.TABLE_SCHEMA
    WHERE Tab.Constraint_Type = 'FOREIGN KEY'
      AND Col.Table_Name = %s
      AND Col.Column_Name = %s
      AND Tab.TABLE_SCHEMA = %s;
    """
    connected_database_cursor.execute(sql_query, (table_name, column, schema_name))
    return connected_database_cursor.fetchall()

def retrieve_table_unique_from_connected_database(column, table_name, schema_name, connected_database_cursor):
    sql_query = """
    SELECT Col.Column_Name
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS Tab
    JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE Col
        ON Col.Constraint_Name = Tab.Constraint_Name AND Col.Table_Name = Tab.Table_Name AND Col.TABLE_SCHEMA = Tab.TABLE_SCHEMA
    WHERE Tab.Constraint_Type = 'UNIQUE'
      AND Col.Table_Name = %s
      AND Col.Column_Name = %s
      AND Tab.TABLE_SCHEMA = %s;
    """
    connected_database_cursor.execute(sql_query, (table_name, column, schema_name))
    return connected_database_cursor.fetchall()

def retrieve_table_auto_incremente_from_connected_database(column, table_name, schema_name, connected_database_cursor):
    # Construct fully qualified table name for OBJECT_ID
    qualified_table_name = f"{schema_name}.{table_name}"
    sql_query = "SELECT name, COLUMNPROPERTY(OBJECT_ID(%s), name, 'IsIdentity') AS is_identity FROM sys.columns WHERE OBJECT_ID = OBJECT_ID(%s) AND name = %s"
    connected_database_cursor.execute(sql_query, (qualified_table_name, qualified_table_name, column))
    row = connected_database_cursor.fetchone() # Expect one row or None
    return row['is_identity'] == 1 if row else False

def retrieve_references_table_foreign_keys_from_tables_from_connected_database(column, table_name, schema_name, connected_database_cursor):
    # This query is quite specific and uses sys objects.
    # The new bulk FK query will use INFORMATION_SCHEMA.
    sql_query = """
    SELECT 
        obj.name AS FK_NAME, 
        s_tab1.name AS schema_name,
        tab1.name AS [table], 
        col1.name AS [column], 
        s_tab2.name AS referenced_schema_name,
        tab2.name AS referenced_table,
        col2.name AS referenced_column
    FROM sys.foreign_key_columns fkc
    INNER JOIN sys.objects obj ON obj.object_id = fkc.constraint_object_id
    INNER JOIN sys.tables tab1 ON tab1.object_id = fkc.parent_object_id
    INNER JOIN sys.schemas s_tab1 ON tab1.schema_id = s_tab1.schema_id
    INNER JOIN sys.columns col1 ON col1.column_id = parent_column_id AND col1.object_id = tab1.object_id
    INNER JOIN sys.tables tab2 ON tab2.object_id = fkc.referenced_object_id
    INNER JOIN sys.schemas s_tab2 ON tab2.schema_id = s_tab2.schema_id
    INNER JOIN sys.columns col2 ON col2.column_id = referenced_column_id AND col2.object_id = tab2.object_id
    WHERE s_tab1.name = %s AND tab1.name = %s AND col1.name = %s;
    """
    connected_database_cursor.execute(sql_query, (schema_name, table_name, column))
    return connected_database_cursor.fetchall() # Returns a list of dicts

# --- New Bulk Metadata Retrieval Functions (SQL Server) ---

def retrieve_all_columns_metadata_bulk_sqlserver(schema_name, cursor):
    sql_query = """
        SELECT
            TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, COLUMN_DEFAULT,
            IS_NULLABLE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION, NUMERIC_PRECISION_RADIX, NUMERIC_SCALE, DATETIME_PRECISION,
            COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') AS IS_IDENTITY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME, ORDINAL_POSITION;
    """
    cursor.execute(sql_query, (schema_name,))
    columns_data = cursor.fetchall() # List of dicts

    tables_metadata = defaultdict(dict)
    if columns_data:
        for col_dict in columns_data:
            table_name = col_dict['TABLE_NAME']
            column_name = col_dict['COLUMN_NAME']
            # Add derived is_auto_increment for consistency with other DBs' bulk functions
            col_dict['is_auto_increment'] = (col_dict.get('IS_IDENTITY') == 1)
            tables_metadata[table_name][column_name] = col_dict
    return {tn: dict(cols) for tn, cols in tables_metadata.items()}

def retrieve_all_constraints_bulk_sqlserver(schema_name, cursor):
    sql_query = """
        SELECT
            tc.TABLE_NAME,
            kcu.COLUMN_NAME,
            tc.CONSTRAINT_NAME,
            tc.CONSTRAINT_TYPE, -- 'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE KEY' (Note: SQL Server uses 'UNIQUE KEY')
            kcu_ref.TABLE_NAME AS REFERENCED_TABLE_NAME,
            kcu_ref.COLUMN_NAME AS REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            AND tc.TABLE_NAME = kcu.TABLE_NAME -- Ensure kcu.TABLE_NAME is used for the join
        LEFT JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME AND tc.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
        LEFT JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE kcu_ref -- For referenced table/column by FK
            ON rc.UNIQUE_CONSTRAINT_NAME = kcu_ref.CONSTRAINT_NAME AND rc.UNIQUE_CONSTRAINT_SCHEMA = kcu_ref.TABLE_SCHEMA -- Match schema for referenced constraint
        WHERE tc.TABLE_SCHEMA = %s
        ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION;
    """
    cursor.execute(sql_query, (schema_name,))
    constraints_data = cursor.fetchall()

    pks_map = defaultdict(list)
    fks_map = defaultdict(dict)
    uniques_map = defaultdict(lambda: defaultdict(list))

    if constraints_data:
        for con_info in constraints_data:
            table_name = con_info['TABLE_NAME']
            column_name = con_info['COLUMN_NAME']
            constraint_name = con_info['CONSTRAINT_NAME']

            if con_info['CONSTRAINT_TYPE'] == 'PRIMARY KEY':
                if column_name not in pks_map[table_name]:
                    pks_map[table_name].append(column_name)
            elif con_info['CONSTRAINT_TYPE'] == 'UNIQUE' or con_info['CONSTRAINT_TYPE'] == 'UNIQUE KEY': # SQL Server uses 'UNIQUE KEY' or just 'UNIQUE'
                uniques_map[table_name][constraint_name].append(column_name)
            elif con_info['CONSTRAINT_TYPE'] == 'FOREIGN KEY':
                if column_name not in fks_map[table_name]: # Store one FK detail per column
                    fks_map[table_name][column_name] = {
                        'referenced_table': con_info['REFERENCED_TABLE_NAME'],
                        'referenced_column': con_info['REFERENCED_COLUMN_NAME'],
                        'constraint_name': constraint_name
                    }

    return {tn: list(cols) for tn, cols in pks_map.items()}, \
           {tn: dict(cols) for tn, cols in fks_map.items()}, \
           {tn: {cn: list(cols) for cn, cols in constrs.items()} for tn, constrs in uniques_map.items()}

# Notes on SQL Server specific details:
# - `INFORMATION_SCHEMA.COLUMNS.TABLE_CATALOG` can be used to filter by current DB if needed, DB_NAME() also works.
# - `COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity')` is a SQL Server specific way to check identity.
# - `INFORMATION_SCHEMA.TABLE_CONSTRAINTS.CONSTRAINT_TYPE` can be 'UNIQUE KEY' for unique constraints.
# - SSL for pymssql: `encrypt=True` often used with `trust_server_certificate=True` (less secure) or proper CA validation.
#   The original SSL dict is not directly compatible. Simplified SSL connection for now.
# - `retrieve_table_columns_from_connected_database` now also fetches `IS_IDENTITY`.
# - `retrieve_table_auto_incremente_from_connected_database` was updated to use fully qualified name for OBJECT_ID.
# - `retrieve_references_table_foreign_keys_from_tables_from_connected_database` also needed schema for referenced table.
# - `retrieve_table_name_tuple_list_from_connected_database` added `TABLE_CATALOG = DB_NAME()` for SQL Server.
# - Corrected port to be int in connection functions.
# - Renamed ssh_password parameter in password auth function.
# - Changed `from pymssql import *` to `import pymssql`.
# - Added schema_name to relevant per-table/per-column functions.
# - The `retrieve_json_from_sql_query` is not used here; pymssql cursor with `as_dict=True` directly gives dicts.
# - The `retrieve_references_table_foreign_keys_from_tables_from_connected_database` query was updated to include schema for the referenced table `s_tab2.name AS referenced_schema_name`.
# - Bulk constraint query for SQL Server needs to handle `UNIQUE KEY` as well as `UNIQUE`.
# - The join for `kcu_ref` in bulk constraints: `rc.UNIQUE_CONSTRAINT_SCHEMA = kcu_ref.TABLE_SCHEMA` (schema of the table owning the constraint).
#   And `rc.UNIQUE_CONSTRAINT_NAME = kcu_ref.CONSTRAINT_NAME`.
#   This ensures we correctly link to the columns of the referenced unique/primary key constraint.
# - The `local_bind_address` for SSH tunnel uses `int(ssh_local_bind_port)`.
# - The `remote_bind_address` for SSH tunnel uses `int(port)`.
# - `get_sqlserver_connection` default port is 1433.
# - `retrieve_table_columns_from_connected_database` query now orders by ORDINAL_POSITION.
# - The bulk queries are now the primary source for metadata in the refactored worker.
# - `retrieve_all_columns_metadata_bulk_sqlserver` derives `is_auto_increment`.
# - `retrieve_all_constraints_bulk_sqlserver` processes PK, FK, Unique constraints.
# - The `pymssql.connect` does not take an `ssl` dictionary. SSL is usually handled by underlying TDS protocol settings or DSN.
#   The SSL connection function has been simplified to reflect this, effectively ignoring the specific cert paths for now unless a DSN or other mechanism is used.
#   A proper pymssql SSL setup often involves `encrypt=True` and potentially other TDS flags.
#   For this refactor, I'm keeping it simple and noting the limitation. The original `ssl` dict was non-functional for pymssql.
# - The function `retrieve_table_auto_incremente_from_connected_database` was simplified to return boolean directly.
# - `retrieve_references_table_foreign_keys_from_tables_from_connected_database` is a complex sys query. The bulk FK query uses INFORMATION_SCHEMA.
#   These might return slightly different details or levels of detail.
# - `retrieve_table_name_tuple_list_from_connected_database` added `ORDER BY TABLE_NAME`.
# - The `retrieve_table_columns_from_connected_database` now includes `TABLE_SCHEMA` in its filter.
# - Corrected `TABLE_SCHEMA` usage in per-column constraint checks.
# - `pymssql.connect(port=...)` expects port to be an int or string that can be int. Ensured int conversion.The file `databaseconnector/SqlServerMetadataGeneratorBuilder.py` has been successfully overwritten.

**Summary of Key Changes:**

1.  **Imports**:
    *   Added `from collections import defaultdict`.
    *   Changed `from pymssql import *` to `import pymssql` for clarity.

2.  **SSH Tunneling Corrections**:
    *   In SSH-tunneled connection functions (`get_sqlserver_db_connection_with_ssh_publickey`, `get_sqlserver_db_connection_with_ssh_password`):
        *   The `server` parameter in `pymssql.connect()` was changed to `'127.0.0.1'` (local end of the tunnel).
        *   `local_bind_address` for `SSHTunnelForwarder` was corrected to `('127.0.0.1', int(ssh_local_bind_port))`.
        *   Ensured all port numbers (`ssh_port`, `port`, `ssh_local_bind_port`) are cast to `int`.
    *   Renamed `ssh_password` parameter in `get_sqlserver_db_connection_with_ssh_password` to `ssh_password_val` to avoid conflict.

3.  **SSL Connection Simplification**:
    *   The `get_sqlserver_db_connection_with_ssl` function was simplified. The non-standard `ssl` dictionary parameter for `pymssql.connect()` was removed as `pymssql` handles SSL via underlying TDS configuration or DSN parameters (like `encrypt=True`). The function now makes a standard connection, noting that SSL parameters like specific CA/cert files would need external configuration (e.g., FreeTDS settings).

4.  **Exception Handling**: Added `raise` to the `except` blocks of all connection helper functions to ensure exceptions are propagated.

5.  **Default Port**: Ensured `get_sqlserver_connection` and SSL connection use `int(port)` or default to 1433 if port is not provided.

6.  **Schema Usage in Queries**:
    *   `retrieve_table_name_tuple_list_from_connected_database` now filters by current database using `TABLE_CATALOG = DB_NAME()` and adds `ORDER BY TABLE_NAME`.
    *   Existing per-table/per-column metadata functions (`retrieve_table_columns_from_connected_database`, `retrieve_table_primary_key_from_connected_database`, etc.) were updated to correctly use `TABLE_SCHEMA` or fully qualified names where appropriate for SQL Server.
    *   `retrieve_table_auto_incremente_from_connected_database` was simplified to return a boolean.

7.  **New Bulk Metadata Retrieval Functions (using `INFORMATION_SCHEMA`)**:
    *   **`retrieve_all_columns_metadata_bulk_sqlserver(schema_name, cursor)`**:
        *   Queries `INFORMATION_SCHEMA.COLUMNS` for the given `schema_name`.
        *   Includes `COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') AS IS_IDENTITY` to detect identity columns.
        *   Derives an `is_auto_increment` boolean flag from `IS_IDENTITY`.
        *   Returns data as `{ 'table_name': { 'column_name': {col_details_including_is_auto_increment} } }`.
    *   **`retrieve_all_constraints_bulk_sqlserver(schema_name, cursor)`**:
        *   Queries `INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc`, `INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu`, `INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc`, and `INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE kcu_ref`.
        *   Filters by `tc.TABLE_SCHEMA = %s`.
        *   Processes results into three maps:
            *   `pks_map = { 'table_name': ['pk_col1', ...], ... }`
            *   `fks_map = { 'table_name': { 'column_name_fk': {'referenced_table': ..., 'referenced_column': ..., 'constraint_name': ...}, ... }, ... }`
            *   `uniques_map = { 'table_name': { 'constraint_name': ['col1', ...], ... }, ... }` (Handles `UNIQUE` and `UNIQUE KEY` constraint types).
        *   Returns these three maps as a tuple.

8.  **Existing Functions**: Were kept as requested, with minor updates for schema handling where necessary.

These changes introduce bulk metadata fetching capabilities for SQL Server and improve the robustness and correctness of database connection functions.

The subtask is complete.
