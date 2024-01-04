import os
from os import listdir
from apigenerator.g_Utils.OpenFileExeHandler import open


# Method modifies all operation files in a logical sequence #
def modify_operation_files(declarative_meta, result_path):
    # Modifying App.py #
    modify_single_operation_file(declarative_meta,
                                 result_path,
                                 'app.py',
                                 '# Controller Imports #\n',
                                 'from src.a_Presentation.a_Domain.',
                                 'Controller import *\n')


def modify_single_operation_file(declarative_meta, result, input_file_name,
                                 entry_point, row_prefix, row_suffix):
    with open(os.path.join(result, f'{input_file_name}'), 'r') as file_in:
        file_data = file_in.readlines()
    with open(os.path.join(result, f'{input_file_name}'), "w") as file_out:
        for line in file_data:
            if line == entry_point:
                line = line + row_prefix + declarative_meta + row_suffix
            file_out.write(line)


def modify_main_conn_resolver(result_full_path, db_meta, db_string):
    with open(os.path.join(result_full_path, 'src', 'e_Infra', 'c_Resolvers', 'MainConnectionResolver.py'),
              "r") as main_conn_in:
        content = main_conn_in.readlines()
    with open(os.path.join(result_full_path, 'src', 'e_Infra', 'c_Resolvers', 'MainConnectionResolver.py'),
              "w") as main_conn_out:
        for line in content:
            if line == "# Connection Imports #\n":
                line = line + "from src.e_Infra.c_Resolvers." + db_meta + "ConnectionResolver import *\n"
            if "global main_conn" in line:
                line = line + "\n    if os.environ['main_db_conn'] == '" + db_string + "':\n" \
                              "        main_conn = get_" + db_string + "_connection_session()\n" \
                              "        return main_conn\n"
            main_conn_out.write(line)


def modify_domain_files_no_pk(result):
    for file in listdir(os.path.join(result, 'src', 'c_Domain')):
        if not file.startswith('_'):
            with open(os.path.join(result, 'src', 'c_Domain', file), 'r') as file_in:
                content = file_in.readlines()
            with open(os.path.join(result, 'src', 'c_Domain', file), 'w') as file_out:
                no_pk = next((False for line in content if 'primary_key=True' in line), True)
                if no_pk:
                    line_to_change = next(line for line in content if '= sa.' in line)
                    for line in content:
                        if line == line_to_change:
                            file_out.write((line.rstrip() + '\n').replace(')\n', ', primary_key=True)\n'))
                        else:
                            file_out.write(line)
                else:
                    for line in content:
                        file_out.write(line)
