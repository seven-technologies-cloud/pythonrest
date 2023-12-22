import os
import shutil
import sys
import subprocess
import time
import ctypes


def move_exe_to_program_files(executable_path, target_folder):
    try:
        # Move the executable to the target folder
        shutil.move(executable_path, os.path.join(target_folder, os.path.basename(executable_path)))
        print(f'Successfully added PythonREST to your Programs in "{target_folder}".')
    except Exception as e:
        print(f'Error: Unable to add PythonREST to Programs. {e}')
        input('Press Enter to exit...')
        sys.exit(1)


def run_powershell_script(script_path):
    try:
        # Build the PowerShell command
        powershell_command = [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path
        ]

        # Run the PowerShell script
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
        # Check if the script is running with administrative privileges
        if not ctypes.windll.shell32.IsUserAnAdmin():
            # If not, attempt to run the script with elevated privileges
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

        # Get the directory of the script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Specify the directory containing the PythonRest executable
        install_directory = os.path.join(os.environ['PROGRAMFILES'], 'PythonREST')

        # Ensure the target folder exists
        os.makedirs(install_directory, exist_ok=True)

        # Specify the path to the PythonRest executable
        executable_path = os.path.join(script_directory, 'pythonrest.exe')

        # Move the executable and add the install directory to the system PATH
        move_exe_to_program_files(executable_path, install_directory)

        # Pause for a moment before running the PowerShell script
        time.sleep(1)

        # Specify the name of your modified PowerShell script
        powershell_script_name = 'addpythonresttouserpath.ps1'

        # Join the script directory and script name to get the full path
        powershell_script_path = os.path.join(script_directory, powershell_script_name)

        # Run the PowerShell script
        run_powershell_script(powershell_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    input('Press Enter to exit...')
