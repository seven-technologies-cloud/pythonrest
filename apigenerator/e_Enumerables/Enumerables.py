import os


def get_database_relation():
    database_relation = {'mysql': '1', 'pgsql': '2', 'mssql': '3', 'mariadb': '4'}
    return database_relation


def get_directory_data():
    data = dict()
    data['domain_test_path'] = os.environ.get('domain_folder')
    data['base_proj_path'] = "apigenerator/resources/1 - Project/1 - BaseProject/Project"
    data['result_path_suffix'] = "PythonRestAPI"
    data['class_generic_path'] = "apigenerator/resources/1 - Project/3 - ClassGeneric"
    data['resource_path'] = "apigenerator/resources"
    data['db_dependencies'] = "apigenerator/resources/1 - Project/2 - Database/database_dependencies/"
    data['db_conn_files'] = "apigenerator/resources/1 - Project/2 - Database/database_conn_files/"
    data['db_conn_resolvers'] = "apigenerator/resources/1 - Project/2 - Database/conn_resolvers/"
    return data


def get_string_list():
    string_list = ['String', 'TIMESTAMP', 'TIME', 'Time', 'Date', 'JSON', 'BLOB', 'DateTime', 'BINARY', 'Binary',
                   'CHAR', 'CLOB', 'DATE', 'DATETIME', 'Enum', 'Interval', 'LargeBinary', 'NCHAR', 'NVARCHAR',
                   'TEXT', 'Text', 'Unicode', 'UnicodeText', 'VARBINARY', 'VARCHAR', 'UUID', 'MONEY']
    return string_list


def get_integer_list():
    integer_list = ['BIGINT', 'BigInteger', 'INTEGER', 'Integer', 'SMALLINT', 'SmallInteger']
    return integer_list


def get_number_list():
    number_list = ['DECIMAL', 'FLOAT', 'Float', 'NUMERIC', 'Numeric', 'REAL']
    return number_list


def get_boolean_list():
    boolean_list = ['BOOLEAN', 'Boolean']
    return boolean_list


def get_array_list():
    array_list = ['ARRAY']
    return array_list


def get_object_list():
    object_list = []
    return object_list

