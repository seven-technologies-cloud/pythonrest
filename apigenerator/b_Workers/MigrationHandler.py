import os
from apigenerator.g_Utils.OpenFileExeHandler import open


# Method handles all migrations from declarative_meta (and other argument) definitions #
def handle_generic_classes_migration(declarative_meta, meta_string, id_from_file,
                                     result, class_generic_path):
    # Handling Meta Controller #
    if id_from_file:
        # Handling Meta Controller #
        handle_migration(declarative_meta, meta_string, id_from_file, class_generic_path,
                         os.path.join(result, 'src', 'a_Presentation', 'a_Domain'),
                         "Controller")
    if not id_from_file:
        # Handling Meta Controller #
        handle_migration(declarative_meta, meta_string, id_from_file, class_generic_path,
                         os.path.join(result, 'src', 'a_Presentation', 'a_Domain'),
                         "ControllerNoPK")

    # Handling Meta Repository #
    handle_migration(declarative_meta, meta_string, id_from_file, class_generic_path,
                     os.path.join(result, 'src', 'd_Repository', 'a_Domain'),
                     "Repository")

    if id_from_file:
        # Handling Meta Service #
        handle_migration(declarative_meta, meta_string, id_from_file, class_generic_path,
                         os.path.join(result, 'src', 'b_Application', 'b_Service', 'a_Domain'),
                         "Service")
    if not id_from_file:
        # Handling Meta Service #
        handle_migration(declarative_meta, meta_string, id_from_file, class_generic_path,
                         os.path.join(result, 'src', 'b_Application', 'b_Service', 'a_Domain'),
                         "ServiceNoPK")

    # Handling Meta Validator #
    handle_migration(declarative_meta, meta_string, id_from_file, class_generic_path,
                     os.path.join(result, 'src', 'e_Infra', 'd_Validators', 'a_Domain'),
                     "Validator")


# Method migration from a single declarative_meta (and other argument) definitions #
def handle_migration(declarative_meta, meta_string, id_from_file, gen_src_path, dst_path, op_class):
    with open(('{}/Control{}.py'.format(gen_src_path, op_class)), "rt") as file_in:
        # Working destination file #
        with open(os.path.join(dst_path, f'{declarative_meta}{op_class.replace("NoPK", "")}.py'), 'wt') as file_out:
            # Writing on destination file #
            if op_class == 'Service':
                for line in file_in:
                    file_out.write(line
                                   .replace("control", meta_string)
                                   .replace("Control", declarative_meta)
                                   .replace("=id_name_list", '=' + str(id_from_file)))

            if op_class == 'Controller' or op_class == "ControllerNoPK":
                for line in file_in:
                    if '@app_handler.route' in line:
                        file_out.write(line
                                       .replace("control", meta_string.replace('_', ''))
                                       .replace("id_path", create_replace_list_string_flask(id_from_file)))
                    else:
                        file_out.write(line
                                       .replace("control", meta_string)
                                       .replace("Control", declarative_meta)
                                       .replace("id_list", str(id_from_file).replace('"', '').replace("'", ''))
                                       .replace("id_args", ', '.join(id_from_file)))
            else:
                for line in file_in:
                    file_out.write(line
                                   .replace("control", meta_string)
                                   .replace("Control", declarative_meta)
                                   .replace("id_control", str(id_from_file)))


def create_replace_list_string_flask(id_name_list):
    id_replace_string = ''
    for id_name in id_name_list:
        id_replace_string = id_replace_string + '<' + id_name + '>/'
    return id_replace_string[1:-2]
