from databaseconnector.PythonTypesUtils import get_python_type
from databaseconnector.SqlAlchemyTypesUtils import get_sa_type
from databaseconnector.ColumnNameFormatter import adding_replace_in_column_name_with_spaces

class MySqlTableColumnConstraintsData:
    def __init__(self, column, table_origin_foreign_key):

        self.name = column['Field'].replace('\\', '\\\\') if '\\' in column['Field'] else column['Field']
        self.key = adding_replace_in_column_name_with_spaces(column['Field'])
        self.primary_key = True if column['Key'] == "PRI" else False
        self.nullable = True if column['Null'] == "YES" else False
        self.unique = True if column['Key'] == "UNI" else False
        self.auto_increment = True if 'auto_increment' in column['Extra'] else False
        self.python_type = get_python_type(column['Type'], "MYSQL")
        self.sa_type = get_sa_type(column['Type'], self.python_type, "MYSQL")
        self.default_value = handle_default_value(
            column['Default'], self.python_type)
        self.referenced_table_name = table_origin_foreign_key["REFERENCED_TABLE_NAME"]
        self.referenced_column_name = table_origin_foreign_key["REFERENCED_COLUMN_NAME"]


def handle_default_value(default_value, python_type):
    if python_type == 'bool' and default_value is not None:
        return False if default_value == '0' else True
