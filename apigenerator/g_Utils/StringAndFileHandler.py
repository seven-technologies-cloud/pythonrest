def create_replace_list_string(id_name_list):
    id_replace_string = ''
    for id_name in id_name_list:
        id_replace_string = id_replace_string + '{' + id_name + '}/'
    return id_replace_string[1:-2]


def copy_file_and_replace_lines(domain_name, origin_file, destination_file):
    with open(origin_file, 'r') as py_file_in:
        content = py_file_in.readlines()
    with open(destination_file, 'a') as py_file_out:
        for line in content:
            if 'meta_string' in line:
                line = line.replace('meta_string', domain_name.lower())
            if 'declarative_meta' in line:
                line = line.replace('declarative_meta', domain_name)
            py_file_out.write(line)
