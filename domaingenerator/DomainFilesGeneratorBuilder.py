import sys
import os
import json
import importlib.metadata


# Check if script is running directly or via exe file to get the path
def define_script_path_based_on_run_context():
    # Get the absolute path of the current script
    script_path = os.path.abspath(sys.argv[0])
    script_absolute_path = ""

    # Check if the script is running as an executable
    if getattr(sys, 'frozen', False):
        # If it's an executable, use the '_MEIPASS' attribute
        script_absolute_path = getattr(sys, '_MEIPASS', os.path.dirname(script_path))
    else:
        # If it's a script, check if it's installed via pip or running from source
        if is_pip_installed('pythonrest3'):  # If installed via pip or in a virtual environment, use the PACKAGE_DIR
            # variable defined on project __init__.py file.
            # If unable to get the PACKAGE_DIR variable(running from source code) get the default script path
            script_absolute_path = os.getenv('PACKAGE_DIR',  os.path.dirname(script_path))
    return script_absolute_path


def is_pip_installed(package_name):
    try:
        importlib.metadata.version(package_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def get_domain_list(json_metadata_path):
    domain_list = os.listdir(json_metadata_path)
    domain_list = [domain for domain in domain_list if domain != "placeholder.json"]
    return domain_list


def get_domain_dict(json_metadata_path):
    with open(json_metadata_path, 'r') as json_in:
        return json.load(json_in)


def build_domain_file(domain_mask_file_path, replacer, generated_domains_path):
    with open(domain_mask_file_path, 'r') as file_in:
        mask_data = file_in.readlines()

    with open(os.path.join(generated_domains_path, replacer.declarative_meta + '.py'), 'w') as domain_out:
        for line in mask_data:
            domain_out.write(line
            .replace('${domain_imports}', replacer.domain_imports)
            .replace('${declarative_meta}', replacer.declarative_meta)
            .replace('${meta_string}', replacer.meta_string)
            .replace('${columns_names}', replacer.columns_names)
            .replace('${sa_columns}', replacer.sa_columns)
            .replace('${columns_init}', replacer.columns_init)
            .replace('${self_columns}', replacer.self_columns))
