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

## Usage

To make use of pythonrest, these are the commands available for use:

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

### Custom options
#### --result-path:
By default, PythonREST will generate the API on your current directory, under a PythonRestAPI folder, but there is also 
a possibility to define a custom path to your generated API, following the below example:

`pythonrest generate --mysql-connection-string <mysql_connection_string> --result-path C:\Users\<your_user_here>\Documents\PythonRestCustomFolder`

The above will generate your API on the provided path, and if the folder does not exist the generator will create it, keep
in mind that the provided folder will be cleaned before generating the API.

#### --use-pascal-case:
This option creates the Python Domain Classes with PascalCase pattern for their names, if this option is provided as
--no-use-pascal-case, you will be prompted to provide a name of python class for each table of your database:

`pythonrest generate --mysql-connection-string <mysql_connection_string> --no-use-pascal-case`

#### --us-datetime:
If you have a database with datetime formatted to the us pattern of mm-dd-yyyy, you can use this option so that the api
will also respect that pattern when validating requests and responses:

`pythonrest generate --mysql-connection-string <mysql_connection_string> --us-datetime`

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
    --collect-submodules site ^
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

# Linux/Mac
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
    --collect-submodules site \
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
Move the pythonrest file from the generated dist/ folder to the linuxinstaller/ or macinstaller/ folder and run from it:
```bash
pyinstaller \
    --onefile \
    --add-data "pythonrest:." \
    --add-data "install_pythonrest.py:." \
    --add-data "addpythonresttouserpath.sh:." \
    --name PythonRESTInstaller install_pythonrest.py
```

## Building the Uninstaller binary
Run from the linuxinstaller/ or macinstaller/ folder:
```bash
pyinstaller \
    --onefile \
    --add-data "uninstall_pythonrest.py:." \
    --add-data "removepythonrestfromuserpath.sh:." \
    --name PythonRESTUninstaller uninstall_pythonrest.py
```

## Build pythonrest, installer and uninstaller
Go to linuxinstaller/ or macinstaller/ folder and from it add execute permission on the script:
```bash
chmod +x ./generate_pythonrest_executables.sh
```

Execute the script:
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
Known Issues:
When executing ./generate_pythonrest_executables.sh, there is a possibility that something like this issue occurs:
```bash
./generate_pythonrest_executables.sh: line 2: $'\r': command not found                                                   
./generate_pythonrest_executables.sh: line 3: syntax error near unexpected token `$'{\r''                                
'/generate_pythonrest_executables.sh: line 3: `function write_log() {   
```
That issue is due to a difference in line endings between Windows (CRLF - Carriage Return and Line Feed) and Linux/Unix
(LF - Line Feed) systems. When you transfer or use scripts created on Windows in a Linux environment, these line ending 
characters can cause issues. To fix it you can install and run dos2unix in all of the sh files of the linuxinstaller
folder:
```bash
sudo apt-get update
sudo apt-get install dos2unix
dos2unix generate_pythonrest_executables.sh
dos2unix addpythonresttouserpath.sh
dos2unix removepythonrestfromuserpath.sh
```

## Build and install pythonrest local pip package
Run from the root folder:
```commandline
pip install .
```
This will use the setup.py from the root folder to build a library of the pythonrest on the site-packages
of the Python folder.
One thing worth noting is that if you need to add a new folder to the project, e.g. apigenerator/c_NewFolder
you need to add a new entry to the list of the packages property in the setup.py, like this:
```python
'pythonrest.apigenerator.c_NewFolder',
```
And if that folder has files that are not of .py extension, e.g. apigenerator/c_NewFolder/new.yaml and 
apigenerator/c_NewFolder/new2.yaml, you need to add a new entry to the list of the package_data property in the 
setup.py, like this:
```python
'pythonrest.apigenerator.c_NewFolder': ['new.yaml', 'new2.yaml'],
```
All of this must be done to successfully add those files to the pip generated and installed library
To uninstall the local pip package, you can just use a common pip uninstall command:
```commandline
pip uninstall pythonrest
```
When reinstalling the local pip package for tests, make sure to delete the build folder generated on the root folder of the project,
as retaining that folder can lead to the project being built using that folder and not catching any changes you made to
the project files.