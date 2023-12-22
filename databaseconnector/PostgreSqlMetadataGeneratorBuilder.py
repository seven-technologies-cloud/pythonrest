from psycopg2 import *
from databaseconnector.JSONDictHelper import retrieve_json_from_sql_query


def get_postgresql_db_connection(_dbname, _host, _port, _user, _password, _schema):
    conn = connect(dbname=_dbname, host=_host, user=_user, password=_password, port=_port, options=f'-c search_path={_schema}')
    cursor = conn.cursor()
    return cursor

def convert_retrieved_table_name_tuple_list_from_connected_schema(tuple_name_list):
    table_list = list()
    for table in tuple_name_list:
        table_list.append(table[0])
    return table_list


def retrieve_table_name_tuple_list_from_connected_schema(connected_db, schema_name):

    connected_db.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}' ORDER BY table_name")
    response = connected_db.fetchall()
    return response


def retrieve_table_field_metadata(table_name, schema_name, connected_db):

    return retrieve_json_from_sql_query(f"SELECT column_name, is_nullable, data_type, character_maximum_length, numeric_precision, numeric_scale, column_default, udt_name FROM information_schema.columns WHERE table_name='{table_name}' AND table_schema='{schema_name}'", connected_db)


def retrieve_auto_increment_from_column(column_name, table_name, connected_db):

    all_table_constraints = retrieve_json_from_sql_query(f"SELECT count(*) FROM pg_class AS t JOIN pg_attribute AS a ON a.attrelid=t.oid JOIN pg_depend AS d ON d.refobjid=t.oid AND d.refobjsubid=a.attnum JOIN pg_class AS s ON s.oid=d.objid WHERE d.classid = 'pg_catalog.pg_class':: regclass AND d.refclassid = 'pg_catalog.pg_class':: regclass AND t.relkind IN('r', 'P') AND s.relkind='S' AND t.relname='{table_name}' AND a.attname='{column_name}'", connected_db)

    return all_table_constraints if all_table_constraints != list() else dict()


def get_constraints_primary_keys(table_name, schema_name, connected_db):

    return retrieve_json_from_sql_query(f"WITH unnested_confkey AS(SELECT oid, unnest(confkey) as confkey FROM pg_constraint), unnested_conkey AS(SELECT oid, unnest(conkey) as conkey FROM pg_constraint) select distinct c.conname AS constraint_name, c.contype AS constraint_type, tbl.relname AS constraint_table, col.attname AS constraint_column, referenced_tbl.relname AS referenced_table, referenced_field.attname AS referenced_column, pg_get_constraintdef(c.oid) AS definition FROM pg_constraint c LEFT JOIN unnested_conkey con ON c.oid=con.oid LEFT JOIN pg_class tbl ON tbl.oid=c.conrelid LEFT JOIN pg_attribute col ON(col.attrelid=tbl.oid AND col.attnum=con.conkey)LEFT JOIN pg_class referenced_tbl ON c.confrelid=referenced_tbl.oid LEFT JOIN unnested_confkey conf ON c.oid=conf.oid LEFT JOIN pg_attribute referenced_field ON(referenced_field.attrelid=c.confrelid AND referenced_field.attnum=conf.confkey) LEFT JOIN information_schema.constraint_column_usage ccu on c.conname=ccu.constraint_name WHERE ccu.table_schema= '{schema_name}' AND tbl.relname='{table_name}' AND c.contype = 'p'", connected_db)


def get_constraints_foreign_key(table_name, schema_name, connected_db):

    return retrieve_json_from_sql_query(f"WITH unnested_confkey AS(SELECT oid, unnest(confkey) as confkey FROM pg_constraint), unnested_conkey AS(SELECT oid, unnest(conkey) as conkey FROM pg_constraint) select distinct c.conname AS constraint_name, c.contype AS constraint_type, tbl.relname AS constraint_table, col.attname AS constraint_column, referenced_tbl.relname AS referenced_table, referenced_field.attname AS referenced_column, pg_get_constraintdef(c.oid) AS definition FROM pg_constraint c LEFT JOIN unnested_conkey con ON c.oid=con.oid LEFT JOIN pg_class tbl ON tbl.oid=c.conrelid LEFT JOIN pg_attribute col ON(col.attrelid=tbl.oid AND col.attnum=con.conkey)LEFT JOIN pg_class referenced_tbl ON c.confrelid=referenced_tbl.oid LEFT JOIN unnested_confkey conf ON c.oid=conf.oid LEFT JOIN pg_attribute referenced_field ON(referenced_field.attrelid=c.confrelid AND referenced_field.attnum=conf.confkey) LEFT JOIN information_schema.constraint_column_usage ccu on c.conname=ccu.constraint_name WHERE ccu.table_schema= '{schema_name}' AND tbl.relname='{table_name}' AND c.contype = 'f'", connected_db)


def get_constraints_unique(table_name, schema_name, connected_db):

    return retrieve_json_from_sql_query(f"WITH unnested_confkey AS(SELECT oid, unnest(confkey) as confkey FROM pg_constraint), unnested_conkey AS(SELECT oid, unnest(conkey) as conkey FROM pg_constraint) select distinct c.conname AS constraint_name, c.contype AS constraint_type, tbl.relname AS constraint_table, col.attname AS constraint_column, referenced_tbl.relname AS referenced_table, referenced_field.attname AS referenced_column, pg_get_constraintdef(c.oid) AS definition FROM pg_constraint c LEFT JOIN unnested_conkey con ON c.oid=con.oid LEFT JOIN pg_class tbl ON tbl.oid=c.conrelid LEFT JOIN pg_attribute col ON(col.attrelid=tbl.oid AND col.attnum=con.conkey)LEFT JOIN pg_class referenced_tbl ON c.confrelid=referenced_tbl.oid LEFT JOIN unnested_confkey conf ON c.oid=conf.oid LEFT JOIN pg_attribute referenced_field ON(referenced_field.attrelid=c.confrelid AND referenced_field.attnum=conf.confkey) LEFT JOIN information_schema.constraint_column_usage ccu on c.conname=ccu.constraint_name WHERE ccu.table_schema= '{schema_name}' AND tbl.relname='{table_name}' AND c.contype = 'u'", connected_db)


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
