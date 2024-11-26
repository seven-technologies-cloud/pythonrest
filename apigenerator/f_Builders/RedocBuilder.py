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


def change_redoc_html_files_title(redoc_files_path, project_name):
    for filename in os.listdir(redoc_files_path):
        if filename.endswith('.html'):
            file_path = os.path.join(redoc_files_path, filename)

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            new_content = content.replace('PythonREST', project_name)

            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)


def modify_redoc_related_files(result, domain_path, script_absolute_path, project_name):
    print('Creating Redoc docs for API')
    domain_list = get_domain_files_list(domain_path)

    if not os.path.exists(os.path.join(result, 'src', 'a_Presentation', 'f_Redoc' 'RedocController.py')):
        shutil.copytree(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/src/a_Presentation/f_Redoc'),
                        os.path.join(result, 'src', 'a_Presentation', 'f_Redoc'), dirs_exist_ok=True)

    if not os.path.exists(os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskBuilder.py')):
        shutil.copy(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/src/e_Infra/b_Builders/FlaskBuilder.py'),
                        os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskBuilder.py'))

    if not os.path.exists(os.path.join(result, 'config', 'redoc.html')):
        shutil.copy(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/config/redoc.html'),
                        os.path.join(result, 'config', 'redoc.html'))

    for domain in domain_list:
        domain_name = domain[:-3]

        copy_file_and_replace_lines(domain_name,
                                    os.path.join(script_absolute_path,
                                                 'apigenerator', 'resources', '5 - Redoc', 'GenericController', 'DomainRedocController.py'),
                                    os.path.join(result, 'src', 'a_Presentation', 'f_Redoc', 'RedocController.py'))

    add_redoc_blueprint_register_function_to_redoc_controller(os.path.join(result, 'src', 'a_Presentation', 'f_Redoc', 'RedocController.py'))
    change_redoc_html_files_title(os.path.join(result, 'config'), project_name)