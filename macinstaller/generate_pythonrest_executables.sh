#!/bin/bash

function write_log() {
    echo "$1"
}

function run_command() {
    write_log "Running command: $1"
    eval "$1"
    if [ $? -ne 0 ]; then
        write_log "Error: Command failed"
        exit 1
    fi
}

if [ "$EUID" -ne 0 ]; then
    write_log "This script needs root privileges. Rerunning with sudo..."
    sudo "$0" "$@"
    exit $?
fi

script_path=$(dirname "$(readlink "$0")")

cd "$script_path" || exit 1

run_command "pyinstaller --onefile --add-data '../pythonrest.py:.' --add-data '../databaseconnector:databaseconnector' --add-data '../domaingenerator:domaingenerator' --add-data '../apigenerator:apigenerator' --collect-submodules typing --collect-submodules re --collect-submodules typer --collect-submodules yaml --collect-submodules parse --collect-submodules mergedeep --collect-submodules site --collect-submodules pymysql --collect-submodules rsa --collect-submodules cryptography --collect-submodules cffi --collect-submodules pycparser --collect-submodules pyasn1 --collect-submodules psycopg2 --collect-submodules psycopg2-binary --collect-submodules pymssql --icon=../pythonrestlogo.icns --windowed ../pythonrest.py"

run_command "mv -f '$script_path/dist/pythonrest' '$script_path'"

chmod +x pythonrest

run_command "pyinstaller --onefile --add-data 'pythonrest:.' --add-data 'install_pythonrest.py:.' --add-data 'addpythonresttouserpath.sh:.' --icon=../pythonrestlogo.icns --windowed --name PythonRESTInstaller install_pythonrest.py"

run_command "pyinstaller --onefile --add-data 'uninstall_pythonrest.py:.' --add-data 'removepythonrestfromuserpath.sh:.' --icon=../pythonrestlogo.icns --windowed --name PythonRESTUninstaller uninstall_pythonrest.py"

executables_dir="$script_path/PythonRestExecutables"
mkdir -p "$executables_dir"
run_command "rm -rf $executables_dir/*"

run_command "mv -f '$script_path/dist/PythonRESTInstaller' '$executables_dir'"
run_command "mv -f '$script_path/dist/PythonRESTUninstaller' '$executables_dir'"

run_command "rm -rf '$script_path/build' '$script_path/dist'"

run_command "rm -f $script_path/*.spec"

run_command "rm -f '$script_path/pythonrest'"

chmod +x "$script_path/$executables_dir/PythonRESTInstaller"
chmod +x "$script_path/$executables_dir/PythonRESTUninstaller"

write_log "PythonRestExecutables successfully generated on path $executables_dir"
