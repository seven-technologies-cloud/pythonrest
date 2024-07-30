# System Imports #
import os
import shutil

from apigenerator.b_Workers.DirectoryManager import get_domain_files_list
from apigenerator.g_Utils.StringAndFileHandler import copy_file_and_replace_lines


def add_redoc_blueprint_register_function_to_redoc_controller(destination_file):
    blueprint_register_lines = '\n# Register the blueprint\n\
app_handler.register_blueprint(redoc_blueprint)'
    with open(destination_file, 'a') as py_file_out:
        py_file_out.write(f'{blueprint_register_lines}\n')


def modify_redoc_related_files(result, domain_path, script_absolute_path):
    print('Creating Redoc docs for API')
    domain_list = get_domain_files_list(domain_path)

    if not os.path.exists(os.path.join(result, 'src', 'a_Presentation', 'c_Redoc' 'RedocController.py')):
        shutil.copytree(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/src/a_Presentation/c_Redoc'),
                        os.path.join(result, 'src', 'a_Presentation', 'c_Redoc'), dirs_exist_ok=True)

    if not os.path.exists(os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskBuilder.py')):
        shutil.copy(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/src/e_Infra/b_Builders/FlaskBuilder.py'),
                        os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskBuilder.py'))

    for domain in domain_list:
        domain_name = domain[:-3]

        copy_file_and_replace_lines(domain_name,
                                    os.path.join(script_absolute_path,
                                                 'apigenerator', 'resources', '5 - Redoc', 'GenericController', 'DomainRedocController.py'),
                                    os.path.join(result, 'src', 'a_Presentation', 'c_Redoc', 'RedocController.py'))

        copy_file_and_replace_lines(domain_name,
                                    os.path.join(script_absolute_path,
                                                 'apigenerator', 'resources', '5 - Redoc', 'templates', 'domain.html'),
                                    os.path.join(result, 'config', f'{domain_name}.html'))

    add_redoc_blueprint_register_function_to_redoc_controller(os.path.join(result, 'src', 'a_Presentation', 'c_Redoc', 'RedocController.py'))
