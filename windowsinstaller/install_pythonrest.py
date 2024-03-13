import os
import shutil
import sys
import subprocess
import time

def move_exe_to_user_program_files(executable_path):
    target_folder = os.path.join(os.environ['LOCALAPPDATA'], 'PythonREST')
    os.makedirs(target_folder, exist_ok=True)
    try:
        shutil.move(executable_path, os.path.join(target_folder, os.path.basename(executable_path)))
        print(f'Successfully added PythonREST to your local app data in "{target_folder}".')
    except Exception as e:
        print(f'Error: Unable to add PythonREST to local app data. {e}')
        input('Press Enter to exit...')
        sys.exit(1)
    return target_folder

def run_powershell_script(script_path):
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
        script_directory = os.path.dirname(os.path.abspath(__file__))
        executable_path = os.path.join(script_directory, 'pythonrest.exe')
        install_directory = move_exe_to_user_program_files(executable_path)

        time.sleep(1)
        powershell_script_name = 'addpythonresttouserpath.ps1'
        powershell_script_path = os.path.join(script_directory, powershell_script_name)
        # Modify the PowerShell script path if necessary
        run_powershell_script(powershell_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    input('Press Enter to exit...')
