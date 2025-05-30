from psycopg2 import *
from databaseconnector.JSONDictHelper import retrieve_json_from_sql_query
from sshtunnel import SSHTunnelForwarder
from pathlib import Path

def get_postgresql_db_connection_with_ssl(
        _dbname, _host, _port, _user, _password, _schema, ssl_ca, ssl_cert, ssl_key, ssl_hostname
):
    try:
        con = connect(
            dbname=_dbname,
            host=ssl_hostname, user=_user,
            password=_password,
            port=_port,
            ssl={
                'ca': ssl_ca,
                'cert': ssl_cert,
                'key': ssl_key,
                'check_hostname': False # TODO Configuração apenas para nivel de teste, para produção necessario a remoção desta linha.
            }
        )

        cursor = con.cursor()
        cursor.execute(f"SET search_path TO {_schema};")
        return cursor

    except Exception as e:
        print(f"Failed to connect: {e}")

def get_postgresql_db_connection_with_ssh_publickey(
        _dbname, _host, _port, _user, _password, _schema, ssh_host, ssh_port, ssh_user, ssh_key_path, ssh_local_bind_port
):
    try:
        ssh_key_path = Path(ssh_key_path).as_posix()

        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=ssh_key_path,
            remote_bind_address=(_host, _port),
            local_bind_address=(ssh_host, ssh_local_bind_port),
            set_keepalive=10
        )

        tunnel.start()

        con = connect(
            dbname=_dbname,
            host=_host, user=_user,
            password=_password,
            port=tunnel.local_bind_port
        )

        cursor = con.cursor()
        cursor.execute(f"SET search_path TO {_schema};")
        return cursor

    except Exception as e:
        print(f"Failed to connect: {e}")

def get_postgresql_db_connection_with_ssh_password(
        _dbname, _host, _port, _user, _password, _schema, ssh_host, ssh_port, ssh_user, ssh_password, ssh_local_bind_port
):
    try:
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_password=ssh_password,
            remote_bind_address=(_host, _port),
            local_bind_address=(ssh_host, ssh_local_bind_port),
            set_keepalive=10
        )

        tunnel.start()

        con = connect(
            dbname=_dbname,
            host=_host, user=_user,
            password=_password,
            port=tunnel.local_bind_port
        )

        cursor = con.cursor()
        cursor.execute(f"SET search_path TO {_schema};")
        return cursor

    except Exception as e:
        print(f"Failed to connect: {e}")

def get_postgresql_db_connection(_dbname, _host, _port, _user, _password, _schema):
    conn = connect(
        dbname=_dbname,
        host=_host,
        user=_user,
        password=_password,
        port=_port
    )
    cursor = conn.cursor()
    cursor.execute(f"SET search_path TO {_schema};")
    return cursor

def convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_name_list):
    table_list = list()
    for table in tuple_name_list:
        table_list.append(table[0])
    return table_list


def retrieve_table_name_tuple_list_from_connected_schema(connected_db, schema_name):
    connected_db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = 'BASE TABLE' ORDER BY table_name",
        (schema_name,))
    response = connected_db.fetchall()
    return response


def retrieve_table_field_metadata(table_name, schema_name, connected_db):
    sql_query = """
        SELECT column_name, is_nullable, data_type, character_maximum_length, numeric_precision, numeric_scale, column_default, udt_name
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = %s
        """
    return retrieve_json_from_sql_query(sql_query, connected_db, (table_name, schema_name))

def retrieve_auto_increment_from_column(column_name, table_name, connected_db):
    sql_query = """
    SELECT count(*) FROM pg_class AS t
    JOIN pg_attribute AS a ON a.attrelid=t.oid
    JOIN pg_depend AS d ON d.refobjid=t.oid AND d.refobjsubid=a.attnum
    JOIN pg_class AS s ON s.oid=d.objid
    WHERE d.classid = 'pg_catalog.pg_class'::regclass
    AND d.refclassid = 'pg_catalog.pg_class'::regclass
    AND t.relkind IN('r', 'P')
    AND s.relkind='S'
    AND t.relname=%s
    AND a.attname=%s
    """
    result = retrieve_json_from_sql_query(sql_query, connected_db, (table_name, column_name))
    return result if result != list() else {}


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

# Verifies if column_metadata has a match on columns_constraint_primary_key
# If match, return true, else return false
def verify_column_is_pk(table_name, column_metadata, columns_constraint_primary_key):
    for ccpk in columns_constraint_primary_key:
        if column_metadata['column_name'] == ccpk['constraint_column'] and table_name == ccpk['constraint_table']:
            return True
    return False

# Verifies if column_metadata has a match on columns_constraint_foreign_key
# If match, return true, else return false


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

# Verifies if column_metadata has a match on columns_constraint_foreign_key
# If match, return fk data from columns_constraint_foreign_key, else return None


def get_column_fk(table_name, column_metadata, columns_constraint_foreign_key):
    for ccfk in columns_constraint_foreign_key:
        if column_metadata['column_name'] == ccfk['constraint_column'] and table_name == ccfk['constraint_table']:
            return ccfk
    return None
