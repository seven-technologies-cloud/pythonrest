import os
import shutil
import sys
import subprocess
import time
import getpass


def move_exe_to_program_files(executable_path, target_folder):
    try:
        shutil.move(executable_path, os.path.join(target_folder, os.path.basename(executable_path)))
        print(f'Successfully added PythonREST to your Programs in "{target_folder}".')
    except Exception as e:
        print(f'Error: Unable to add PythonREST to Programs. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


def run_bash_script(script_path):
    try:
        bash_command = [
            'bash',
            script_path
        ]
        subprocess.run(bash_command, check=True)
        print('PythonREST has been successfully added to your user PATH.')
        print('PythonREST installation completed successfully.')
        print('You can now run "sudo pythonrest version" to verify its installation.')
    except Exception as e:
        print(f'Error: Unable to set PythonREST on user PATH. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


if __name__ == "__main__":
    try:
        if getpass.getuser() != "root":
            print("Please run this script with sudo or as a root user.")
            sys.exit()

        script_directory = os.path.dirname(os.path.abspath(__file__))
        install_directory = '/usr/local/bin'

        os.makedirs(install_directory, exist_ok=True)

        executable_path = os.path.join(script_directory, 'pythonrest')

        move_exe_to_program_files(executable_path, install_directory)

        time.sleep(1)

        bash_script_name = 'addpythonresttouserpath.sh'
        bash_script_path = os.path.join(script_directory, bash_script_name)

        run_bash_script(bash_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    input('Press Enter to exit...')
