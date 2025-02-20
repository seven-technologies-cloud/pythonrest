from databaseconnector.PythonTypesUtils import get_python_type
from databaseconnector.SqlAlchemyTypesUtils import get_sa_type
from databaseconnector.ColumnNameFormatter import adding_replace_in_column_name_with_spaces

class PostgreSqlTableColumnFieldData:
    def __init__(self, column_metadata, pk_status, u_status):

        self.name = column_metadata['column_name'].replace('\\', '\\\\') if '\\' in column_metadata['column_name'] else column_metadata['column_name']
        self.key = adding_replace_in_column_name_with_spaces(column_metadata['column_name'])
        self.primary_key = pk_status
        self.nullable = True if column_metadata['is_nullable'] == "YES" else False
        self.unique = u_status
        self.auto_increment = True if column_metadata['auto_increment'] == 1 else False
        self.python_type = get_python_type(
            column_metadata['data_type'], 'PgSQL')
        self.sa_type = self.handler_sa_value(get_sa_type(column_metadata['data_type'], self.python_type, 'PgSQL') if ' ' not in column_metadata['data_type'] else get_sa_type(
            column_metadata['data_type'][:column_metadata['data_type'].index(' ')], self.python_type, 'PgSQL'), column_metadata['character_maximum_length'], column_metadata['numeric_precision'], column_metadata['numeric_scale'], column_metadata)
        self.default_value = self.handle_default_value(
            column_metadata['column_default'], self.python_type, self.auto_increment)

    def handle_default_value(self, default_value, python_type, auto_increment):
        if python_type == 'bool' and default_value is not None:
            return False if default_value == '0' else True
        if default_value is not None and auto_increment == False:
            return default_value

    def handler_sa_value(self, sa_type, character_length, numeric_precision, numeric_scale, column_metadata):
        if sa_type == 'CHAR' and character_length == 36:
            return f'{sa_type}({character_length})'
        if sa_type == 'CHAR' and character_length != 36:
            return F'VARCHAR({character_length})'
        if sa_type == 'CHAR' and character_length is None:
            return 'VARCHAR'
        if sa_type == 'NUMERIC' and numeric_precision is not None and numeric_scale is not None:
            return f'{sa_type}({numeric_precision}, {numeric_scale})'
        if sa_type == 'ARRAY':
            try:
                return self.handle_array_type(column_metadata['udt_name'])
            except Exception as e:
                print(f"Type of array: {column_metadata['udt_name']}")
                array_type = input('Array type: ')
                return f'ARRAY({array_type})'
        else:
            return sa_type

    def handle_array_type(self, udt_name):
        array_type_map = {
            '_int2': 'Integer',
            '_int4': 'Integer',
            '_int8': 'Integer',
            '_text': 'String',
            '_varchar': 'String',
            '_char': 'String',
            '_float4': 'Float',
            '_float8': 'Float',
            '_bool': 'Boolean',
            '_uuid': 'UUID',
            '_json': 'JSON',
            '_jsonb': 'JSON',
            '_int2[]': 'Integer',
            '_int4[]': 'Integer',
            '_int8[]': 'Integer',
            '_text[]': 'String',
            '_varchar[]': 'String',
            '_char[]': 'String',
            '_float4[]': 'Float',
            '_float8[]': 'Float',
            '_bool[]': 'Boolean',
            '_uuid[]': 'UUID',
            '_json[]': 'JSON',
            '_jsonb[]': 'JSON',
        }
        if udt_name in array_type_map:
            return f'ARRAY(sa.{array_type_map[udt_name]})'
        else:
            '''
            Unsupported types will fall on this else, like:
            '_date': 'Date',
            '_timestamp': 'DateTime',
            '_date[]': 'Date',
            '_timestamp[]': 'DateTime',
            '_int2range': 'Integer',
            '_int4range': 'Integer',
            '_int8range': 'Integer',
            '_numrange': 'Integer',  # Numeric ranges are stored as integers in SQLAlchemy
            '_tsrange': 'DateTime',  # Timestamp ranges are stored as DateTime in SQLAlchemy
            '_tstzrange': 'DateTime',  # Timestamp with time zone ranges are stored as DateTime in SQLAlchemy
            '_daterange': 'Date',  # Date ranges are stored as Date in SQLAlchemy
            '_int4range[]': 'Integer',
            '_int8range[]': 'Integer',
            '_numrange[]': 'Integer',
            '_tsrange[]': 'DateTime',
            '_tstzrange[]': 'DateTime',
            '_daterange[]': 'Date',
            '_box': 'String',
            '_circle': 'String',
            '_path': 'String',
            '_polygon': 'String',
            '_line': 'String',
            '_lseg': 'String',
            '_macaddr': 'String',
            '_macaddr8': 'String',
            '_inet': 'String',
            '_cidr': 'String',
            '_xml': 'String',
            '_tsvector': 'String',
            '_tsquery': 'String',
            '_point': 'String',
            '_varbit': 'String',
            '_bit': 'String',
            '''
            return 'String'

