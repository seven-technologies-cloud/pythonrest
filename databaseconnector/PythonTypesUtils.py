from databaseconnector.SqlAlchemyTypesUtils import *


def get_str_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_string_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_string_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_string_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_string_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_string_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_string_types_list()


def get_bytes_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_bytes_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_bytes_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_bytes_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_bytes_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_bytes_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_bytes_types_list()


def get_int_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_int_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_int_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_int_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_int_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_int_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_int_types_list()


def get_float_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_float_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_float_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_float_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_float_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_float_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_float_types_list()


def get_bool_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_bool_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_bool_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_bool_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_bool_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_bool_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_bool_types_list()


def get_list_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_list_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_list_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_list_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_list_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_list_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_list_types_list()


def get_dict_type_list(database):
    if database == 'MYSQL':
        return get_sa_MySQL_dict_types_list()
    if database == 'AuSQL':
        return get_sa_AuSQL_dict_types_list()
    if database == 'MaSQL':
        return get_sa_MaSQL_dict_types_list()
    if database == 'OcSQL':
        return get_sa_OcSQL_dict_types_list()
    if database == 'PgSQL':
        return get_sa_PgSQL_dict_types_list()
    if database == 'SeSQL':
        return get_sa_SeSQL_dict_types_list()


def get_exceptional_sql_type(column_type, database):
    if database == "MYSQL":
        if "tinyint(1)" in column_type.lower():
            return "bool"


def get_python_type(column_type, database):
    str_type_list = get_str_type_list(database)
    bytes_type_list = get_bytes_type_list(database)
    int_type_list = get_int_type_list(database)
    float_type_list = get_float_type_list(database)
    bool_type_list = get_bool_type_list(database)
    list_type_list = get_list_type_list(database)
    dict_type_list = get_dict_type_list(database)

    types_list_object = {'str': str_type_list, 'bytes': bytes_type_list, 'int': int_type_list, 'float': float_type_list,
                        'bool': bool_type_list, 'list': list_type_list, 'dict': dict_type_list}

    sql_exceptional = get_exceptional_sql_type(column_type, database)

    if sql_exceptional is not None:
        return sql_exceptional

    for python_type, type_list in types_list_object.items():
        is_type = next((True for sql_type in type_list if sql_type.lower() in column_type.lower()), False)

        if is_type:
            return python_type
