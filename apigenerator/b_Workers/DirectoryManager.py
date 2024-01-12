# System Imports #
import sys
import os
import shutil
from apigenerator.e_Enumerables.Enumerables import *
import site


# Check if script is running directly or via exe file to get the path
def define_script_path_based_on_run_context():
    # Get the absolute path of the current script
    script_path = os.path.abspath(sys.argv[0])

    # Check if the script is running as an executable
    if getattr(sys, 'frozen', False):
        # If it's an executable, use the '_MEIPASS' attribute
        script_absolute_path = getattr(sys, '_MEIPASS', os.path.dirname(script_path))
    else:
        # If it's a script, check if it's installed via pip or running from source
        if is_pip_installed('pythonrest'):
            # If installed via pip or in a virtual environment, use the package directory
            script_absolute_path = os.environ['PACKAGE_DIR']
        else:
            # If running from source, use the directory of the script
            script_absolute_path = os.path.dirname(script_path)
    return script_absolute_path


def is_pip_installed(package_name):
    site_packages = site.getsitepackages()

    for path in site_packages:
        package_path = os.path.join(path, package_name)
        if os.path.exists(package_path):
            return True

    return False


# Method removes all files under a certain directory #
def clean_directory(directory, ignore_files=None):
    ignore_files = set(ignore_files) if ignore_files else set()

    files_to_process = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename not in ignore_files]

    for file_path in files_to_process:
        # Removing files #
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


# Copy base 'Project' directory to result hierarchy #
def copy_proj_base_dir(result_full_path, symlinks=False, ignore=None):
    directories = get_directory_data()
    script_absolute_path = define_script_path_based_on_run_context()
    src = os.path.join(script_absolute_path, directories['base_proj_path'])
    # Iterating over working tree #
    for item in os.listdir(src):
        src_folder = os.path.join(src, item)
        dst_folder = os.path.join(result_full_path, item)
        if os.path.isdir(src_folder):
            shutil.copytree(src_folder, dst_folder, symlinks, ignore)
        else:
            shutil.copy2(src_folder, dst_folder)


# Method copies domain files into proper folder of result hierarchy #
def copy_domain_files(proj_domain_folder, generated_domains_path, symlinks=False, ignore=None):
    # Iterating over domain directory #
    for item in os.listdir(generated_domains_path):
        src_folder = os.path.join(generated_domains_path, item)
        dst_folder = os.path.join(proj_domain_folder, item)
        # Copying files #
        if os.path.isdir(src_folder):
            shutil.copytree(src_folder, dst_folder, symlinks, ignore)
        else:
            shutil.copy2(src_folder, dst_folder)

    shutil.rmtree(generated_domains_path)


# Method copies database connection files into proper folder of result hierarchy #
def copy_database_files(db_resources_folder, resources_folder, symlinks=False, ignore=None):
    # Iterating over proper directory #
    for item in os.listdir(db_resources_folder):
        s = os.path.join(db_resources_folder, item)
        d = os.path.join(resources_folder, item)
        # Asssembling files into destination folder #
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


def mergefolders(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)


def get_list_of_directories_in_directory(path):
    return os.listdir(path)


def get_domain_files_list(domain_path):
    domain_files_list = [f for f in os.listdir(domain_path)
                         if os.path.isfile(os.path.join(domain_path, f)) and f != '__init__.py']
    return domain_files_list


def append_database_library_to_requirements_file(file_path, new_dependency):
    try:
        # Read the content of the existing requirements.txt file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Check if the last line is not empty and does not end with a newline
        if lines and lines[-1].strip() != '':
            # Add a newline if the last line is not empty
            lines.append('\n')

        # Append the new dependency to the list
        lines.append(new_dependency + '\n')

        # Write the updated content back to the requirements.txt file
        with open(file_path, 'w') as file:
            file.writelines(lines)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")


# Check if base project folders exists and cleans those folders to regenerate their files
def check_if_base_project_exists(result_full_path):
    # List of directories and files to check relative to the base_path
    base_project_directories_and_files = [
        'src/c_Domain',
        'src/a_Presentation/a_Domain',
        'src/b_Application/b_Service/a_Domain',
        'src/d_Repository/a_Domain',
        'src/a_Presentation/d_Swagger',
        'src/e_Infra/b_Builders/a_Swagger',
        'src/e_Infra/d_Validators/a_Domain',
        'src/e_Infra/g_Environment',
        'src/e_Infra/b_Builders/FlaskBuilder.py',
        'config',
        'app.py'
    ]

    # Check if all directories and files exist
    base_project_exists = all(os.path.exists(os.path.join(result_full_path, item)) for item in base_project_directories_and_files)

    if base_project_exists:
        # Clean all directories and delete files
        for item in base_project_directories_and_files:
            full_path = os.path.join(result_full_path, item)

            if os.path.isdir(full_path):
                # If it's a directory, clean it
                clean_directory(full_path, ignore_files=['__init__.py'])
            elif os.path.isfile(full_path):
                # If it's a file, delete it
                os.remove(full_path)

    return base_project_exists
