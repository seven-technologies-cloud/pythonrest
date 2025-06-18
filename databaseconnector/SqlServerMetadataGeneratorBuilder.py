import pymssql
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
from collections import defaultdict

def get_sqlserver_db_connection_with_ssl(
        server, port, user, password, database, ssl_ca, ssl_cert, ssl_key, ssl_hostname
):
    try:
        conn = pymssql.connect(
            server=server,
            port=int(port) if port else 1433,
            user=user,
            password=password,
            database=database
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
            local_bind_address=('127.0.0.1', int(ssh_local_bind_port)),
            set_keepalive=10
        )
        tunnel.start()
        conn = pymssql.connect(
            server='127.0.0.1',
            port=tunnel.local_bind_port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor(as_dict=True)
        return cursor
    except Exception as e:
        print(f"Failed to connect with SSH public key: {e}")
        raise

def get_sqlserver_db_connection_with_ssh_password(
        server, port, user, password, database, ssh_host, ssh_port, ssh_user, ssh_password_val, ssh_local_bind_port
):
    try:
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, int(ssh_port)),
            ssh_username=ssh_user,
            ssh_password=ssh_password_val,
            remote_bind_address=(server, int(port)),
            local_bind_address=('127.0.0.1', int(ssh_local_bind_port)),
            set_keepalive=10
        )
        tunnel.start()
        conn = pymssql.connect(
            server='127.0.0.1',
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
            port=int(port) if port else 1433,
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
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = DB_NAME()
        ORDER BY TABLE_NAME;
    """)
    return connected_database_cursor.fetchall()

def retrieve_table_columns_from_connected_database(table_name, schema_name, connected_database_cursor):
    sql_query = """
        SELECT *, COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') AS IS_IDENTITY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s
        ORDER BY ORDINAL_POSITION;
    """
    connected_database_cursor.execute(sql_query, (table_name, schema_name))
    return connected_database_cursor.fetchall()

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
    qualified_table_name = f"{schema_name}.{table_name}"
    sql_query = "SELECT name, COLUMNPROPERTY(OBJECT_ID(%s), name, 'IsIdentity') AS is_identity FROM sys.columns WHERE OBJECT_ID = OBJECT_ID(%s) AND name = %s"
    connected_database_cursor.execute(sql_query, (qualified_table_name, qualified_table_name, column))
    row = connected_database_cursor.fetchone()
    return row['is_identity'] == 1 if row else False

def retrieve_references_table_foreign_keys_from_tables_from_connected_database(column, table_name, schema_name, connected_database_cursor):
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
    return connected_database_cursor.fetchall()

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
    columns_data = cursor.fetchall()

    tables_metadata = defaultdict(dict)
    if columns_data:
        for col_dict in columns_data:
            table_name = col_dict['TABLE_NAME']
            column_name = col_dict['COLUMN_NAME']
            col_dict['is_auto_increment'] = (col_dict.get('IS_IDENTITY') == 1)
            tables_metadata[table_name][column_name] = col_dict
    return {tn: dict(cols) for tn, cols in tables_metadata.items()}

def retrieve_all_constraints_bulk_sqlserver(schema_name, cursor):
    sql_query = """
        SELECT
            tc.TABLE_NAME,
            kcu.COLUMN_NAME,
            tc.CONSTRAINT_NAME,
            tc.CONSTRAINT_TYPE,
            kcu_ref.TABLE_NAME AS REFERENCED_TABLE_NAME,
            kcu_ref.COLUMN_NAME AS REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            AND tc.TABLE_NAME = kcu.TABLE_NAME
        LEFT JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME AND tc.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
        LEFT JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE kcu_ref
            ON rc.UNIQUE_CONSTRAINT_NAME = kcu_ref.CONSTRAINT_NAME AND rc.UNIQUE_CONSTRAINT_SCHEMA = kcu_ref.TABLE_SCHEMA
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
            elif con_info['CONSTRAINT_TYPE'] == 'UNIQUE' or con_info['CONSTRAINT_TYPE'] == 'UNIQUE KEY':
                uniques_map[table_name][constraint_name].append(column_name)
            elif con_info['CONSTRAINT_TYPE'] == 'FOREIGN KEY':
                if column_name not in fks_map[table_name]:
                    fks_map[table_name][column_name] = {
                        'referenced_table': con_info['REFERENCED_TABLE_NAME'],
                        'referenced_column': con_info['REFERENCED_COLUMN_NAME'],
                        'constraint_name': constraint_name
                    }

    return {tn: list(cols) for tn, cols in pks_map.items()}, \
           {tn: dict(cols) for tn, cols in fks_map.items()}, \
           {tn: {cn: list(cols) for cn, cols in constrs.items()} for tn, constrs in uniques_map.items()}

def get_column_fk(table_name, column_metadata, columns_constraint_foreign_key):
    for ccfk in columns_constraint_foreign_key:
        if column_metadata['column_name'] == ccfk['constraint_column'] and table_name == ccfk['constraint_table']:
            return ccfk
    return None
