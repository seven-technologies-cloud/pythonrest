import shutil
import yaml
from mergedeep import merge
import os


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def install_sql_route(result, script_absolute_path):
    copytree(os.path.join(script_absolute_path, 'apigenerator/resources/4 - SQLRoute'),
             os.path.join(result, 'src\\a_Presentation\\b_Custom'))


def install_sql_swagger(result, script_absolute_path):
    with open(os.path.join(result, 'config\\swagger.yaml'), 'r') as yaml_in:
        swagger_dict = yaml.safe_load(yaml_in)
    with open(os.path.join(script_absolute_path, 'apigenerator/resources/2 - Swagger/yaml/sql.yaml'), 'r') as sql_in:
        sql_dict = yaml.safe_load(sql_in)

    swagger_dict['tags'] = swagger_dict['tags'] + sql_dict['tags']

    merge(swagger_dict['paths'], sql_dict['paths'])

    with open(os.path.join(result, 'config\\swagger.yaml'), 'w') as yaml_out:
        yaml.dump(swagger_dict, yaml_out, sort_keys=False)


def finalize_project(result, script_absolute_path):
    install_sql_route(result, script_absolute_path)
    install_sql_swagger(result, script_absolute_path)
