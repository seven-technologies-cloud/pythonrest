# PythonREST CLI
<div style="display:flex;justify-content:center"><img src="https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYRwXKtdeE8-HqRdDC2xuB42_glxttz2rFC_BJ-_zOTUA6Aa4DlebuFJcn1KkoBEi3rQKVuFxc2yQeNBmSX_1F_no-qHAA=w2880-h1508" alt="Logo" width="350"/></div>


PythonREST is the ultimate full API generator for Python language. Based on the best performing frameworks and software development best practices, PythonREST can create an entire CRUD API in minutes or seconds based on your relational database on a single CLI command. This allows you to create your APIs from scratch and update your current API previously created with our tool to always match your latest database definitions.

THIS WILL SAVE YOU MONTHS OF DEVELOPMENT TIME, GUARANTEED!

Your new generated API will have full CRUD compatibility with your mapped database and full swagger documentation and specs available. With your new API in hand, you will be able to containerize or serverless deploy it to any local, private and public cloud providers of your choice and use it at will! If you're interested in taking your API to the next level and don't know how, please inquiry us on the email below for consultancies.

This project is under active enhancement and we have several open GitHub issues so we can improve it even further, if you're an Open Source enthusiast and wish to contribute, we'd be more than happy to have you on our team! Get in touch via admin@seventechnologies if you have any doubts or suggestions and don't forget to star rate our repo! 

if you like our solution, please consider donating on our [Patreon campaign](https://www.patreon.com/seventechnologiescloud)!

## Key features
- Support for MySQL, PostgreSQL, SQLServer and MariaDB databases
- Full [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) (formerly known as Swagger) documentation
to use for making queries inside the database.
- Raw query execution via route requests
- Simple Stored Procedure execution supported
- Query filters(select, orderby, limit) on Get routes supported
- Pagination of queries
- Filter query results by each table field

## Installation
To begin working with PythonREST, you can visit our [website's download page](https://pythonrest.seventechnologies.cloud/en/download) and download the installer for your system or if you're more 
familiar with package managers, we have options for that below.

### Chocolatey

```ps
choco install pythonrest --version=0.1.0
```

### Pip

```bash
pip install pythonrest3
```

## ⚠️ Disclaimer for Mac users
As of now, pythonrest may fail on installation or present some errors when trying to use it, showing issues with the pymssql library, this is due to the latter having some issues to install on Mac machines, sometimes the library is installed but presents some errors on usage and other times it does not even complete installation. So, if you have issues with it to install/run pythonrest, follow the below steps to fix pymssql:
- Uninstall any version of pymssql if applicable:
```bash
pip uninstall pymssql
```

- Install necessary software libraries (using brew) to run pymssql:
```bash
brew install FreeTDS
brew install openssl
```

- Install and/or upgrade some pip libraries used to build pymssql library and used to run pymssql on the machine:
```bash
pip install --upgrade pip setuptools
pip install cython --upgrade
pip install –upgrade wheel
pip install --upgrade pip
```

- Finally, install pymssql with the below commands:
```bash
export CFLAGS="-I$(brew --prefix openssl)/include"
export LDFLAGS="-L$(brew --prefix openssl)/lib -L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
pip install --pre --no-binary :all: pymssql --no-cache
```
After a successful installation of pymssql, you can then proceed with the installation of pythonrest using pip

## Prerequisites
To use PythonREST, you must have Python 3.11 installed.
You'll also need a database so that the generator can access and create an API on top of it. If you're not familiar with creating and connecting to databases, you can check these [articles](https://medium.com/@seventechnologiescloud/) written by us at Seven Technologies Clouds, on how to create a local database (MySQL, PostgreSQL, SQLServer and MariaDB) using Docker and connect to it.

## Usage

Here are some pythonrest usage examples:

Check version:

`pythonrest version`

Generate API based on mysql database:

`pythonrest generate --mysql-connection-string <mysql_connection_string>`

Generate API based on postgres database:

`pythonrest generate --postgres-connection-string <postgres_connection_string>`

Generate API based on sqlserver database:

`pythonrest generate --sqlserver-connection-string <sqlserver_connection_string>`

Generate API based on mariadb database:

`pythonrest generate --mariadb-connection-string <mariadb_connection_string>`

### Custom options
#### --result-path:
By default, PythonREST will generate the API on your current directory, under a PythonRestAPI folder, but there is also 
a possibility to define a custom path to your generated API, following the below example:

`pythonrest generate --mysql-connection-string <mysql_connection_string> --result-path C:\Users\<your_user_here>\Documents\PythonRestCustomFolder`

The above will generate your API on the provided path, and if the folder does not exist the generator will create i.
The following folders/files will be modified(content deleted and recreated) if a PythonREST project is already in place:
- src/c_Domain
- src/a_Presentation/a_Domain
- src/b_Application/b_Service/a_Domain
- src/d_Repository/a_Domain
- src/a_Presentation/d_Swagger
- src/e_Infra/b_Builders/a_Swagger
- src/e_Infra/d_Validators/a_Domain
- src/e_Infra/g_Environment
- src/e_Infra/b_Builders/FlaskBuilder.py
- config
- app.py
This allows you to make customizations or enhancements on your generated API and new upgrades will only affect CRUD API feature folders
## ⚠️ Disclaimer
Keep in mind that the provided folder will have all of its files deleted before generating the API, except when a PythonREST project is already in place

#### --use-pascal-case:
This option creates the Python Domain Classes with PascalCase pattern for their names, if this option is provided as
--no-use-pascal-case, you will be prompted to provide a name of python class for each table of your database:

`pythonrest generate --mysql-connection-string <mysql_connection_string> --no-use-pascal-case`

#### --us-datetime:
If you have a database with datetime formatted to the us pattern of mm-dd-yyyy, you can use this option so that the api
will also respect that pattern when validating requests and responses:

`pythonrest generate --mysql-connection-string <mysql_connection_string> --us-datetime`
 
This behavior can be modified on the project's environment variables file(src/e_Infra/g_Environment/EnvironmentVariables.py), modifying the date_valid_masks variable. Some valid values are(more options and details on the API Environment Variables section below):
- "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y" -> This value accepts dates on YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD and DD/MM/YYYY formats
- "%Y-%m-%d, %m-%d-%Y, %Y/%m/%d, %m/%d/%Y" -> This value accepts dates on YYYY-DD-MM, MM-DD-YYYY, YYYY/DD/MM and MM/DD/YYYY formats

### How to Run

#### venv run
If you wish to run this project using a Python virtual environment, you can follow the steps below:

1. Create a virtual environment:

#### Windows:

```commandline
python -m venv venv
```

#### Linux/Mac:
On Debian/Ubuntu systems, you need to have the python3-venv package installed, which you can do with the following commands:
```bash
apt-get update
apt install python3.8-venv
```
And then you can create the venv with the following:
```bash
python3 -m venv venv
```
2. Activate the virtual environment:
#### Windows:
```
.\venv\Scripts\activate
```

#### Linux/Mac:
```bash
source venv/bin/activate
```

3. Install required libraries for API to run:
```commandline
pip install -r requirements.txt
```

4. Run app.py:
```commandline
python app.py
```

#### Run and Debug using venv with VSCode
If you wish to go deep and debug the API, or simply wishes to run from VSCode Python extension, you'll want to configure
a launch.json file for the API, to do that you'll go to the top bar of VSCode -> Run(if run is not visible, you may find
it in the "..." on the title bar) -> Add Configuration.
Doing that will generate your launch.json, in which you'll want to add a "python" key, similar to the example below:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "python": "${command:python.<full_path_to_your_venv_python_exe_file>}",
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

## Swagger Overview
When running the API, it will provide you with a localhost url, then you have the following swagger pages accessible:
#### /swagger
That's the base route for viewing swagger, it contains the documentation of the SQL routes present on the application

#### /swagger/tablename
For each table on your database, PythonREST creates an openapi page documentation for it, in which you can make your database queries targetting each table. To access them, simply append to the swagger endpoint url your table name in flatcase(all words together in lower case with no separators).

### Postman/cURL
If you're familiar with Postman or using cURL requests directly, you can make requests to the routes shown in the open api specification, using the examples of usage present on it to build your request.
For example, a table user with id_user, username and date_joined fields would have a POST cURL request like:
```bash
curl -X 'POST' \
  'http://localhost:5000/user' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "id_user": 1,
    "username": "first_user",
    "date_joined": "2024-01-01 12:00:00"
  }
]'
```

### Use cases
#### select all table items
Starting with a basic use, you go to your swagger/<table_name>, the first route is the get one, if you just hit "try it out" and then "execute", it will present you with a response equivalent to a SELECT * from <table_name> query. If you wish to, you can use the available filters to select only the attributes that you want to retrieve, limit the number of results, paginate your results and so on. If you still did not have anything on your database to retrieve, it will just be an empty list, now we can get to our next use case to solve that!

#### insert table item
From the same swagger page we were in, the next route is the post /<table_name>, in which when you hit "try it out" it will present you with a sample JSON body to insert an entry on your table. 

For more detailed use cases, you can check our [blog](https://medium.com/@seventechnologiescloud/) and [readthedocs](https://readthedocs.org/projects/pythonrest/)

## API Environment Variables
Generated API environment variables can be found on src/e_Infra/g_Environment/EnvironmentVariables.py and each one has the following utility:
- **domain_like_left** – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "%COLUMN_VALUE" search behavior whenever it's value is defined on a query parameter.
Example:
    - Test
    - 1Test
    - NameTest
    - Example-Test

- **domain_like_right** – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "COLUMN_VALUE%" search behavior whenever it's value is defined on a query parameter.
Example:
    - Test
    - Test1
    - Test Name
    - Test-Example

- **domain_like_full** – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "%COLUMN_VALUE%" search behavior whenever a it's value is defined on a query parameter.
Example:
    - Test
    - Test1
    - TestName
    - Test-Example
    - 1Test
    - NameTest
    - Example-Test

- **date_valid_masks** – Specifies the date formats accepted by the API. Valid values are:
    - "%Y-%m-%d" - This value accepts dates on YYYY-MM-DD format
    - "%d-%m-%Y" - This value accepts dates on DD-MM-YYYY format
    - "%Y/%m/%d" - This value accepts dates on YYYY/MM/DD format
    - "%d/%m/%Y" - This value accepts dates on DD/MM/YYYY format
    - "%m-%d-%Y" - This value accepts dates on MM-DD-YYYY format
    - "%m/%d/%Y" - This value accepts dates on MM/DD/YYYY format
    Your end result can be a combination of two or more of the previous options, like the following examples:
    - "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y" This value accepts dates on YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD and DD/MM/YYYY formats(default API generation behavior with us-datetimes set to false)
    - "%Y-%m-%d, %m-%d-%Y, %Y/%m/%d, %m/%d/%Y" This value accepts dates on YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD and MM/DD/YYYY formats(default API generation behavior with us-datetimes set to true)

    ⚠️ Disclaimer
    The previous behavior affects all fields from all database tables, is is not possible at this point to specify these rules for specific table columns

- **time_valid_masks** – Specifies the time formats accepted by the API. Valid values are:
    - "%H:%M:%S" This value accepts times on HH:MM:SS format
    - "%I:%M:%S %p" This value accepts times on HH:MM:SS AM/PM format 
    - "%H:%M" This value accepts times on HH:MM format
    - "%I:%M %p" This value accepts times on HH:MM AM/PM format
    - "%I:%M:%S%p" This value accepts times on HH:MM:SSAM/PM format
    - "%I:%M%p" This value accepts times on HH:MMAM/PM format
    Your end result can be a combination of two or more of the previous options, like the following example(default API generation behavior):
    - "%H:%M:%S, %I:%M:%S %p, %H:%M, %I:%M %p, %I:%M:%S%p, %I:%M%p"

    ⚠️ Disclaimer
    The previous behavior affects all fields from all database tables, is is not possible at this point to specify these rules for specific table columns

- **query_limit** – Global result limiting of GET requests CRUD routes can return. Default value '*' means your CRUD GET requests won't have a maximum limit and will retrieve all data from a specified query even if your pagination or query limit parameters are not set. Valid values are any integer natural numbers (greater than 0) or '*'

- **display_stacktrace_on_error** – When enabled, the original Python exception appears in the JSON response when an error occurs in the request. Valid values are "True" or "False"

- **origins** – Defines allowed CORS origins, separated by comma.

- **headers** – Defines allowed CORS origins headers values, separated by comma.

- main_db_conn - Specifies the database type (mysql, pgsql, mssql, mariadb) of the database your custom API accesses. Should not be messed around to avoid breaking the code. Valid values are: mysql, pgsql, mssql and mariadb

- <project_database_type>_user - User to authenticate on API's database sessions.

- <project_database_type>_password - Password to authenticate on API's database sessions.

- <project_database_type>_host - The endpoint of your database.

- <project_database_type>_port - Port that is allowed access to your database.

- <project_database_type>_schema - On MySQL, MariaDB and SQLServer, this is the name of your database. On PostgreSQL, this is the schema inside of your database.

- pgsql_database_name - On PostgreSQL, this is the database name in which your selected schema resides.


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

# Linux/Mac
```bash
sudo pip install -r requirements.txt
```

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

If you find our solution helpful, we would appreciate your support through a donation to our [Patreon campaign](https://www.patreon.com/seventechnologiescloud)!

Thank you for riding with us! Feel free to use and contribute to our project. PythonREST CLI Tool generates a COMPLETE API for a relational database based on a connection string. It reduces your API development time by 40-60% and it's OPEN SOURCE!
Don't forget to star rate this repo if you like our job!