from apigenerator.b_Workers.StarterWorker import *
from apigenerator.b_Workers.DatabaseFilesWorker import *
from apigenerator.b_Workers.DomainMigrationHandler import *
from apigenerator.b_Workers.ProjectFinalizer import *
from apigenerator.b_Workers.EnvironmentVariablesWorker import *


def generate_python_rest_api(result_full_path, generated_domains_path, us_datetime, db, db_params):
    try:
        proj_domain_folder = os.path.join(result_full_path, 'src\\c_Domain')
        script_absolute_path = define_script_path_based_on_run_context()

        # ------------------------------- Start project ---------------------------------- #

        start_project(result_full_path, generated_domains_path)

        # ---------------------------- Copying Database Files ---------------------------- #

        install_database_files(result_full_path, db, script_absolute_path)

        # ------------------------------------ Domain ------------------------------------ #

        handle_domain_migration_multiple_swagger_files(result_full_path, proj_domain_folder, script_absolute_path)

        modify_swagger_related_files(result_full_path, proj_domain_folder, script_absolute_path)

        # ------------------------------- Project Finalizer ------------------------------- #

        finalize_project(result_full_path, script_absolute_path)

        # ----------------------------- Environment Variables ----------------------------- #

        install_environment_variables(result_full_path, us_datetime, db, db_params, script_absolute_path)
    except Exception as e:
        print(e)
        return
