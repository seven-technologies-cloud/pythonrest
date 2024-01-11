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

script_path=$(dirname "$(readlink -f "$0")")

cd "$script_path" || exit 1

run_command "pyinstaller --onefile --add-data '../pythonrest.py:.' --add-data '../databaseconnector:databaseconnector' --add-data '../domaingenerator:domaingenerator' --add-data '../apigenerator:apigenerator' --collect-submodules typing --collect-submodules re --collect-submodules typer --collect-submodules yaml --collect-submodules parse --collect-submodules mergedeep --collect-submodules pymysql --collect-submodules psycopg2 --collect-submodules psycopg2-binary --collect-submodules pymssql ../pythonrest.py"

run_command "mv '$script_path/dist/pythonrest' '$script_path' -f"

run_command "pyinstaller --onefile --add-data 'pythonrest:.' --add-data 'install_pythonrest.py:.' --add-data 'addpythonresttouserpath.sh:.' --name PythonRESTInstaller install_pythonrest.py"

run_command "pyinstaller --onefile --add-data 'uninstall_pythonrest.py:.' --add-data 'removepythonrestfromuserpath.sh:.' --name PythonRESTUninstaller uninstall_pythonrest.py"

executables_dir="$script_path/PythonRestExecutables"
mkdir -p "$executables_dir"
run_command "rm -rf $executables_dir/*"

run_command "mv '$script_path/dist/PythonRESTInstaller' '$executables_dir' -f"
run_command "mv '$script_path/dist/PythonRESTUninstaller' '$executables_dir' -f"

run_command "rm -rf '$script_path/build' '$script_path/dist'"

run_command "rm -f $script_path/*.spec"

run_command "rm -f '$script_path/pythonrest'"

chmod +x "$executables_dir/PythonRESTInstaller"
chmod +x "$executables_dir/PythonRESTUninstaller"

write_log "PythonRestExecutables successfully generated on path $executables_dir"
