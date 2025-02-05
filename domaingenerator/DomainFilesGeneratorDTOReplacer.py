
def get_columns_names_str(domain_dict):
    columns_list = [column['key'] for column in domain_dict['Columns']] + \
        [constraint['key'] for constraint in domain_dict['Constraints']]
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
                result_string = result_string + tab + column['key'] + ": " + column['python_type'].replace(
                    'bytes', 'str') + ' = sa.Column(' + column['sa_type'] + get_column_arguments_string(column) + ')\n'
            else:
                result_string = result_string + tab + column['key'] + ": " + column['python_type'].replace(
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
    if column['name']:
        arguments_string = arguments_string + f', name="{column["name"]}"'
    if column['key']:
        arguments_string = arguments_string + f', key="{column["key"]}"'
    if column['default_value'] is not None:
        arguments_string = arguments_string + ', server_default=sa.FetchedValue()'
    return arguments_string


def get_constraint_argument(constraint, table_name):
    if constraint['referenced_table_name'] == table_name:
        return ', sa.ForeignKey(' + constraint['referenced_column_name'] + ')'
    else:
        return ', sa.ForeignKey("' + constraint['referenced_table_name'] + '.' + constraint['referenced_column_name'] + '")'



def get_columns_init(domain_dict):
    columns_init_str = ''
    columns = domain_dict['Columns'] + domain_dict['Constraints']

    for column in columns:
        columns_init_str = columns_init_str + ', ' + column['key'] + '=None'

    return columns_init_str


def get_self_columns(domain_dict):
    self_columns_str = ''
    columns = domain_dict['Columns'] + domain_dict['Constraints']
    tab = '        '

    for column in columns:
        if column['python_type'] == 'bytes':
            self_columns_str = self_columns_str + tab + 'self.' + \
                column['key'] + ' = ' + 'str.encode(' + column['key'] + ') if ' + \
                column['key'] + ' else ' + column['key'] + '\n'
        else:
            self_columns_str = self_columns_str + tab + 'self.' + \
                column['key'] + ' = ' + column['key'] + '\n'

    return self_columns_str
