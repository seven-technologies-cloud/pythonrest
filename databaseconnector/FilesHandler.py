import os
import shutil


def get_domain_result_files(domain_result_folder):
    domain_result_json_files = os.listdir(domain_result_folder)
    return domain_result_json_files


# Function to delete all files of a directory #
def clean_directory(directory):
    # Iterating over working tree #
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Removing files #
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))