from apigenerator.b_Workers.DirectoryManager import *
from apigenerator.f_Builders.SwaggerBuilder import *
from apigenerator.a_Domain.SaMetaClass import *
from apigenerator.b_Workers.MigrationHandler import *
from apigenerator.b_Workers.ModifierHandler import *
from apigenerator.e_Enumerables.Enumerables import *
import os
import re

def check_domain_files(proj_domain_folder):
    domain_files_content = []
    for root, _, files in os.walk(proj_domain_folder):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    domain_files_content.append(f.read())
    return domain_files_content

def replace_money(file_content):
    money_found = False
    money_pattern = re.compile(r'\bsa\.MONEY\b')
    new_content, num_replacements = money_pattern.subn('MONEY', file_content)
    if num_replacements > 0:
        money_found = True
    return new_content, money_found

def add_import_money(file_content):
    import_statement = "from sqlalchemy.dialects.postgresql.types import MONEY\n"
    if "import sqlalchemy as sa" in file_content and import_statement not in file_content:
        parts = file_content.split("import sqlalchemy as sa")
        file_content = parts[0] + "import sqlalchemy as sa\n" + import_statement + parts[1]
    return file_content

def analyze_domain_files(db, proj_domain_folder, result_full_path):
    if db == 'pgsql':
        domain_files_content = check_domain_files(proj_domain_folder)
        for content in domain_files_content:
            new_content, money_found = replace_money(content)
        if money_found:
            with open(result_full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            with open(result_full_path, 'r+', encoding='utf-8') as f:
                existing_content = f.read()
                f.seek(0)
                f.write(add_import_money(existing_content))
                f.truncate()


def handle_domain_migration_multiple_swagger_files(result, proj_domain_folder, script_absolute_path):
# Migrates generated domain python files to correct project folder and extracts data from it to configure Controllers, Services, Validators and Repositories. Finally, it also configures the Swagger files.
    try:
        class_generic_path = os.path.join(script_absolute_path, get_directory_data()['class_generic_path'])

        if not os.path.exists(os.path.join(result, 'config', 'swagger.yaml')):
            shutil.copy(os.path.join(script_absolute_path,
                                     'apigenerator/resources/1 - Project/1 - BaseProject/Project/config/swagger.yaml'),
                        os.path.join(result, 'config', 'swagger.yaml'))

        if not os.path.exists(os.path.join(result, 'app.py')):
            shutil.copy(os.path.join(script_absolute_path,
                                     'apigenerator/resources/1 - Project/1 - BaseProject/Project/app.py'),
                        os.path.join(result, 'app.py'))

        domain_list = get_domain_files_list(proj_domain_folder)

        for domain in domain_list:
            domain_name = domain[:-3]

            print(f"Generating files for: {domain_name}")

            domain_swagger_data = load_swagger_definitions_for_domain_target(result, "PythonREST", domain_name)

            domain_obj = get_sa_meta_class_attributes_object(proj_domain_folder, domain)

            primary_key_list = [attr.row_attr for attr in domain_obj.attr_list if attr.is_primary_key]

            handle_generic_classes_migration(domain_obj.declarative_meta, domain_obj.meta_string, primary_key_list,
                                             result, class_generic_path)

            modify_operation_files(domain_obj.declarative_meta, result)

            if primary_key_list:
                build_swagger_yaml(script_absolute_path, domain_obj, domain_swagger_data, primary_key_list)
            else:
                build_swagger_yaml_no_pk(script_absolute_path, domain_obj, domain_swagger_data, primary_key_list)

            save_each_domain_swagger_yaml(result, domain_swagger_data, domain_name)

            print(f"Swagger file generated for: {domain_name}")

        modify_domain_files_no_pk(result)

        change_main_swagger_title(result, "PythonREST")

    except Exception as e:
        raise e
