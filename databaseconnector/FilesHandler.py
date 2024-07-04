import os
import re
import shutil


def get_domain_result_files(domain_result_folder):
    domain_result_json_files = os.listdir(domain_result_folder)
    return domain_result_json_files


def normalize_path(path):
    # Replace forward slashes and double forward slashes with double backslashes
    path = re.sub(r'[/]+', r'\\', path)
    path = re.sub(r'//', r'\\', path)

    # Replace multiple consecutive backslashes with a single backslash
    path = re.sub(r'\\+', r'\\', path)

    # Ensure there are always two backslashes separating each folder
    path = re.sub(r'\\(?!\\)', r'\\', path)

    # Remove trailing backslashes or slashes at the end of the string
    if path != '\\':
        path = re.sub(r'[\\/]+$', '', path)

    return path


def check_if_given_result_path_is_unsafe(path):
    path = normalize_path(path)

    sensitive_startswith_paths = [
        # Linux sensitive paths
        "\\bin", "\\boot",  "\\dev", "\\etc", "\\init", "\\lib", "\\lib32", "\\lib64", "\\libx32", "\\opt",
        "\\proc", "root", "run", "\\sbin", "snap", "\\srv", "\\sys", "tmp", "usr", "\\usr\\bin", "\\usr\\sbin"

        # Mac sensitive paths
        "\\System", "\\Library", "\\Applications", "\\Volumes", "\\bin", "\\tmp", "\\cores", "\\opt", 
        "\\private\\var", "\\etc", "\\sbin", "\\dev", "\\private", "\\var", "\\usr",

        # Windows sensitive paths
        "C:\\ProgramData", "C:\\WINDOWS", "C:\\WINDOWS\\system32", "C:\\WINDOWS\\SysWOW64", "C:\\Program Files", "C:\\Program Files (x86)"
    ]


    # List of sensitive paths for different systems
    sensitive_paths = [
        # Linux sensitive paths
        "\\", "\\bin", "\\boot", "\\dev", "\\etc", "\\home", "\\init", "\\lib", "\\lib32", "\\lib64", "\\libx32",
        "\\media", "\\mnt", "\\opt", "\\proc", "root", "run", "\\sbin", "snap", "\\srv", "\\sys", "tmp", "usr",
        "\\usr\\bin", "\\usr\\sbin"

        # Mac sensitive paths
        "\\", "\\System", "\\Library", "\\Applications", "\\Volumes", "\\bin", "\\home", "\\tmp", "\\cores", "\\opt", 
        "\\private\\var", "\\Users", "\\etc", "\\sbin", "\\dev", "\\private", "\\var", "\\usr",

        # Windows sensitive paths
        "C:", "C:\\ProgramData", "C:\\WINDOWS", "C:\\WINDOWS\\system32", "C:\\WINDOWS\\SysWOW64", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Users"
    ]				

    path = path.lower()

    # Check if the path is unsafe for creation
    for sensitive_path in sensitive_startswith_paths:
        sensitive_path = sensitive_path.lower()
        if os.name == "nt" and os.path.splitdrive(os.path.abspath(path))[0].lower() == os.path.splitdrive(sensitive_path)[0].lower():
            if path.startswith(sensitive_path) or path == sensitive_path:
                return True
        elif os.name != "nt":
            if path.startswith(sensitive_path) or path == sensitive_path:
                return True

    # Check if the path is unsafe for creation
    for sensitive_path in sensitive_paths:
        sensitive_path = sensitive_path.lower()
        if os.name == "nt" and os.path.splitdrive(os.path.abspath(path))[0].lower() == os.path.splitdrive(sensitive_path)[0].lower():
            if path.endswith(sensitive_path) or path == sensitive_path:
                return True
        elif os.name != "nt":
            if path.endswith(sensitive_path) or path == sensitive_path:
                return True


def check_if_current_working_directory_is_unsafe(path):
    path = normalize_path(path)

    sensitive_startswith_paths = [
        # Linux sensitive paths
        "\\bin", "\\boot", "\\dev", "\\etc", "\\init", "\\lib", "\\lib32", "\\lib64", "\\libx32", "\\opt",
        "\\proc", "root", "run", "\\sbin", "snap", "\\srv", "\\sys", "tmp", "usr", "\\usr\\bin", "\\usr\\sbin"

        # Mac sensitive paths
        "\\System", "\\Library", "\\Applications", "\\Volumes", "\\bin", "\\tmp", "\\cores", "\\opt", 
        "\\private\\var", "\\etc", "\\sbin", "\\dev", "\\private", "\\var", "\\usr",

        # Windows sensitive paths
        "C:\\ProgramData", "C:\\WINDOWS", "C:\\WINDOWS\\system32", "C:\\WINDOWS\\SysWOW64", "C:\\Program Files", "C:\\Program Files (x86)"
    ]

    # List of sensitive paths for different systems
    sensitive_paths = [
        # Linux sensitive paths
        "\\", "\\bin", "\\boot", "\\dev", "\\etc", "\\home", "\\init", "\\lib", "\\lib32", "\\lib64", "\\libx32",
        "\\media", "\\mnt", "\\opt", "\\proc", "root", "run", "\\sbin", "snap", "\\srv", "\\sys", "tmp", "usr",
        "\\usr\\bin", "\\usr\\sbin"

        # Mac sensitive paths
        "\\", "\\System", "\\Library", "\\Applications", "\\Volumes", "\\bin", "\\home", "\\tmp", "\\cores", "\\opt", 
        "\\private\\var", "\\Users", "\\etc", "\\sbin", "\\dev", "\\private", "\\var", "\\usr",

        # Windows sensitive paths
        "C:", "C:\\ProgramData", "C:\\WINDOWS", "C:\\WINDOWS\\system32", "C:\\WINDOWS\\SysWOW64", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Users"
    ]

    path = path.lower()

    # Check if the path is unsafe for creation
    for sensitive_path in sensitive_startswith_paths:
        sensitive_path = sensitive_path.lower()
        if os.name == "nt" and os.path.splitdrive(os.path.abspath(path))[0].lower() == os.path.splitdrive(sensitive_path)[0].lower():
            if path.startswith(sensitive_path) or path == sensitive_path:
                return True
        elif os.name != "nt":
            if path.startswith(sensitive_path) or path == sensitive_path:
                return True

    # Check if the path is unsafe for creation
    for sensitive_path in sensitive_paths:
        sensitive_path = sensitive_path.lower()
        if os.name == "nt" and os.path.splitdrive(os.path.abspath(path))[0].lower() == os.path.splitdrive(sensitive_path)[0].lower():
            if path.endswith(sensitive_path) or path == sensitive_path:
                return True
        elif os.name != "nt":
            if path.endswith(sensitive_path) or path == sensitive_path:
                return True


def check_if_provided_directory_is_unsafe(path):
    path = normalize_path(path)
    # List of sensitive paths for different systems
    sensitive_paths = [
        # Linux sensitive paths
        "\\", "\\bin", "\\boot", "\\dev", "\\etc", "\\home", "\\init", "\\lib", "\\lib32", "\\lib64", "\\libx32", "\\media",
        "\\mnt", "\\opt", "\\proc", "root", "run", "\\sbin", "snap", "\\srv", "\\sys", "tmp", "usr", "\\usr\\bin", "\\usr\\sbin"

        # Mac sensitive paths
        "\\System", "\\Library", "\\Applications", "\\Volumes", "\\bin", "\\home", "\\tmp", "\\cores", "\\opt", 
        "\\private\\var", "\\etc", "\\sbin", "\\dev", "\\private", "\\var", "\\Users", "\\usr",

        # Windows sensitive paths
        "C:", "C:\\Windows", "C:\\WINDOWS\\system32", "C:\\WINDOWS\\SysWOW64", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Users"
    ]

    path = path.lower()

    # Check if the path is unsafe for creation
    for sensitive_path in sensitive_paths:
        sensitive_path = sensitive_path.lower()
        if os.name == "nt" and os.path.splitdrive(os.path.abspath(path))[0].lower() == os.path.splitdrive(sensitive_path)[0].lower():
            if path.endswith(sensitive_path) or path == sensitive_path:
                return True
        elif os.name != "nt":
            if path.endswith(sensitive_path) or path == sensitive_path:
                return True

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