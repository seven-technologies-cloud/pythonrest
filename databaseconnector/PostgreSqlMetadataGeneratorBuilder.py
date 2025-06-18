import psycopg2
from databaseconnector.JSONDictHelper import retrieve_json_from_sql_query
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
from collections import defaultdict

def get_postgresql_db_connection_with_ssl(
        _dbname, _host, _port, _user, _password, _schema, ssl_ca, ssl_cert, ssl_key, ssl_hostname
):
    try:
        conn_string = f"dbname='{_dbname}' user='{_user}' host='{_host}' password='{_password}' port='{_port}' " \
                      f"sslmode='verify-ca' sslrootcert='{ssl_ca}' sslcert='{ssl_cert}' sslkey='{ssl_key}'"
        if ssl_hostname:
             conn_string += f" hostaddr='{_host}'"

        con = psycopg2.connect(conn_string)
        cursor = con.cursor()
        if _schema:
            cursor.execute(f"SET search_path TO {_schema};")
        return cursor
    except Exception as e:
        print(f"Failed to connect with SSL: {e}")
        raise

def get_postgresql_db_connection_with_ssh_publickey(
        _dbname, _host, _port, _user, _password, _schema, ssh_host, ssh_port, ssh_user, ssh_key_path, ssh_local_bind_port
):
    try:
        ssh_key_path_str = Path(ssh_key_path).as_posix()
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, int(ssh_port)),
            ssh_username=ssh_user,
            ssh_pkey=ssh_key_path_str,
            remote_bind_address=(_host, int(_port)),
            local_bind_address=('127.0.0.1', int(ssh_local_bind_port)),
            set_keepalive=10
        )
        tunnel.start()
        con = psycopg2.connect(
            dbname=_dbname,
            host='127.0.0.1',
            user=_user,
            password=_password,
            port=tunnel.local_bind_port
        )
        cursor = con.cursor()
        if _schema:
            cursor.execute(f"SET search_path TO {_schema};")
        return cursor
    except Exception as e:
        print(f"Failed to connect with SSH public key: {e}")
        raise

def get_postgresql_db_connection_with_ssh_password(
        _dbname, _host, _port, _user, _password, _schema, ssh_host, ssh_port, ssh_user, ssh_password_val, ssh_local_bind_port
):
    try:
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, int(ssh_port)),
            ssh_username=ssh_user,
            ssh_password=ssh_password_val,
            remote_bind_address=(_host, int(_port)),
            local_bind_address=('127.0.0.1', int(ssh_local_bind_port)),
            set_keepalive=10
        )
        tunnel.start()
        con = psycopg2.connect(
            dbname=_dbname,
            host='127.0.0.1',
            user=_user,
            password=_password,
            port=tunnel.local_bind_port
        )
        cursor = con.cursor()
        if _schema:
            cursor.execute(f"SET search_path TO {_schema};")
        return cursor
    except Exception as e:
        print(f"Failed to connect with SSH password: {e}")
        raise

def get_postgresql_db_connection(_dbname, _host, _port, _user, _password, _schema):
    conn = psycopg2.connect(
        dbname=_dbname,
        host=_host,
        user=_user,
        password=_password,
        port=int(_port)
    )
    cursor = conn.cursor()
    if _schema:
        cursor.execute(f"SET search_path TO {_schema};")
    return cursor

def convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_name_list):
    return [table[0] for table in tuple_name_list] if tuple_name_list else []

def retrieve_table_name_tuple_list_from_connected_schema(connected_db, schema_name):
    connected_db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = 'BASE TABLE' ORDER BY table_name",
        (schema_name,))
    response = connected_db.fetchall()
    return response

def retrieve_table_field_metadata(table_name, schema_name, connected_db):
    sql_query = """
        SELECT column_name, is_nullable, data_type, character_maximum_length,
               numeric_precision, numeric_scale, column_default, udt_name
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = %s ORDER BY ordinal_position;
        """
    return retrieve_json_from_sql_query(sql_query, connected_db, (table_name, schema_name))

def retrieve_auto_increment_from_column(column_name, table_name, connected_db):
    sql_query = """
    SELECT count(*)
    FROM pg_class AS t
    JOIN pg_attribute AS a ON a.attrelid=t.oid
    JOIN pg_depend AS d ON d.refobjid=t.oid AND d.refobjsubid=a.attnum
    JOIN pg_class AS s ON s.oid=d.objid
    WHERE d.classid = 'pg_catalog.pg_class'::regclass
      AND d.refclassid = 'pg_catalog.pg_class'::regclass
      AND t.relkind IN('r', 'P')
      AND s.relkind='S'
      AND t.relname=%s
      AND a.attname=%s;
    """
    result = retrieve_json_from_sql_query(sql_query, connected_db, (table_name, column_name))
    return result[0]['count'] > 0 if result and 'count' in result[0] else False

def get_constraints_primary_keys(table_name, schema_name, connected_db):
    sql_query = """
      WITH unnested_confkey AS (
          SELECT oid, unnest(confkey) as confkey FROM pg_constraint
      ), unnested_conkey AS (
          SELECT oid, unnest(conkey) as conkey FROM pg_constraint
      )
      SELECT distinct c.conname AS constraint_name, c.contype AS constraint_type, 
      tbl.relname AS constraint_table, col.attname AS constraint_column,
      referenced_tbl.relname AS referenced_table, referenced_field.attname AS referenced_column,
      pg_get_constraintdef(c.oid) AS definition
      FROM pg_constraint c
      LEFT JOIN unnested_conkey con ON c.oid=con.oid
      LEFT JOIN pg_class tbl ON tbl.oid=c.conrelid
      LEFT JOIN pg_attribute col ON (col.attrelid=tbl.oid AND col.attnum=con.conkey)
      LEFT JOIN pg_class referenced_tbl ON c.confrelid=referenced_tbl.oid
      LEFT JOIN unnested_confkey conf ON c.oid=conf.oid
      LEFT JOIN pg_attribute referenced_field ON (referenced_field.attrelid=c.confrelid AND referenced_field.attnum=conf.confkey)
      LEFT JOIN information_schema.constraint_column_usage ccu on c.conname=ccu.constraint_name
      WHERE ccu.table_schema= %s AND tbl.relname= %s AND c.contype = 'p'
      """
    return retrieve_json_from_sql_query(sql_query, connected_db, (schema_name, table_name))

def get_constraints_foreign_key(table_name, schema_name, connected_db):
    sql_query = """
    WITH unnested_confkey AS (
        SELECT oid, unnest(confkey) as confkey FROM pg_constraint
    ), unnested_conkey AS (
        SELECT oid, unnest(conkey) as conkey FROM pg_constraint
    )
    SELECT distinct c.conname AS constraint_name, c.contype AS constraint_type, 
    tbl.relname AS constraint_table, col.attname AS constraint_column,
    referenced_tbl.relname AS referenced_table, referenced_field.attname AS referenced_column,
    pg_get_constraintdef(c.oid) AS definition
    FROM pg_constraint c
    LEFT JOIN unnested_conkey con ON c.oid=con.oid
    LEFT JOIN pg_class tbl ON tbl.oid=c.conrelid
    LEFT JOIN pg_attribute col ON (col.attrelid=tbl.oid AND col.attnum=con.conkey)
    LEFT JOIN pg_class referenced_tbl ON c.confrelid=referenced_tbl.oid
    LEFT JOIN unnested_confkey conf ON c.oid=conf.oid
    LEFT JOIN pg_attribute referenced_field ON (referenced_field.attrelid=c.confrelid AND referenced_field.attnum=conf.confkey)
    LEFT JOIN information_schema.constraint_column_usage ccu ON c.conname=ccu.constraint_name
    WHERE ccu.table_schema= %s AND tbl.relname= %s AND c.contype = 'f'
    """
    return retrieve_json_from_sql_query(sql_query, connected_db, (schema_name, table_name))

def get_constraints_unique(table_name, schema_name, connected_db):
    sql_query = """
    WITH unnested_confkey AS (
        SELECT oid, unnest(confkey) as confkey FROM pg_constraint
    ), unnested_conkey AS (
        SELECT oid, unnest(conkey) as conkey FROM pg_constraint
    )
    SELECT distinct c.conname AS constraint_name, c.contype AS constraint_type, 
    tbl.relname AS constraint_table, col.attname AS constraint_column,
    referenced_tbl.relname AS referenced_table, referenced_field.attname AS referenced_column,
    pg_get_constraintdef(c.oid) AS definition
    FROM pg_constraint c
    LEFT JOIN unnested_conkey con ON c.oid=con.oid
    LEFT JOIN pg_class tbl ON tbl.oid=c.conrelid
    LEFT JOIN pg_attribute col ON (col.attrelid=tbl.oid AND col.attnum=con.conkey)
    LEFT JOIN pg_class referenced_tbl ON c.confrelid=referenced_tbl.oid
    LEFT JOIN unnested_confkey conf ON c.oid=conf.oid
    LEFT JOIN pg_attribute referenced_field ON (referenced_field.attrelid=c.confrelid AND referenced_field.attnum=conf.confkey)
    LEFT JOIN information_schema.constraint_column_usage ccu ON c.conname=ccu.constraint_name
    WHERE ccu.table_schema= %s AND tbl.relname= %s AND c.contype = 'u'
    """
    return retrieve_json_from_sql_query(sql_query, connected_db, (schema_name, table_name))

def retrieve_all_columns_metadata_bulk_pg(schema_name, connected_db):
    sql_query = """
        SELECT
            table_name, column_name, ordinal_position, column_default,
            is_nullable, data_type, udt_name,
            character_maximum_length, numeric_precision, numeric_scale,
            datetime_precision, interval_type, interval_precision,
            is_identity, identity_generation,
            is_updatable
        FROM information_schema.columns
        WHERE table_schema = %s ORDER BY table_name, ordinal_position;
    """
    params = (schema_name,)
    columns_data = retrieve_json_from_sql_query(sql_query, connected_db, params)

    tables_metadata = defaultdict(dict)
    if columns_data:
        for col in columns_data:
            table_name = col['table_name']
            column_name = col['column_name']
            tables_metadata[table_name][column_name] = col

    return dict(tables_metadata)

def retrieve_all_constraints_bulk_pg(schema_name, connected_db):
    sql_query = """
        SELECT
            tc.table_name,
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu_ref.table_name AS referenced_table_name,
            ccu_ref.column_name AS referenced_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            AND tc.table_name = kcu.table_name
        LEFT JOIN information_schema.referential_constraints AS rc
            ON tc.constraint_name = rc.constraint_name AND tc.constraint_schema = rc.constraint_schema
        LEFT JOIN information_schema.key_column_usage AS ccu_ref
            ON rc.unique_constraint_name = ccu_ref.constraint_name
            AND rc.unique_constraint_schema = ccu_ref.table_schema
        WHERE tc.table_schema = %s
        ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position;
    """
    params = (schema_name,)
    constraints_data = retrieve_json_from_sql_query(sql_query, connected_db, params)

    pks_map = defaultdict(list)
    fks_map = defaultdict(dict)
    uniques_map = defaultdict(lambda: defaultdict(list))

    if constraints_data:
        for con_info in constraints_data:
            table_name = con_info['table_name']
            column_name = con_info['column_name']
            constraint_name = con_info['constraint_name']

            if con_info['constraint_type'] == 'PRIMARY KEY':
                if column_name not in pks_map[table_name]:
                     pks_map[table_name].append(column_name)
            elif con_info['constraint_type'] == 'UNIQUE':
                uniques_map[table_name][constraint_name].append(column_name)
            elif con_info['constraint_type'] == 'FOREIGN KEY':
                if column_name not in fks_map[table_name]:
                    fks_map[table_name][column_name] = {
                        'referenced_table': con_info['referenced_table_name'],
                        'referenced_column': con_info['referenced_column_name'],
                        'constraint_name': constraint_name
                    }

    return {tn: list(cols) for tn, cols in pks_map.items()}, \
           {tn: dict(cols) for tn, cols in fks_map.items()}, \
           {tn: {cn: list(cols) for cn, cols in constrs.items()} for tn, constrs in uniques_map.items()}

def verify_column_is_pk(table_name, column_metadata, columns_constraint_primary_key):
    for ccpk in columns_constraint_primary_key:
        if column_metadata['column_name'] == ccpk['constraint_column'] and table_name == ccpk['constraint_table']:
            return True
    return False

def verify_column_is_fk(table_name, column_metadata, columns_constraint_foreign_key):
    for ccfk in columns_constraint_foreign_key:
        if column_metadata['column_name'] == ccfk['constraint_column'] and table_name == ccfk['constraint_table']:
            return True
    return False

def verify_column_is_unique(table_name, column_metadata, columns_constraint_unique):
    for ccu in columns_constraint_unique:
        if column_metadata['column_name'] == ccu['constraint_column'] and table_name == ccu['constraint_table']:
            return True
    return False

def get_column_fk(table_name, column_metadata, columns_constraint_foreign_key):
    for ccfk in columns_constraint_foreign_key:
        if column_metadata['column_name'] == ccfk['constraint_column'] and table_name == ccfk['constraint_table']:
            return ccfk
    return None
