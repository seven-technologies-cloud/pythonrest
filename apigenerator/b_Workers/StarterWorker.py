from apigenerator.b_Workers.DatabaseFilesWorker import *


def start_project(result_full_path):
# Copy base project files and generate domain files.
    try:
        copy_proj_base_dir(result_full_path)
    except Exception as e:
        raise e
