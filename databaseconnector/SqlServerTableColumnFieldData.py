from databaseconnector.PythonTypesUtils import get_python_type
from databaseconnector.SqlAlchemyTypesUtils import get_sa_type
from databaseconnector.ColumnNameFormatter import adding_replace_in_column_name_with_spaces

class SqlServerTableColumnFieldData:
    def __init__(self, column_metadata, primary_key_column, unique_column, auto_increment):


        self.name = column_metadata['COLUMN_NAME'].replace('\\', '\\\\') if '\\' in column_metadata['COLUMN_NAME'] else column_metadata['COLUMN_NAME']
        self.key = adding_replace_in_column_name_with_spaces(column_metadata['COLUMN_NAME'])
        self.primary_key = False if primary_key_column == list() else True
        self.nullable = True if column_metadata['IS_NULLABLE'] == "YES" else False
        self.unique = False if unique_column == list() else False
        self.auto_increment = auto_increment
        self.python_type = get_python_type(
            column_metadata['DATA_TYPE'], 'SeSQL')
        self.sa_type = handler_sa_value(get_sa_type(column_metadata['DATA_TYPE'], self.python_type, 'SeSQL') if ' ' not in column_metadata['DATA_TYPE'] else get_sa_type(
            column_metadata['DATA_TYPE'][:column_metadata['DATA_TYPE'].index(' ')], self.python_type, 'SeSQL'), column_metadata['CHARACTER_MAXIMUM_LENGTH'], column_metadata['NUMERIC_PRECISION'], column_metadata['NUMERIC_SCALE'])

        self.default_value = handle_default_value(
            column_metadata['COLUMN_DEFAULT'], self.python_type)


def handle_default_value(default_value, python_type):
    if python_type == 'bool' and default_value is not None:
        return False if default_value == '0' else True


def handler_sa_value(sa_type, character_length, numeric_precision, numeric_scale):
    if sa_type == 'CHAR' and character_length == 36:
        return f'{sa_type}({character_length})'
    if sa_type == 'CHAR' and character_length != 36:
        return F'VARCHAR({character_length})'
    if sa_type == 'CHAR' and character_length is None:
        return 'VARCHAR'
    if sa_type == 'NUMERIC' and numeric_precision is not None and numeric_scale is not None:
        return f'{sa_type}({numeric_precision}, {numeric_scale})'
    else:
        return sa_type
