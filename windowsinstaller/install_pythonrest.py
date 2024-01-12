import os
import shutil
import sys
import subprocess
import time
import ctypes

def move_pythonrest_exe_to_program_files(executable_path, target_folder):
    try:
        shutil.move(executable_path, os.path.join(target_folder, os.path.basename(executable_path)))
        print(f'Successfully added PythonREST to your Programs in "{target_folder}".')
    except Exception as e:
        print(f'Error: Unable to add PythonREST to Programs. {e}')
        input('Press Enter to exit...')
        sys.exit(1)

def run_script_that_adds_pythonrest_to_path(script_path):
    try:
        powershell_command = [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path
        ]

        subprocess.run(powershell_command, check=True)
        print('PythonREST has been successfully added to your user PATH.')
        print('PythonREST installation completed successfully.')
        print('You can now run "pythonrest version" to verify its installation.')
    except Exception as e:
        print(f'Error: Unable to set PythonREST on user PATH. {e}')
        input('Press Enter to exit...')
        sys.exit(1)

if __name__ == "__main__":
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

        script_directory = os.path.dirname(os.path.abspath(__file__))
        install_directory = os.path.join(os.environ['PROGRAMFILES'], 'PythonREST')
        os.makedirs(install_directory, exist_ok=True)
        executable_path = os.path.join(script_directory, 'pythonrest.exe')
        move_pythonrest_exe_to_program_files(executable_path, install_directory)

        time.sleep(1)
        powershell_script_name = 'addpythonresttouserpath.ps1'
        powershell_script_path = os.path.join(script_directory, powershell_script_name)
        run_script_that_adds_pythonrest_to_path(powershell_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    input('Press Enter to exit...')
