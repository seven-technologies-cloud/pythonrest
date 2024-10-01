import json
import os
from shutil import copytree
from apigenerator.g_Utils.OpenFileExeHandler import open


def install_environment_variables(result, us_datetime, db, db_params, script_absolute_path, uid_type, db_secure_connection_params=None):
    # Installs and configures environment variables in environment variables file.
    print('Adding Environment Variables to API')
    copytree(os.path.join(script_absolute_path, 'apigenerator/resources/3 - Variables/EnvironmentVariablesFile'),
             os.path.join(result, 'src', 'e_Infra', 'g_Environment'), dirs_exist_ok=True)

    with open(os.path.join(result, 'src', 'e_Infra', 'g_Environment', 'EnvironmentVariables.py'), 'r') as env_in:
        content = env_in.readlines()
    with open(os.path.join(result, 'src', 'e_Infra', 'g_Environment', 'EnvironmentVariables.py'), 'w') as env_out:
        for line in content:
            if '# Database start configuration #' in line:
                append_line = "os.environ['main_db_conn'] = '{}'\n".format(db)
                line = line + append_line

            if '# Configuration for database connection #' in line:
                append_line = ''
                for key in db_params:
                    append_line = append_line + "os.environ['{}'] = '{}'\n".format(key, db_params[key])
                line = line + append_line

                if db_secure_connection_params:
                    append_line = ''
                    for key in db_secure_connection_params:
                        append_line = append_line + "os.environ['{}'] = '{}'\n".format(key, db_secure_connection_params[key])
                    line = line + append_line

            if '# UID Generation Type #' in line:
                append_line = "os.environ['id_generation_method'] = '{}'\n".format(uid_type)
                line = line + append_line

            env_out.write(line)

    install_datetime_masks(result, us_datetime)


def install_datetime_masks(result, us_datetime):
    if us_datetime:
        with open(os.path.join(result, 'src', 'e_Infra', 'g_Environment', 'EnvironmentVariables.py'), 'r') as env_in:
            env_file_lines = env_in.readlines()
        with open(os.path.join(result, 'src', 'e_Infra', 'g_Environment', 'EnvironmentVariables.py'), 'w') as env_out:
            for line in env_file_lines:
                env_out.write(line.replace("%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y",
                                           "%Y-%m-%d, %m-%d-%Y, %Y/%m/%d, %m/%d/%Y"))
