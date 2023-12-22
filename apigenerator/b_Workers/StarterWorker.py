from apigenerator.b_Workers.DatabaseFilesWorker import *


def start_project(result_full_path, generated_domains_path):
# Copy base project files and generate domain files.
    try:
        print('Preparing to generate API...')

        copy_proj_base_dir(result_full_path)

        copy_domain_files(result_full_path, generated_domains_path)
    except Exception as e:
        raise e
