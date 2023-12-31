from databaseconnector.PythonTypesUtils import get_python_type
from databaseconnector.SqlAlchemyTypesUtils import get_sa_type


class MySqlTableColumnFieldData:
    def __init__(self, column):

        self.name = column['Field']
        self.primary_key = True if column['Key'] == "PRI" else False
        self.nullable = True if column['Null'] == "YES" else False
        self.unique = True if column['Key'] == "UNI" else False
        self.auto_increment = True if 'auto_increment' in column['Extra'] else False
        self.python_type = get_python_type(column['Type'], 'MYSQL')
        self.sa_type = get_sa_type(column['Type'], self.python_type) if " " not in column['Type'] else get_sa_type(column['Type'][:column['Type'].index(" ")], self.python_type)
        self.default_value = handle_default_value(column['Default'], self.python_type)


def handle_default_value(default_value, python_type):
    if python_type == 'bool' and default_value is not None:
        return False if default_value == '0' else True
