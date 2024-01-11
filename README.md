# PythonREST CLI

## Requirements

Already listed within ./requirements.txt

- 'typer==0.9.0',
- 'PyYAML==6.0.1'
- 'parse==1.20.0'
- 'mergedeep==1.3.4'
- 'pymysql==1.1.0'
- 'psycopg2==2.9.9'
- 'psycopg2-binary==2.9.9'
- 'pymssql==2.2.10'
- 'pyinstaller==6.3.0'

To run and build this project, you need to have the above libraries installed on your machine, which you can do running 
the below command on the project root directory:
# Windows
```commandline
pip install -r requirements.txt
```

# Linux
```bash
sudo pip install -r requirements.txt
```

## Structure

PrivatePythonRest/
├── pythonrest/
│   ├── __init__.py
│   ├── pythonrest.py
│   ├── connect_functions.py
│   └── test.py
├── setup.py
└── README.md

## Run our pythonrest CLI

There are five available commands for now:

Check the version:
`pythonrest version`

Connect to mysql:
`pythonrest generate --mysql-connection-string <mysql_connection_string>`

Connect to postgres:
`pythonrest generate --postgres-connection-string <postgres_connection_string>`

Connect to sqlserver:
`pythonrest generate --sqlserver-connection-string <sqlserver_connection_string>`

Connect to mariadb:
`pythonrest generate --mariadb-connection-string <mariadb_connection_string>`

# How to Build

# Windows

## Building the CLI exe
Run from the root folder:
```commandline
pyinstaller --onefile ^
    --add-data "pythonrest.py;." ^
    --add-data "databaseconnector;databaseconnector" ^
    --add-data 'domaingenerator;domaingenerator' ^
    --add-data 'apigenerator;apigenerator' ^
    --collect-submodules typing ^
    --collect-submodules re ^
    --collect-submodules typer ^
    --collect-submodules yaml ^
    --collect-submodules parse ^
    --collect-submodules mergedeep ^
    --collect-submodules pymysql ^
    --collect-submodules psycopg2 ^
    --collect-submodules psycopg2-binary ^
    --collect-submodules pymssql ^
    --icon=pythonrestlogo.ico ^
    pythonrest.py
```
it will generate a dist folder with the pythonrest.exe file 

Known Issues:
When using pyinstaller with typing installed it generates the following error:
```commandline
The 'typing' package is an obsolete backport of a standard library package and is incompatible with PyInstaller. Please remove this package
```
Just removing the package and retrying fixes that error.

## Building the Installer exe
Move the pythonrest.exe file from the generated dist/ folder to the windowsinstaller/ folder and run from the latter folder:
```commandline
pyinstaller ^
--onefile ^
--add-data "pythonrest.exe;." ^
--add-data "install_pythonrest.py;." ^
--add-data "addpythonresttouserpath.ps1;." ^
--icon=../pythonrestlogo.ico ^
--name PythonRESTInstaller install_pythonrest.py
```

## Building the Uninstaller exe
Run from the windowsinstaller folder:
```commandline
pyinstaller ^
--onefile ^
--add-data "uninstall_pythonrest.py;." ^
--add-data "removepythonrestfromuserpath.ps1;." ^
--icon=../pythonrestlogo.ico ^
--name PythonRESTUninstaller uninstall_pythonrest.py
```

## Build exe, installer and uninstaller
run from windowsinstaller/ folder:
```powershell
.\generate_pythonrest_executables.ps1
```
This will take care of running the above pyinstaller commands and it will generate both installer and uninstaller 
executables on PythonRestExecutables/ directory, which you can then run to install and/or uninstall the cli on your
machine.

# Linux
## Building the CLI binary
Run from the root folder:
```bash
pyinstaller --onefile \
    --add-data "pythonrest.py:." \
    --add-data "databaseconnector:databaseconnector" \
    --add-data 'domaingenerator:domaingenerator' \
    --add-data 'apigenerator:apigenerator' \
    --collect-submodules typing \
    --collect-submodules re \
    --collect-submodules typer \
    --collect-submodules yaml \
    --collect-submodules parse \
    --collect-submodules mergedeep \
    --collect-submodules pymysql \
    --collect-submodules psycopg2 \
    --collect-submodules psycopg2-binary \
    --collect-submodules pymssql \
    pythonrest.py
```
it will generate a dist folder with the pythonrest file 

Known Issues:
When using pyinstaller with typing installed it generates the following error:
```commandline
The 'typing' package is an obsolete backport of a standard library package and is incompatible with PyInstaller. Please remove this package
```
Just removing the package and retrying fixes that error.

## Building the Installer binary
Move the pythonrest.exe file from the generated dist/ folder to the linuxinstaller/ folder and run from the latter folder:
```bash
pyinstaller \
    --onefile \
    --add-data "pythonrest:." \
    --add-data "install_pythonrest.py:." \
    --add-data "addpythonresttouserpath.sh:." \
    --name PythonRESTInstaller install_pythonrest.py
```

## Building the Uninstaller binary
Run from the linuxinstaller/ folder:
```bash
pyinstaller \
    --onefile \
    --add-data "uninstall_pythonrest.py:." \
    --add-data "removepythonrestfromuserpath.sh:." \
    --name PythonRESTUninstaller uninstall_pythonrest.py
```

## Build pythonrest, installer and uninstaller
run from linuxinstaller/ folder:
```bash
./generate_pythonrest_executables.sh
```
This will take care of running the above pyinstaller commands, and it will generate both installer and uninstaller 
binaries on PythonRestExecutables/ directory, which you can then run to install and/or uninstall the cli on your
machine, like below:
```bash
./PythonRESTInstaller
./PythonRESTUninstaller
```
