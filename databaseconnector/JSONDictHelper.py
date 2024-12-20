import json
from databaseconnector.RegexHandler import transform_table_name_to_pascal_case_class_name



def retrieve_json_from_sql_query(sql_query, connected_schema, params=None):
    connected_schema.execute(sql_query, params if params else ())
    data = connected_schema.fetchall()

    field_names = [i[0] for i in connected_schema.description]

    result_list = []

    for _object in data:
        new_object = dict()
        for i in range(len(field_names)):
            new_object[field_names[i]] = _object[i]
        result_list.append(new_object)

    return result_list


def create_domain_result_file(table_name, domain_result_folder, use_pascal_case):
    data = dict()
    data["TableName"] = table_name
    if use_pascal_case:
        data["ClassName"] = transform_table_name_to_pascal_case_class_name(table_name)
    else:
        data["ClassName"] = input('Write the classname for the table ' + table_name + ': ')
    data["Columns"] = list()
    data["Constraints"] = list()
    with open(f'{domain_result_folder}/{table_name}.json', 'w') as domain_file:
        domain_file = json.dump(data, domain_file, indent=4)
    return domain_file


def add_table_column_to_json_domain(table_name, field_data, domain_result_folder):
    with open(f'{domain_result_folder}/{table_name}.json', 'r') as f:
        data = json.load(f)

    data["Columns"].append(field_data)

    with open(f'{domain_result_folder}/{table_name}.json', 'w') as domain_file:
        json.dump(data, domain_file, indent=4)


def add_table_constraint_to_json_domain(table_name, table_constraints_data, domain_result_folder):
    with open(f'{domain_result_folder}/{table_name}.json', 'r') as f:
        data = json.load(f)

    # data = dict()
    data["Constraints"].append(table_constraints_data)

    with open(f'{domain_result_folder}/{table_name}.json', 'w') as domain_file:
        json.dump(data, domain_file, indent=4)


def add_referenced_class_name_to_constraints(domain_result_json_file, domain_result_json_files, domain_result_folder):
    referenced_class_name = ''
    with open(f'{domain_result_folder}/' + domain_result_json_file, 'r') as domain_json_file_to_append_data:
        domain_json_file_data = json.load(domain_json_file_to_append_data)
        constraints = domain_json_file_data['Constraints']
        for constraint in constraints:
            for domain_json_file in domain_result_json_files:
                with open(f'{domain_result_folder}/' + domain_json_file, 'r') as domain_json_file:
                    domain_json_data = json.load(domain_json_file)
                table_name = domain_json_data['TableName']
                if constraint['referenced_table_name'] == table_name:
                    constraint.update({'referenced_class_name': str(domain_json_data['ClassName'])})

    with open(f'{domain_result_folder}/' + domain_result_json_file, 'w') as domain_file_to_append_data:
        json.dump(domain_json_file_data, domain_file_to_append_data, indent=4)