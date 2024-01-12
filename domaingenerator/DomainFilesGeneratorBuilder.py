import sys
import os
import json
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
