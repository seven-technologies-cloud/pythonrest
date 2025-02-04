from apigenerator.b_Workers.StarterWorker import *
from apigenerator.b_Workers.DatabaseFilesWorker import *
from apigenerator.b_Workers.DomainMigrationHandler import *
from apigenerator.b_Workers.ProjectFinalizer import *
from apigenerator.b_Workers.EnvironmentVariablesWorker import *
from apigenerator.b_Workers.DirectoryManager import copy_domain_files
from apigenerator.f_Builders.FlaskAdminBuilder import build_flask_admin_files
from apigenerator.f_Builders.RedocBuilder import modify_redoc_related_files


def generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, db, db_params, base_project_exists,
                             project_name, uid_type, db_secure_connection_params=None, db_authentication_method=None):
    try:
        print('Preparing to generate API...')
        proj_domain_folder = os.path.join(result_full_path, 'src', 'c_Domain')
        script_absolute_path = define_script_path_based_on_run_context()

        # ------------------------------- Start project ---------------------------------- #
        if not base_project_exists:
            start_project(result_full_path)
        copy_domain_files(proj_domain_folder, generated_domains_path)

        # ---------------------------- Copying Database Files ---------------------------- #
        if not base_project_exists:
            if db_authentication_method:
                install_database_files(result_full_path, db, script_absolute_path, db_authentication_method)
            else:
                install_database_files(result_full_path, db, script_absolute_path)

        # ------------------------------------ Domain ------------------------------------ #

        handle_domain_migration_multiple_swagger_files(result_full_path, proj_domain_folder, script_absolute_path,
                                                       project_name)

        modify_swagger_related_files(
            result_full_path, proj_domain_folder, script_absolute_path)

        modify_exceptional_types_in_domain_files(db, proj_domain_folder, result_full_path)

        # ------------------------------- Project Finalizer ------------------------------- #
        if not base_project_exists:
            finalize_project(result_full_path, script_absolute_path)
        print('Adding SQL swagger')
        install_sql_swagger(result_full_path, script_absolute_path)

        # ----------------------------- Environment Variables ----------------------------- #

        if db_secure_connection_params:
            install_environment_variables(
                result_full_path, us_datetime, db, db_params, script_absolute_path, uid_type, db_secure_connection_params)
        else:
            install_environment_variables(
                result_full_path, us_datetime, db, db_params, script_absolute_path, uid_type)

        # ---------------------------------- Flask-Admin ---------------------------------- #
        build_flask_admin_files(result_full_path, proj_domain_folder, script_absolute_path, db)

        # ------------------------------------ Redoc -------------------------------------- #
        modify_redoc_related_files(
            result_full_path, proj_domain_folder, script_absolute_path)
    except Exception as e:
        print(e)
        return
