# PythonREST CLI
<div align="center" style="padding:0px 100px 0px 0px">
  <img src="https://lh3.googleusercontent.com/u/0/drive-viewer/AEYmBYQaGLdP44igBcrFUpCFt2Fxa3E_fk1p8cmMDx2FmKCF9oWUKMxvgOZEYE7EOJD1mCRi8dFDhF-HpdY90PQQ5r6tXdqo=w1920-h922" alt="Logo" width="350"/>
</div>

PythonREST is the ultimate full API generator for Python language. Based on the best performing frameworks and software development best practices, PythonREST can create an entire CRUD API in minutes or seconds based on your relational database on a single CLI command. This allows you to create your APIs from scratch and update your current API previously created with our tool to always match your latest database definitions.

THIS WILL SAVE YOU MONTHS OF DEVELOPMENT TIME, GUARANTEED!

Your new generated API will have full CRUD compatibility with your mapped database and full swagger documentation and specs available. With your new API in hand, you will be able to containerize or serverless deploy it to any local, private and public cloud providers of your choice and use it at will! If you're interested in taking your API to the next level and don't know how, please inquiry us on the email below for consultancies.

This project is under active enhancement and we have several open GitHub issues so we can improve it even further, if you're an Open Source enthusiast and wish to contribute, we'd be more than happy to have you on our team! Get in touch via admin@seventechnologies if you have any doubts or suggestions and don't forget to star rate our repo! 

### If you like our solution, please consider donating on our [Patreon campaign](https://www.patreon.com/seventechnologiescloud)!
<br>

# How Is PythonREST good for Developers?
PythonREST allows you to have an entire CRUD API ready in minutes or seconds to fully manipulate your relational database. This will allow you to only need to write code specifically for functions that require third party integration or have super complex business rules. These are the project possibilities our project can provide you:

- Create an API with PythonREST, add your own custom routes and update your CRUD routes at will keeping the best of both worlds.
- Install PythonREST on your pipeline, containerize or serverless your new application and have entire APIs with no need for repositories for them.
- Have your PythonREST API manage your CRUD operations and any other applications in any language manage the rest. This is a nice option if you're not a Python developer and wish the best from both worlds.
<br></br>

# How Is PythonREST good for your Business?
PythonREST allows you to create Web, Mobile Apps, SaaS products or simply manage data transactions from your database in an easy and automated way. This will empower your teams and make your product lifecycles smoother and cleaner and will enable your to launch faster and more reliable products:

- Save effort, energy and money by having your development team have more time to focus on business driven functionalities. Using PythonREST can save you more than 50% of a product development time.
- Easy to use for free, consult us for Premium support and trainings on demand.
- Cloud friendly and easily adaptable to any workflow, even for teams that do not use Python as a development language.

## Key features
- Support for MySQL, PostgreSQL, SQLServer and MariaDB databases
- Full [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) (formerly known as Swagger) documentation
to use for making queries inside the database.
- Raw query execution via route requests
- Simple Stored Procedure execution supported
- Query filters(select, orderby, limit) on Get routes supported
- Pagination of queries
- Filter query results by each table field
<br>

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
<br></br>

## Prerequisites
To use PythonREST, you must have Python 3.11 installed on your machine.
You'll also need access to the your desired database so that the generator can assess it and create your API. If you're not familiar with creating and connecting to relational databases, you can check these [articles](https://medium.com/@seventechnologiescloud/) written by us at Seven Technologies on how to create local databases (MySQL, PostgreSQL, SQLServer and MariaDB) using Docker and connect to it.
<br></br>

## Usage

Here are some pythonrest usage examples:

Check version:

```bash
pythonrest version
```

Generate APIs based on MySQL databases:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>
```

Generate APIs based on Postgres databases:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public
```

Generate APIs based on SQLServer databases:

```bash
pythonrest generate --sqlserver-connection-string mssql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>
```

Generate APIs based on DariaDB databases:

```bash
pythonrest generate --mariadb-connection-string mariadb://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>
```

Generate APIs based on Aurora MySQL databases:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>
```

Generate APIs based on Aurora Postgres databases:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public
```


### Custom options
#### --result-path:
By default, PythonREST will generate the API on your current directory under a PythonRestAPI folder. To define a custom 
path to your generated API please follow the example below:

```bash
pythonrest generate --mysql-connection-string <mysql_connection_string> --result-path C:\<YOUR_DESIRED_PATH_HERE>
```

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

```bash
pythonrest generate --mysql-connection-string <MYSQL_CONNECTION_STRING> --no-use-pascal-case
```

#### --us-datetime:
If you have a database with datetime formatted to the us pattern of mm-dd-yyyy, you can use this option so that the api
will also respect that pattern when validating requests and responses:

```bash
pythonrest generate --mysql-connection-string <MYSQL_CONNECTION_STRING> --us-datetime
```
 
This behavior can be modified on the project's environment variables file(src/e_Infra/g_Environment/EnvironmentVariables.py), modifying the date_valid_masks variable. Some valid values are(more options and details on the API Environment Variables section below):
- "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y" -> This value accepts dates on YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD and DD/MM/YYYY formats
- "%Y-%m-%d, %m-%d-%Y, %Y/%m/%d, %m/%d/%Y" -> This value accepts dates on YYYY-DD-MM, MM-DD-YYYY, YYYY/DD/MM and MM/DD/YYYY formats
<br></br>

## How to Run Generated API
After generating your API, you may open it on your preferred IDE(VSCode, PyCharm, etc) or even the bash/cmd if you wish to, from there you may build your venv like below to run the project.

### How to Run with venv (Python virtual environment)
This project was initially built to run using a Python virtual environment, below we'll provide how to install the virtual environment and run the project on different systems:
#### Windows(CMD/Powershell):
1. Create the venv
First of all, you should open this project on your terminal, from now on all the commands will be run from the root folder of the project.
Below is the command to create a python venv:
```commandline
python -m venv venv
```
2. Activate the virtual environment
The below command is how to activate your venv for use on your current terminal session:
```commandline
.\venv\Scripts\activate
```
The above command works fine for CMD or Powershell. If you are using GitBash to run these commands, the only change would be running the below command instead of the above one:

```bash
source venv/Scripts/activate
```

3. Install required libraries for API to run
This project needs a number of libraries stored on PyPi to run, these are all listed on the requirements.txt file on the root folder of the generated project and to be installed you run the below command:
```commandline
pip install -r requirements.txt
```

4. Run app.py
After the libraries installation is complete, you can use the below command to run the project:
```commandline
python app.py
```
From there you can access the URL localhost:5000, which is the base endpoint to go to the project routes and make requests following the **API Usage Examples** section on this readme, our [blog](https://medium.com/@seventechnologiescloud/) and documentation at [readthedocs](https://readthedocs.org/projects/pythonrest/) 

#### Linux/Mac(Bash/Zsh):
1. Create the venv:
On Debian/Ubuntu systems, you need to have the python3-venv package installed, which you can do with the following commands:
```bash
apt-get update
apt install python3.8-venv
```
And then you can create the venv with the following:
```bash
python3 -m venv venv
```

2. Activate the virtual environment
The below command is how to activate your venv for use on your current terminal session:
```bash
source venv/bin/activate
```

3. Install required libraries for API to run
This project needs a number of libraries stored on PyPi to run, these are all listed on the requirements.txt file on the root folder of the generated project and to be installed you run the below command:
```bash
pip install -r requirements.txt
```

4. Run app.py
After the libraries installation is complete, you can use the below command to run the project:
```bash
python app.py
```
From there you can access the URL localhost:5000, which is the base endpoint to go to the project routes and make requests following the **API Usage Examples** section on this readme, our [blog](https://medium.com/@seventechnologiescloud/) and documentation at [readthedocs](https://readthedocs.org/projects/pythonrest/) 
<br></br>

## Run and Debug using venv with VSCode
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
<br>

## API Usage Examples
After following the **How to run** section to its final steps, with your project running you can finally test the routes it creates, to follow the below examples, if you have a table named user, you would want to access localhost:5000/swagger/user to check the routes provided to that table.

### Select All Table Entries
<hr>
Starting with a basic use, you go to your swagger/<table_name>, the first route is the get one, if you just hit "try it out" and then "execute", it will present you with a response equivalent to a SELECT * from <table_name> query. If you wish to, you can use the available filters to select only the attributes that you want to retrieve, limit the number of results, paginate your results and so on. If you still did not have anything on your database to retrieve, it will just be an empty list, now we can get to our next use case to solve that!

<br>

<div align="center">
  <img src="https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYRxL8hUgfencMlNjW35HP7fx_ZvlheJUuPjefCisGhDu6VxE2HUt9aOFSiBMOSpYXe8J5KKZZGN50VNt8VoleEz_GFw=w2880-h1404" alt="Swagger Select all Users"/>
</div>

### Insert Table Entry
<hr>
From the same swagger page we were in, the next route is the post /<table_name>, in which when you hit "try it out" it will present you with a sample JSON body to insert an entry on your table. The JSON body sent on the request is a list, so if you wish to you can provide multiple entries at once on table with the same request, below is an example of a request inserting three entries on a simple pre-designed USER table with 'id_user', 'username' and 'date_joined' fields:

<br>

<div align="center">
  <img src="https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYSKKVmPS5CH_OCAbonoV_DJbjXq2IS5wGx6Q-CPAn4dI7Jo2W-2kx193E5lOg3VSrPmFRtz_1G8sYld8hUjT6JuagQjkQ=w2880-h1404" alt="Swagger Insert User"/>
</div>

<br>

Example JSON payload:
```json
[
  {
    "id_user": 1,
    "username": "user1",
    "date_joined": "2000-01-01 12:00:00"
  },
  {
    "id_user": 2,
    "username": "user2",
    "date_joined": "2000-01-01 12:00:00"
  },
  {
    "id_user": 3,
    "username": "user3",
    "date_joined": "2000-01-01 12:00:00"
  }
]
```

### Delete Table Entry
<hr>
Now we're talking about the delete /user route, if you hit "try it out" it will also present you with a sample JSON body of a generic object of your table, you can then use that example, modify its values to suit an entry that exists on your database. Note that this is a delete by full match route, so you need to provide the correct values for all of the table collumns on your response, below is an example of JSON body to delete a user table entry that has 3 columns: id_user, username and date_joined:

<br>

<div align="center">
  <img src="https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYTi11erJfknIMgb0R2auyanxd_g34kkoVcNYXfS5Kct20SRB-dsqOi7pMRG9UGXV_hAaiGOGvLf6CM8LQOxVMDedqGFXw=w2880-h1404" alt="Swagger Delete User"/>
</div>

<br>

```json
[
  {
    "id_user": 2,
    "username": "user2",
    "date_joined": "2000-01-01 12:00:00"
  }
]
```

For more detailed examples, please check our [blog](https://medium.com/@seventechnologiescloud/) and documentation at[readthedocs](https://readthedocs.org/projects/pythonrest/)
<br></br>


## Swagger Overview
When running the API, it will provide you with a localhost url, then you have the following swagger pages accessible:

### /swagger
<hr>
That's the base route for viewing swagger, it contains the documentation of the SQL routes present on the application
<div align="center">
  <img src="https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYR_dUffHUELqs1yay5iiqu0ltnAtbLqtPgjwjpsHv5IRhCRfZuhv0B5qVvPG5ZHm0ThT08xu99zsZuCRMblvjuFSasp=w2880-h1508" alt="Swagger Main Screen"/>
</div>

### /swagger/tablename
<hr>
For each table on your database, PythonREST creates an openapi page documentation for it, in which you can make your database queries targetting each table. To access them, simply append to the swagger endpoint url your table name in *flatcase* (**ALL WORDS TOGETHER IN LOWER CASE WITH NO SEPARATORS**).
<div align="center">
  <img src="https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYRfUGgCAiU0KSLZJjLGttaIuBCf5vRNWa8ioShBm7KQtm_EkwwLSHiW-G2hZbi-25SH-x_HtkLKjizLfxafbYMnJ-D0uA=w2880-h1508" alt="Swagger User Screen"/>
</div> 
<br>

## Postman/cURL
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
<br>

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

- <PROJECT_DATABASE_TYPE>_user - User to authenticate on API's database sessions.

- <PROJECT_DATABASE_TYPE>_password - Password to authenticate on API's database sessions.

- <PROJECT_DATABASE_TYPE>_host - The endpoint of your database.

- <PROJECT_DATABASE_TYPE>_port - Port that is allowed access to your database.

- <PROJECT_DATABASE_TYPE>_schema - On MySQL, MariaDB and SQLServer, this is the name of your database. On PostgreSQL, this is the schema inside of your database.

- pgsql_database_name - On PostgreSQL, this is the database name in which your selected schema resides.
<br></br>

# Generated API Directory Structure
The generated API has a structure of a number of directories with sub-directories. This section will explain that division in order to enlighten the project for debugging and feature implementations. Taking from the root of the generated project, we have:
- config/: This directory contains all of the swagger files of the project, the main one and each database table swagger page.
- src/a_Presentation: This directory houses the controllers of the project, the files which are responsible for defining the routes of the project, creating functions for each route and defining the parameters used by them
  - src/a_Presentation/a_Domain: Contains the controllers for all of the domains of the project, which are the tables scanned by PythonREST of your database.
  - src/a_Presentation//b_Custom: Contains controllers of other sections of the project, like the SQL routes controllers, OPTIONS method conrollers(that deals with CORS and its related stuff), before request controller, which prints the request on terminal and exception handler controller, which prints the error on terminal and calls a function to build the response error to be returned as a response
  - src/a_Presentation/d_Swagger: Contains the swagger routes controllers, which notifies the project which swagger file it should open when determined route is accessed.
- src/b_Application: This directory houses the services and DTOs of the project.
  - src/b_Application/a_DTO: This directory houses any custom DTOs(Data Transfer Objects are a structured and serializable object used to encapsulate and transport data between layers of an application or between different parts of a distributed system) that would be created for the project, separated by request(src/b_Application/a_DTO/a_Request) and response(src/b_Application/a_DTO-b_Response)
  - src/b_Application/b_Service: The service files are contained here, which are the files responsible for data manipulation, validation, and communication with external systems.
    - src/b_Application/b_Service/a_Domain: All of the service files for the domains are contained here
    - src/b_Application/b_Service/b_Custom: All of the sql routes, before request and error handler services are contained here.
- src/c_Domain: Contains all the main classes of the project domains, which define how each table is structured.
- src/d_Repository: This directory houses the repositories of the project, they are the data access layer responsible for handling database interactions and they are involved in doing the direct CRUD (Create, Read, Update, Delete) operations on data entities.
- src/d_Repository/GenericRepository.py: Contains functions responsible for each of the routes transactions, selecting objects(by id or just a select all), inserting objects, updating objects and deleting objects(by id or by full match) and applies necessary business logics or functionalities before executing the queries on the database.
    - src/d_Repository/a_Domain: This directory contains files for each table, in which you can set your custom repositories for each one separately.
    - src/d_Repository/b_Transactions: Contains functions responsible for each of the routes transactions, selecting objects(by id or just a select all), inserting objects, updating objects and deleting objects(by id or by full match) and on these calls the methods of the GenericRepository.py
    - src/d_Repository/d_DbConnection: Contains the function responsible for creating a connection string to the database accessed by the project.
- src/e_Infra: Contains files or components that deal with the foundational structure, setup and configuration of the project.
  - src/e_Infra/a_Handlers: Contains files used to configure exceptions and system messages returned by the API
  - src/e_Infra/b_Builders: Contains files used to configure and build date times, domain objects, flask, proxy responses, sql alchemy, strings
    - src/e_Infra/b_Builders/a_Swagger: Contains the functions to build the Swagger blueprints that renders the Swagger page.
  - src/e_Infra/c_Resolvers: Contains functions to deal with some logics and operations like creation of engine and session of a connected database and filtering queries with left like, right lke and the such.
  - src/e_Infra/d_Validators: Contains functions that validates if given requests have correct data, like JSON bodies, datetimes values, types of table parameters.
  - src/e_Infra/d_Validators/a_Domain: Contains functions for each domain in which custom validators can be set.
  - src/e_Infra/f_Decorators: Contains decorator functions, which modify or extend the behavior of functions by wrapping them with additional functionality.
  - src/e_Infra/g_Environment: Contains the environment variables used by the project.
  - src/e_Infra/CustomVariables.py: Contains functions to return custom values used by the code, like empty dicts, empty lists and more.
  - src/e_Infra/GlobalVariablesManager.py: Contains a function to call the environment variables if they exist or None if they don't.
  - src/g_Tests: Directory to store the UnitTests created to test the project's functionalities. 

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
## Windows
```commandline
pip install -r requirements.txt
```

## Linux/Mac
```bash
sudo pip install -r requirements.txt
```
<br></br>

# For Contributors: How to Build Your Own Binaries and Installers

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
<br></br>

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

<br></br>
## If you find our solution helpful, consider donating on our [Patreon campaign](https://www.patreon.com/seventechnologiescloud)!
## Thank you for riding with us! Feel free to use and contribute to our project. PythonREST CLI Tool generates a COMPLETE API for a relational database based on a connection string. It reduces your API development time by 40-60% and it's OPEN SOURCE!
## Don't forget to star rate this repo if you like our job!