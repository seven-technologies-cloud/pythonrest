import os
import shutil
import subprocess
import sys
import time
import ctypes


def remove_pythonrest_from_program_files(install_directory):
    try:
        # Remove the 'PythonREST' folder from Program Files
        shutil.rmtree(install_directory)
        print(f'Successfully removed the PythonREST installation from Program Files.')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST installation folder. {e}')
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
        print('Successfully cleaned up the user PATH settings.')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST from the user PATH. {e}')
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

        # Specify the directory containing the PythonREST executable
        install_directory = os.path.join(os.environ['PROGRAMFILES'], 'PythonREST')

        # Remove the 'PythonREST' folder from Program Files
        remove_pythonrest_from_program_files(install_directory)

        # Pause for a moment before running the PowerShell script
        time.sleep(1)

        # Specify the name of your modified PowerShell script
        powershell_script_name = 'removepythonrestfromuserpath.ps1'

        # Join the script directory and script name to get the full path
        powershell_script_path = os.path.join(script_directory, powershell_script_name)

        # Run the PowerShell script
        run_powershell_script(powershell_script_path)

    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')
        sys.exit(1)

    # Inform the user about the completion
    print('PythonREST uninstallation completed successfully.')
    # Prompt to stop before finalizing
    input('Press Enter to exit...')
