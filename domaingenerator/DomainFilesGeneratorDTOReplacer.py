def get_columns_names_str(domain_dict):
    columns_list = [column['key'] for column in domain_dict['Columns']] + \
        [constraint['key'] for constraint in domain_dict['Constraints']]
    sub_string = '", "'.join(columns_list)
    if len(columns_list) == 1:
        return f'"{sub_string}",'
    else:
        return f'"{sub_string}"'


def get_sa_columns(domain_dict):
    parts = []
    columns = domain_dict['Columns']
    constraints = domain_dict['Constraints']
    tab = '    '

    for column in columns:
        try:
            python_type_str = str(column.get('python_type', '')).replace('bytes', 'str')
            sa_type_str = str(column.get('sa_type', ''))
            column_args_str = get_column_arguments_string(column)

            if 'Set' in sa_type_str:
                sa_type_str = sa_type_str.replace('Set', 'SET')
                parts.append(f"{tab}{column['key']}: {python_type_str} = sa.Column({sa_type_str}{column_args_str})\n")
            else:
                parts.append(f"{tab}{column['key']}: {python_type_str} = sa.Column(sa.{sa_type_str}{column_args_str})\n")
        except Exception as e:
            print(f"Error processing column {column.get('key', 'UNKNOWN')} in {domain_dict.get('TableName', 'UNKNOWN_TABLE')}: {e}")
            return ""

    for constraint in constraints:
        try:
            python_type_str = str(constraint.get('python_type', '')).replace('bytes', 'str')
            sa_type_str = str(constraint.get('sa_type', ''))
            constraint_arg_str = get_constraint_argument(constraint, domain_dict['TableName'])
            column_args_str = get_column_arguments_string(constraint)

            parts.append(f"{tab}{constraint['name']}: {python_type_str} = sa.Column(sa.{sa_type_str}{constraint_arg_str}{column_args_str})\n")
        except Exception as e:
            print(f"Error processing constraint {constraint.get('name', 'UNKNOWN')} in {domain_dict.get('TableName', 'UNKNOWN_TABLE')}: {e}")
            return ""

    return "".join(parts)


def get_column_arguments_string(column):
    parts = []
    if column.get('primary_key'):
        parts.append(', primary_key=True')
    if not column.get('nullable', True):
        parts.append(', nullable=False')
    if column.get('unique'):
        parts.append(', unique=True')
    if column.get('auto_increment'):
        parts.append(', autoincrement=True')
    if column.get('name'):
        parts.append(f', name="{column["name"]}"')
    if column.get('default_value') is not None:
        parts.append(', server_default=sa.FetchedValue()')
    return "".join(parts)


def get_constraint_argument(constraint, table_name):
    ref_col_name = constraint['referenced_column_name']
    ref_table_name = constraint['referenced_table_name']
    if ref_table_name == table_name:
        return f", sa.ForeignKey('{ref_col_name}')"
    else:
        return f', sa.ForeignKey("{ref_table_name}.{ref_col_name}")'


def get_columns_init(domain_dict):
    columns = domain_dict['Columns'] + domain_dict['Constraints']
    if not columns:
        return ""
    parts = [f", {column['key']}=None" for column in columns]
    return "".join(parts)


def get_self_columns(domain_dict):
    parts = []
    columns = domain_dict['Columns'] + domain_dict['Constraints']
    tab = '        '

    for column in columns:
        key = column['key']
        python_type_str = str(column.get('python_type', ''))

        if python_type_str == 'bytes':
            parts.append(f"{tab}self.{key} = str.encode({key}) if {key} is not None else None\n")
        else:
            parts.append(f"{tab}self.{key} = {key}\n")

    return "".join(parts)
