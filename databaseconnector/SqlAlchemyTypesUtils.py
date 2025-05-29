import sys
import os


######################################################################################################################## SaAuSQLTypes
def get_sa_AuSQL_string_types_list():
    return ['String', 'TIMESTAMP', 'timestamp', 'TIME', 'Time', 'Date', 'JSON', 'DateTime',
            'CHAR',  'DATE', 'DATETIME', 'Enum', 'Interval', 'NCHAR', 'NVARCHAR',
            'TEXT', 'Text', 'Unicode', 'UnicodeText', 'VARCHAR']


def get_sa_AuSQL_bytes_types_list():
    return ['Binary', 'BLOB', 'BINARY', 'CLOB', 'LargeBinary', 'VARBINARY']


def get_sa_AuSQL_int_types_list():
    return ['Integer', 'BIGINT', 'BigInteger',
            'INTEGER', 'SMALLINT', 'SmallInteger']


def get_sa_AuSQL_float_types_list():
    return ['Float', 'DECIMAL', 'FLOAT', 'NUMERIC', 'Numeric', 'REAL']


def get_sa_AuSQL_bool_types_list():
    return ['Boolean', 'BOOLEAN']


def get_sa_AuSQL_list_types_list():
    return ['ARRAY']


def get_sa_AuSQL_dict_types_list():
    return []


######################################################################################################################## SaMaSQLTypes
def get_sa_MaSQL_string_types_list():
    return ['String', 'TIMESTAMP', 'timestamp', 'TIME', 'Time', 'Date', 'JSON', 'DateTime',
            'CHAR',  'DATE', 'DATETIME', 'Enum', 'Interval', 'NCHAR', 'NVARCHAR',
            'TEXT', 'Text', 'Unicode', 'UnicodeText', 'VARCHAR']


def get_sa_MaSQL_bytes_types_list():
    return ['Binary', 'BLOB', 'BINARY', 'CLOB', 'LargeBinary', 'VARBINARY']


def get_sa_MaSQL_int_types_list():
    return ['Integer', 'BIGINT', 'BigInteger',
            'INTEGER', 'SMALLINT', 'SmallInteger']


def get_sa_MaSQL_float_types_list():
    return ['Float', 'DECIMAL', 'FLOAT', 'NUMERIC', 'Numeric', 'REAL']


def get_sa_MaSQL_bool_types_list():
    return ['Boolean', 'BOOLEAN']


def get_sa_MaSQL_list_types_list():
    return ['ARRAY']


def get_sa_MaSQL_dict_types_list():
    return []


######################################################################################################################## SaMySQLTypes
def get_sa_MySQL_string_types_list():
    return ['String', 'TIMESTAMP', 'timestamp', 'TIME', 'Time', 'Date', 'JSON', 'DateTime',
            'CHAR',  'DATE', 'DATETIME', 'Enum', 'Set', 'Interval', 'NCHAR', 'NVARCHAR', "YEAR", "year",
            'TEXT', 'Text', 'Unicode', 'UnicodeText', 'VARCHAR',
            'BIT', 'GEOMETRY', 'GEOMETRYCOLLECTION', 'GEOMCOLLECTION', 'POLYGON', 'MULTIPOLYGON', 'MULTILINESTRING']  # On this line there are non-supported types that will be cast to string to avoid errors


def get_sa_MySQL_bytes_types_list():
    return ['Binary', 'BLOB', 'BINARY', 'CLOB', 'LargeBinary', 'VARBINARY']


def get_sa_MySQL_int_types_list():
    return ['Integer', 'BIGINT', 'BigInteger', 'MEDIUMINT', 'TINYINT'
            'INTEGER', 'SMALLINT', 'SmallInteger', 'int']


def get_sa_MySQL_float_types_list():
    return ['Float', 'DECIMAL', 'FLOAT', 'NUMERIC', 'Numeric', 'REAL', 'DOUBLE', 'DOUBLE PRECISION']


def get_sa_MySQL_bool_types_list():
    return ['Boolean', 'BOOLEAN']


def get_sa_MySQL_list_types_list():
    return ['ARRAY']


def get_sa_MySQL_dict_types_list():
    return []


######################################################################################################################## SaOcSQLTypes
def get_sa_OcSQL_string_types_list():
    return ['CHAR', 'VARCHAR2', 'VARCHAR', ]


def get_sa_OcSQL_bytes_types_list():
    return ['Binary', 'BINARY', 'LargeBinary', 'VARBINARY',
            'NCLOB', 'BFILE', 'CLOB', 'BLOB', 'LONG', 'RAW', 'LONG RAW']


def get_sa_OcSQL_int_types_list():
    return ['Integer', 'BIGINT', 'BigInteger',
            'INTEGER', 'SMALLINT', 'SmallInteger']


def get_sa_OcSQL_float_types_list():
    return ['Float', 'DECIMAL', 'FLOAT', 'NUMERIC', 'Numeric', 'REAL']


def get_sa_OcSQL_bool_types_list():
    return ['Boolean', 'BOOLEAN']


def get_sa_OcSQL_list_types_list():
    return ['ARRAY']


def get_sa_OcSQL_dict_types_list():
    return []


######################################################################################################################## SaPgSQLTypes
def get_sa_PgSQL_string_types_list():
    return ['character varying', 'char', 'bpchar', 'BLOB', 'character', 'varchar', 'Binary', 'interval', 'enum', 'ENUM',
            'name', 'CLOB', 'DATE', 'DATETIME', 'Enum', 'Interval', 'LargeBinary', 'time', 'time with time zone',
            'text', 'Unicode', 'UnicodeText', 'VARBINARY', 'UUID', 'date', 'time without time zone', 'XML', 'xml',
            'timestamp with time zone', 'timestamp without time zone', 'timestamp', 'jsonb', 'JSONB', 'inet', 'INET',
            'bit', 'BIT', 'cidr', 'macaddr', 'macaddr8', 'json', 'JSON', 'timestamptz', 'timetz',
            'point', 'line', 'lseg', 'box', 'path', 'polygon', 'circle', 'pg_lsn', 'pg_snapshot',
            'regclass', 'regcollation', 'regconfig', 'regdictionary', 'regnamespace', 'regoper', 'regoperator',
            'regprocedure', 'regtype', 'regrole', 'regproc', 'MONEY',
            'regprocregproc', 'USER-DEFINED','tsvector', 'tsquery',  # On this line there are non-supported types that will be cast to string to avoid errors
            'int4range', 'int8range', 'numrange', 'tsrange', 'tstzrange', 'daterange']  # On this line there are types that support types that will be cast to string to avoid errors


def get_sa_PgSQL_bytes_types_list():
    return ['bytea']


def get_sa_PgSQL_int_types_list():
    return ['smallint', 'integer', 'bigint', 'smallserial', 'serial', 'bigserial', 'oid']


def get_sa_PgSQL_float_types_list():
    return ['Float', 'DECIMAL', 'FLOAT', 'NUMERIC', 'Numeric', 'REAL']


def get_sa_PgSQL_bool_types_list():
    return ['bool', 'boolean']


def get_sa_PgSQL_list_types_list():
    return ['ARRAY', 'GEOMETRY', 'array', 'geometry']


def get_sa_PgSQL_dict_types_list():
    return []


######################################################################################################################## SaSeSQLTypes
def get_sa_SeSQL_string_types_list():
    return ['char', 'varchar', 'text', 'nchar', 'nvarchar', 'ntext', 'date', 'smalldatetime', 'datetime', 'datetime2', 'datetimeoffset', 'time']


def get_sa_SeSQL_bytes_types_list():
    return ['binary', 'varbinary', 'image']


def get_sa_SeSQL_int_types_list():
    return ['bigint', 'numeric', 'bit', 'smallint', 'decimal', 'smallmoney', 'int', 'tinyint']


def get_sa_SeSQL_float_types_list():
    return ['float', 'real']


def get_sa_SeSQL_bool_types_list():
    return ['BOOL', 'bool', 'BOOLEAN', 'boolean']


def get_sa_SeSQL_list_types_list():
    return ['array']


def get_sa_SeSQL_dict_types_list():
    return []

########################################################################################################################


def get_sa_string_types_list():
    return ['String', 'TIMESTAMP', 'timestamp', 'TIME', 'Time', 'Date', 'JSON', 'jsonb', 'JSONB' 'DateTime',
            'CHAR',  'DATE', 'DATETIME', 'Enum', 'Set', 'Interval', 'NCHAR', 'NVARCHAR', 'UUID',
            'TEXT', 'Text', 'Unicode', 'UnicodeText', 'VARCHAR', "YEAR", "year"]


def get_sa_bytes_types_list():
    return ['BLOB', 'BINARY', 'CLOB', 'LargeBinary', 'VARBINARY']


def get_sa_int_types_list():
    return ['Integer', 'BIGINT', 'BigInteger',
            'INTEGER', 'SMALLINT', 'SmallInteger', 'bigint']


def get_sa_float_types_list():
    return ['Float', 'DECIMAL', 'FLOAT', 'NUMERIC', 'Numeric', 'REAL']


def get_sa_bool_types_list():
    return ['Boolean', 'BOOLEAN']


def get_sa_list_types_list():
    return ['ARRAY']


def get_sa_dict_types_list():
    return []

################################################################################################################


def type_with_size(column_type):
    return True if '(' in column_type and ')' in column_type else False


def add_size_to_result(result, column_type):
    return result + column_type[column_type.index('('):]


def get_sa_type_match(type_list, column_type_no_size, python_type_value, python_type):
    first_result = next((sa_type for sa_type in type_list
                        if sa_type.lower() == column_type_no_size.lower() and python_type_value == python_type), None)
    if first_result:
        return first_result

    contains_list = [sa_type for sa_type in type_list
                     if sa_type.lower() in column_type_no_size.lower() and python_type_value == python_type]

    if contains_list != list():
        result = max(contains_list, key=len)
        return result

    third_result = next(
        (sa_type for sa_type in type_list if python_type_value == python_type), None)
    if third_result:
        return third_result


def convert_enum_to_Enum(input_string):
    # Check if the input is in 'enum(...)' format
    if input_string.lower().startswith("enum(") and input_string.lower().endswith(")"):
        # Strip 'enum(' from the start and ')' from the end
        values_string = input_string[5:-1]
    else:
        raise ValueError(
            "Input string is not in the expected format: 'enum(...)'")

    # Extract the values and split by comma, keeping the quotes
    values = [value.strip().strip("'") for value in values_string.split(",")]

    # Create the Enum declaration
    enum_declaration = f"Enum({', '.join(repr(value) for value in values)})"

    return enum_declaration


def convert_set_to_SET(input_string):
    # Check if the input is in 'SET(...)' format
    if input_string.lower().startswith("set(") and input_string.lower().endswith(")"):
        # Strip 'set(' from the start and ')' from the end
        values_string = input_string[4:-1]
    else:
        raise ValueError(
            "Input string is not in the expected format: 'set(...)'")

    # Extract the values and split by comma, keeping the quotes
    values = [value.strip().strip("'") for value in values_string.split(",")]

    # Create the Set declaration
    set_declaration = f"Set({', '.join(repr(value) for value in values)})"

    return set_declaration


def handle_sql_to_sa_types_conversion(column_type):
    if column_type.lower().startswith("enum"):
        converted_column_type = convert_enum_to_Enum(column_type)
        return converted_column_type
    if column_type.lower().startswith("set"):
        converted_column_type = convert_set_to_SET(column_type)
        return converted_column_type
    # TODO remove this when float type casting to Decimal or a way to send data of decimal type on requests is supported by PythonREST
    if "decimal" in column_type.lower() or "numeric" in column_type.lower():
        return "Float"
    if "year" in column_type.lower():  # TODO remove this when YEAR types are fully supported by PythonREST
        return "String"
    if "jsonb" in column_type.lower():
        return "JSON"
    if "money" in column_type.lower():
        return "MONEY"



def get_sa_type(column_type, python_type_value, database):
    base_column_type = column_type.split(" ")[0]

    column_type_no_size = base_column_type.split(
        '(')[0] if '(' in base_column_type else base_column_type

    str_type_list = get_sa_string_types_list()
    bytes_type_list = get_sa_bytes_types_list()
    int_type_list = get_sa_int_types_list()
    float_type_list = get_sa_float_types_list()
    bool_type_list = get_sa_bool_types_list()
    list_type_list = get_sa_list_types_list()
    dict_type_list = get_sa_dict_types_list()

    types_list_object = {'str': str_type_list, 'bytes': bytes_type_list, 'int': int_type_list, 'float': float_type_list,
                         'bool': bool_type_list, 'list': list_type_list, 'dict': dict_type_list}

    converted_type = handle_sql_to_sa_types_conversion(column_type)

    if converted_type is not None:
        return converted_type

    for python_type, type_list in types_list_object.items():
        result = get_sa_type_match(
            type_list, column_type_no_size, python_type_value, python_type)
        if result:
            if type_with_size(column_type):
                if python_type == "int" or python_type == "float" and database == "MYSQL":
                    pass
                else:
                    result = add_size_to_result(result, column_type)
            return result


    sys.exit(f'Unsupported column type: {column_type}')