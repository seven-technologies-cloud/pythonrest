from pymysql import *
from databaseconnector.JSONDictHelper import retrieve_json_from_sql_query


def get_mysql_db_connection(_host, _port, _user, _password, _database):
    con = connect(host=_host, port=_port, user=_user,
                  password=_password, database=_database)
    cursor = con.cursor()
    return cursor


def retrieve_table_constraints(schema, table_name, connected_schema):
    sql_query = """
    SELECT * 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_TYPE='FOREIGN KEY' 
      AND TABLE_SCHEMA=%s 
      AND TABLE_NAME=%s
    """

    params = (schema, table_name)

    return retrieve_json_from_sql_query(sql_query, connected_schema, params)


def convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_name_list):
    table_list = list()
    for table in tuple_name_list:
        table_list.append(table[0])
    return table_list


def retrieve_table_name_tuple_list_from_connected_schema(connected_schema):
    connected_schema.execute('SHOW tables')
    response = connected_schema.fetchall()
    return response


def retrieve_table_field_metadata(table_name, connected_schema):
    try:
        return retrieve_json_from_sql_query(f'SHOW FIELDS FROM {table_name}', connected_schema)
    except:
        return retrieve_json_from_sql_query(f'SHOW FIELDS FROM `{table_name}`', connected_schema)


def retrieve_table_relative_column_constraints(column_name, table_name, schema, connected_schema):
    sql_query = """
    SELECT `REFERENCED_TABLE_NAME`, `REFERENCED_COLUMN_NAME`, `COLUMN_NAME`
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `CONSTRAINT_SCHEMA` = %s AND `REFERENCED_TABLE_SCHEMA` IS NOT NULL 
      AND `REFERENCED_TABLE_NAME` IS NOT NULL AND `COLUMN_NAME` = %s 
      AND `TABLE_NAME` = %s AND `REFERENCED_COLUMN_NAME` IS NOT NULL;
    """

    params = (schema, column_name, table_name)

    result = retrieve_json_from_sql_query(sql_query, connected_schema, params)
    return result[0] if result else {}
