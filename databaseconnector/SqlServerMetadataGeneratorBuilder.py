from pymssql import *
from sshtunnel import SSHTunnelForwarder
from pathlib import Path

def get_sqlserver_db_connection_with_ssl(
        server, port, user, password, database, ssl_ca, ssl_cert, ssl_key, ssl_hostname
):
    try:
        conn = connect(
            server=ssl_hostname,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl={
                'ca': ssl_ca,
                'cert': ssl_cert,
                'key': ssl_key,
                'check_hostname': False # TODO Configuração apenas para nivel de teste, para produção necessario a remoção desta linha.
            }
        )

        cursor = conn.cursor(as_dict=True)
        return cursor

    except Exception as e:
        print(f"Failed to connect: {e}")

def get_sqlserver_db_connection_with_ssh_publickey(
        server, port, user, password, database, ssh_host, ssh_port, ssh_user, ssh_key_path, ssh_local_bind_port
):
    try:
        ssh_key_path = Path(ssh_key_path).as_posix()

        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=ssh_key_path,
            remote_bind_address=(server, port),
            local_bind_address=(ssh_host, ssh_local_bind_port),
            set_keepalive=10
        )

        tunnel.start()

        conn = connect(
            server=server,
            port=tunnel.local_bind_port,
            user=user,
            password=password,
            database=database
        )

        cursor = conn.cursor(as_dict=True)
        return cursor

    except Exception as e:
        print(f"Failed to connect: {e}")


def get_sqlserver_db_connection_with_ssh_password(
        server, port, user, password, database, ssh_host, ssh_port, ssh_user, ssh_password, ssh_local_bind_port
):
    try:
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_password=ssh_password,
            remote_bind_address=(server, port),
            local_bind_address=(ssh_host, ssh_local_bind_port),
            set_keepalive=10
        )

        tunnel.start()

        conn = connect(
            server=server,
            port=tunnel.local_bind_port,
            user=user,
            password=password,
            database=database
        )

        cursor = conn.cursor(as_dict=True)
        return cursor

    except Exception as e:
        print(f"Failed to connect: {e}")


def get_sqlserver_connection(server, port, user, password, database):
    conn = connect(server=server, port=port, user=user, password=password, database=database)
    cursor = conn.cursor(as_dict=True)
    return cursor


def convert_retrieved_tuple_name_list_from_sqlserver(table_name_tuple_list):
    table_list = list()
    for table_name in table_name_tuple_list:
        table_list.append(table_name['TABLE_NAME'])
    return table_list


def retrieve_table_name_tuple_list_from_connected_database(connected_database_cursor):
    connected_database_cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
    """)
    response = connected_database_cursor.fetchall()
    return response



def retrieve_table_columns_from_connected_database(table_name, connected_database_cursor):
    sql_query = "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=%s"
    connected_database_cursor.execute(sql_query, (table_name,))
    response = connected_database_cursor.fetchall()
    return response


def retrieve_table_primary_key_from_connected_database(column, table_name, connected_database_cursor):
    sql_query = """
    SELECT Col.Column_Name from INFORMATION_SCHEMA.TABLE_CONSTRAINTS Tab, 
    INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE Col 
    WHERE Col.Constraint_Name=Tab.Constraint_Name AND Col.Table_Name=Tab.Table_Name 
    AND Constraint_Type='PRIMARY KEY' AND Col.Table_Name=%s AND col.Column_name = %s
    """
    connected_database_cursor.execute(sql_query, (table_name, column))
    response = connected_database_cursor.fetchall()
    return response


def retrieve_table_foreign_key_from_connected_database(column, table_name, connected_database_cursor):
    sql_query = """
    SELECT Col.Column_Name from INFORMATION_SCHEMA.TABLE_CONSTRAINTS Tab, 
    INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE Col 
    WHERE Col.Constraint_Name=Tab.Constraint_Name AND Col.Table_Name=Tab.Table_Name 
    AND Constraint_Type='FOREIGN KEY' AND Col.Table_Name=%s AND col.Column_name = %s
    """
    connected_database_cursor.execute(sql_query, (table_name, column))
    response = connected_database_cursor.fetchall()
    return response


def retrieve_table_unique_from_connected_database(column, table_name, connected_database_cursor):
    sql_query = """
    SELECT Col.Column_Name from INFORMATION_SCHEMA.TABLE_CONSTRAINTS Tab, 
    INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE Col 
    WHERE Col.Constraint_Name=Tab.Constraint_Name AND Col.Table_Name=Tab.Table_Name 
    AND Constraint_Type='UNIQUE' AND Col.Table_Name=%s AND col.Column_name = %s
    """
    connected_database_cursor.execute(sql_query, (table_name, column))
    response = connected_database_cursor.fetchall()
    return response


def retrieve_table_auto_incremente_from_connected_database(column, table_name, connected_database_cursor):
    sql_query = "SELECT name, is_identity FROM sys.columns WHERE OBJECT_ID=OBJECT_ID(%s) AND name=%s"
    connected_database_cursor.execute(sql_query, (table_name, column))
    fetch = connected_database_cursor.fetchall()
    response = next((_object for _object in fetch), dict())
    return response.get('is_identity', False)


def retrieve_references_table_foreign_keys_from_tables_from_connected_database(column, table_name, connected_database_cursor):
    sql_query = """
    SELECT 
        obj.name AS FK_NAME, 
        sch.name AS [schema_name], 
        tab1.name AS [table], 
        col1.name AS [column], 
        tab2.name AS [referenced_table], 
        col2.name AS [referenced_column] 
    FROM 
        sys.foreign_key_columns fkc 
    INNER JOIN 
        sys.objects obj ON obj.object_id = fkc.constraint_object_id 
    INNER JOIN 
        sys.tables tab1 ON tab1.object_id = fkc.parent_object_id 
    INNER JOIN 
        sys.schemas sch ON tab1.schema_id = sch.schema_id 
    INNER JOIN 
        sys.columns col1 ON col1.column_id = parent_column_id AND col1.object_id = tab1.object_id 
    INNER JOIN 
        sys.tables tab2 ON tab2.object_id = fkc.referenced_object_id 
    INNER JOIN 
        sys.columns col2 ON col2.column_id = referenced_column_id AND col2.object_id = tab2.object_id 
    WHERE 
        tab1.name = %s AND col1.name = %s
    """
    connected_database_cursor.execute(sql_query, (table_name, column))
    fetch = connected_database_cursor.fetchall()
    response = next((_object for _object in fetch), dict())
    return response
