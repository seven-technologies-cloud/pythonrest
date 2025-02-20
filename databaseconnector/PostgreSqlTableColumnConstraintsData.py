from databaseconnector.PythonTypesUtils import get_python_type
from databaseconnector.SqlAlchemyTypesUtils import get_sa_type
from databaseconnector.ColumnNameFormatter import adding_replace_in_column_name_with_spaces

class PostgreSqlTableColumnConstraintsData:
    def __init__(self, column_metadata, column_fk, pk_status, u_status):

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
            column_metadata['column_default'], self.python_type)
        self.referenced_table_name = column_fk['referenced_table']
        self.referenced_column_name = column_fk['referenced_column']

    def handle_default_value(self, default_value, python_type):
        if python_type == 'bool' and default_value is not None:
            return False if default_value == '0' else True

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
            print(f"Type of array: {column_metadata['udt_name']}")
            array_type = input('Array type: ')
            return f'ARRAY({array_type})'
        else:
            return sa_type
