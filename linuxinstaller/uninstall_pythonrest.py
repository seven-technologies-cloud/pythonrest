import os
import subprocess
import sys
import time
import getpass


def remove_pythonrest_from_program_files(install_path):
    try:
        os.remove(install_path)
        print(f'Successfully removed the PythonREST binary: {install_path}')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST binary. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


def run_bash_script(script_path):
    try:
        bash_command = [
            'bash',
            script_path
        ]
        subprocess.run(bash_command, check=True)
        print('Successfully cleaned up the user PATH settings.')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST from the user PATH. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


if __name__ == "__main__":
    try:
        if getpass.getuser() != "root":
            print("Please run this script with sudo or as a root user.")
            sys.exit()

        script_directory = os.path.dirname(os.path.abspath(__file__))
        install_path = '/usr/local/bin/pythonrest'

        remove_pythonrest_from_program_files(install_path)

        time.sleep(1)

        bash_script_name = 'removepythonrestfromuserpath.sh'
        bash_script_path = os.path.join(script_directory, bash_script_name)

        run_bash_script(bash_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    print('PythonREST uninstallation completed successfully.')
    input('Press Enter to exit...')
