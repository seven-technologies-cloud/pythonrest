import os
import shutil
import subprocess
import sys
import time
import ctypes


def remove_pythonrest_from_program_files(install_directory):
    try:
        shutil.rmtree(install_directory)
        print(f'Successfully removed the PythonREST installation from Program Files.')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST installation folder. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


def run_script_that_removes_pythonrest_from_path(script_path):
    try:
        powershell_command = [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path
        ]
        subprocess.run(powershell_command, check=True)
        print('Successfully cleaned up the user PATH settings.')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST from the user PATH. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


if __name__ == "__main__":
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

        script_directory = os.path.dirname(os.path.abspath(__file__))
        install_directory = os.path.join(os.environ['PROGRAMFILES'], 'PythonREST')

        remove_pythonrest_from_program_files(install_directory)

        time.sleep(1)

        powershell_script_name = 'removepythonrestfromuserpath.ps1'
        powershell_script_path = os.path.join(script_directory, powershell_script_name)

        run_script_that_removes_pythonrest_from_path(powershell_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    print('PythonREST uninstallation completed successfully.')
    input('Press Enter to exit...')
