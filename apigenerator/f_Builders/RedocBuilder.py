# System Imports #
import os
import shutil

from apigenerator.b_Workers.DirectoryManager import get_domain_files_list
from apigenerator.g_Utils.StringAndFileHandler import copy_file_and_replace_lines


def add_redoc_blueprint_function_calls_to_flaskbuilder(result, domain_name):
    with open(os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskBuilder.py'), 'r') \
            as py_file_in:
        content = py_file_in.readlines()
    with open(os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'FlaskBuilder.py'), 'w') \
            as py_file_out:
        for line in content:
            if line == '# Building Redoc Blueprint #\n':
                line = line \
                       + f'build_{domain_name.lower()}_redoc_blueprint(app_handler, redoc_blueprint)\n'
            py_file_out.write(line)


def modify_redoc_related_files(result, domain_path, script_absolute_path):
    print('Creating RedocBuilder functions')
    domain_list = get_domain_files_list(domain_path)

    if not os.path.exists(os.path.join(result, 'src', 'a_Presentation', 'c_Redoc' 'RedocController.py')):
        shutil.copytree(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/src/a_Presentation/c_Redoc'),
                        os.path.join(result, 'src', 'a_Presentation', 'c_Redoc'), dirs_exist_ok=True)

    if not os.path.exists(os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'b_Redoc', 'RedocBuilder.py')):
        shutil.copytree(os.path.join(script_absolute_path, 'apigenerator/resources/1 - Project/1 - BaseProject/Project/src/e_Infra/b_Builders/b_Redoc'),
                        os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'b_Redoc'), dirs_exist_ok=True)

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
                                                 'apigenerator', 'resources', '5 - Redoc', 'GenericBuilder', 'DomainRedocBuilder.py'),
                                    os.path.join(result, 'src', 'e_Infra', 'b_Builders', 'b_Redoc', 'RedocBuilder.py'))

        copy_file_and_replace_lines(domain_name,
                                    os.path.join(script_absolute_path,
                                                 'apigenerator', 'resources', '5 - Redoc', 'templates', 'domain.html'),
                                    os.path.join(result, 'config', f'{domain_name}.html'))

        add_redoc_blueprint_function_calls_to_flaskbuilder(result, domain_name)
