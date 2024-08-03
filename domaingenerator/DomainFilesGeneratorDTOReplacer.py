def get_domain_imports(domain_dict):
    domain_imports = ''
    constraint_names = list(set([constraint['referenced_class_name']
                            for constraint in domain_dict['Constraints']]))

    for constraint in constraint_names:
        if constraint == domain_dict['ClassName']:
            continue
        domain_imports = domain_imports + \
            f'from src.c_Domain.{constraint} import *\n'
    return domain_imports if domain_imports != '' else 'import ujson\n'


def get_columns_names_str(domain_dict):
    columns_list = [column['name'] for column in domain_dict['Columns']] + \
        [constraint['name'] for constraint in domain_dict['Constraints']]
    sub_string = '", "'.join(columns_list)
    if len(columns_list) == 1:
        return f'"{sub_string}",'
    else:
        return f'"{sub_string}"'


def get_sa_columns(domain_dict):
    result_string = ''
    columns = domain_dict['Columns']
    constraints = domain_dict['Constraints']
    tab = '    '

    for column in columns:
        try:
            if 'Set' in column['sa_type']:
                column['sa_type'] = column['sa_type'].replace('Set', 'SET')
                result_string = result_string + tab + column['name'] + ": " + column['python_type'].replace(
                    'bytes', 'str') + ' = sa.Column(' + column['sa_type'] + get_column_arguments_string(column) + ')\n'
            else:
                result_string = result_string + tab + column['name'] + ": " + column['python_type'].replace(
                    'bytes', 'str') + ' = sa.Column(sa.' + column['sa_type'] + get_column_arguments_string(column) + ')\n'
        except Exception as e:
            print(domain_dict, e)
            return

    for constraint in constraints:
        result_string = result_string + tab + constraint['name'] + ": " + constraint['python_type'].replace(
            'bytes', 'str') + ' = sa.Column(sa.' + constraint['sa_type'] + get_constraint_argument(constraint, domain_dict['TableName']) + get_column_arguments_string(constraint) + ')\n'

    return result_string


def get_column_arguments_string(column):
    arguments_string = ''
    if column['primary_key']:
        arguments_string = arguments_string + ', primary_key=True'
    if not column['nullable']:
        arguments_string = arguments_string + ', nullable=False'
    if column['unique']:
        arguments_string = arguments_string + ', unique=True'
    if column['auto_increment']:
        arguments_string = arguments_string + ', autoincrement=True'
    if column['default_value'] is not None:
        arguments_string = arguments_string + ', server_default=sa.FetchedValue()'
    return arguments_string


def get_constraint_argument(constraint, table_name):
    if constraint['referenced_table_name'] == table_name:
        return ', sa.ForeignKey(' + constraint['referenced_column_name'] + ')'
    else:
        return ', sa.ForeignKey(' + constraint['referenced_class_name'] + '.' + constraint['referenced_column_name'] + ')'


def get_columns_init(domain_dict):
    columns_init_str = ''
    columns = domain_dict['Columns'] + domain_dict['Constraints']

    for column in columns:
        columns_init_str = columns_init_str + ', ' + column['name'] + '=None'

    return columns_init_str


def get_self_columns(domain_dict):
    self_columns_str = ''
    columns = domain_dict['Columns'] + domain_dict['Constraints']
    tab = '        '

    for column in columns:
        if column['python_type'] == 'bytes':
            self_columns_str = self_columns_str + tab + 'self.' + \
                column['name'] + ' = ' + 'str.encode(' + column['name'] + ') if ' + \
                column['name'] + ' else ' + column['name'] + '\n'
        else:
            self_columns_str = self_columns_str + tab + 'self.' + \
                column['name'] + ' = ' + column['name'] + '\n'

    return self_columns_str
