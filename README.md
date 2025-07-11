# PythonREST CLI  

![image](https://drive.google.com/uc?export=view&id=1FMzeZQL2JpKmkODdIcLVTSQC149rvFEg)

PythonREST is the ultimate full API generator for Python language. Based on the best performing frameworks and software development best practices, PythonREST can create an entire CRUD API in minutes or seconds based on your relational database on a single CLI command. This allows you to create your APIs from scratch and update your current API previously created with our tool to always match your latest database definitions.

THIS WILL SAVE YOU MONTHS OF DEVELOPMENT TIME, GUARANTEED!

Your new generated API will have full CRUD compatibility with your mapped database and full swagger documentation and specs available. With your new API in hand, you will be able to containerize or serverless deploy it to any local, private and public cloud providers of your choice and use it at will! If you're interested in taking your API to the next level and don't know how, please inquiry us on the email below for consultancies.

This project is under active enhancement and we have several open GitHub issues so we can improve it even further, if you're an Open Source enthusiast and wish to contribute, we'd be more than happy to have you on our team! Get in touch via admin@seventechnologies if you have any doubts or suggestions and don't forget to star rate our repo!

### If you like our solution, please consider donating on our [Patreon campaign](https://www.patreon.com/seventechnologies)!

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

## Version Disclaimer

**Version 0.2.1**
* Added some quality of life improvements for redoc building

**Version 0.2.4**
* Adding ssh and ssl connection methods (direct file provision only where applicable)
* Support for PostgreSQL MONEY type (mapped as string on code)
* Implementation of GROUPBY SQL Statement as a header for tables routes

**Version 0.2.6:**
Support for column names that contain unusual characters, like "-", " ", ".", "/", "\", ":", "~", "*", "+", "|", "@"

**Version 0.2.7:**
* SQL Views are not listed as routes on generated API anymore
* Fixing some cases of exceptions being returned improperly as bytes like object
* Fixing [or] filter of GET routes when using multiple query params simultaneously
* Improving rendering of swagger and redoc pages

**Version 0.2.8:**
* Small fixes to swagger improved rendering

**Version 0.2.9:**
* Support for columns named with Python reserved keywords

**Version 0.3.0:**
* Adding fixed version for generated API libraries to avoid breaking changes

**Version 0.3.1:**
* Setting READ COMMITTED isolation level on mysql and mariadb resolvers

**Version 0.3.2:**
* Adding fix for search path option not working on some PostgreSQL environments

**Version 0.3.3:**
* Adding powershell test scripts for mysql, postgresql and sqlserver

**Version 0.3.4:**
* Fix CORS issue by properly configuration of after request decorator function

**Version 0.3.5:**
* Synchronization between the versions on PyPI and the releases on GitHub

**Version 0.3.6:**
* Introduced Model Context Protocol (MCP) endpoints for dynamic LLM configuration and interaction

**Version 0.3.7:**
* Adding metadata to reserved keyword formatter


## Installation

To begin working with PythonREST, you can visit our [website's download page](https://pythonrest.seventechnologies.cloud/en/download) and download the installer for your system or if you're more
familiar with package managers, we have options for that below.

### Chocolatey

```ps
choco install pythonrest
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
pip install wheel --upgrade
pip install pip --upgrade
```

- Finally, install pymssql with the below commands:

```bash
export CFLAGS="-I$(brew --prefix openssl)/include"
export LDFLAGS="-L$(brew --prefix openssl)/lib -L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
pip install --pre --no-binary :all: pymssql --no-cache
```

After a successful installation of pymssql, you can then proceed with the installation of pythonrest using pip or the
download on the website
<br></br>

## Prerequisites

To use PythonREST, you must have Python 3.11 installed on your machine.
You'll also need credentials that can connect to your desired database so that the generator can access it and create
your API. If you're not familiar with creating and connecting to relational databases, you can check these
[articles](https://medium.com/@seventechnologiescloud/) written by us at Seven Technologies on how to create local
databases (MySQL, PostgreSQL, SQLServer and MariaDB) using Docker and connect to it.
<br></br>

## Usage

Here are some pythonrest usage examples:

Check version:

```bash
pythonrest version
```

### Password-based Authentication

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

Generate APIs based on MariaDB databases:

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

### SSH-Based Authentication

#### SSH with Password

Generate MySQL database-based APIs with SSH password authentication:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-password-authenticatio-string ssh://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>?local_bind_port=<LOCAL_BIND_PORT>
```

Generate Postgres database-based APIs with SSH password authentication:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public --ssh-password-authenticatio-string ssh://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>?local_bind_port=<LOCAL_BIND_PORT>
```

Generate SQLServer database-based APIs with SSH password authentication:

```bash
pythonrest generate --sqlserver-connection-string mssql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-password-authenticatio-string ssh://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>?local_bind_port=<LOCAL_BIND_PORT>
```

Generate MariaDB database-based APIs with SSH password authentication:

```bash
pythonrest generate --mariadb-connection-string mariadb://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-password-authenticatio-string ssh://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>?local_bind_port=<LOCAL_BIND_PORT>
```

Generate Aurora MySQL database-based APIs with SSH password authentication:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-password-authenticatio-string ssh://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>?local_bind_port=<LOCAL_BIND_PORT>
```

Generate Aurora Postgres database-based APIs with SSH password authentication:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public --ssh-password-authenticatio-string ssh://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>?local_bind_port=<LOCAL_BIND_PORT>
```

#### SSH with Public Key

Generate MySQL database-based APIs with SSH public key authentication:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-publickey-authentication-string ssh://<USER>@<ENDPOINT>:<PORT>?key_path=/path/your/public/key/id_rsa?local_bind_port=<LOCAL_BIND_PORT>
```

Generate Postgres database-based APIs with SSH public key authentication:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public --ssh-publickey-authentication-string ssh://<USER>@<ENDPOINT>:<PORT>?key_path=/path/your/public/key/id_rsa?local_bind_port=<LOCAL_BIND_PORT>
```

Generate SQLServer database-based APIs with SSH public key authentication:

```bash
pythonrest generate --sqlserver-connection-string mssql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-publickey-authentication-string ssh://<USER>@<ENDPOINT>:<PORT>?key_path=/path/your/public/key/id_rsa?local_bind_port=<LOCAL_BIND_PORT>
```

Generate MariaDB database-based APIs with SSH public key authentication:

```bash
pythonrest generate --mariadb-connection-string mariadb://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-publickey-authentication-string ssh://<USER>@<ENDPOINT>:<PORT>?key_path=/path/your/public/key/id_rsa?local_bind_port=<LOCAL_BIND_PORT>
```

Generate Aurora MySQL database-based APIs with SSH public key authentication:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssh-publickey-authentication-string ssh://<USER>@<ENDPOINT>:<PORT>?key_path=/path/your/public/key/id_rsa?local_bind_port=<LOCAL_BIND_PORT>
```

Generate Aurora Postgres database-based APIs with SSH public key authentication:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public --ssh-publickey-authentication-string ssh://<USER>@<ENDPOINT>:<PORT>?key_path=/path/your/public/key/id_rsa?local_bind_port=<LOCAL_BIND_PORT>
```

### SSL/TLS-Based Authentication

Generate MySQL database-based APIs with SSL authentication:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssl-authentication-string ssl://ssl_ca=./path/your/ssl/ca-cert.pem?ssl_cert=./path/your/ssl/server-cert.pem?ssl_key=./path/your/ssl/server-key.pem?hostname=<HOST>
```

Generate Postgres database-based APIs with SSL authentication:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public --ssl-authentication-string ssl://ssl_ca=./path/your/ssl/ca-cert.pem?ssl_cert=./path/your/ssl/server-cert.pem?ssl_key=./path/your/ssl/server-key.pem?hostname=<HOST>
```

Generate SQLServer database-based APIs with SSL authentication:

```bash
pythonrest generate --sqlserver-connection-string mssql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssl-authentication-string ssl://ssl_ca=./path/your/ssl/ca-cert.pem?ssl_cert=./path/your/ssl/server-cert.pem?ssl_key=./path/your/ssl/server-key.pem?hostname=<HOST>
```

Generate MariaDB database-based APIs with SSL authentication:

```bash
pythonrest generate --mariadb-connection-string mariadb://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssl-authentication-string ssl://ssl_ca=./path/your/ssl/ca-cert.pem?ssl_cert=./path/your/ssl/server-cert.pem?ssl_key=./path/your/ssl/server-key.pem?hostname=<HOST>
```

Generate Aurora MySQL database-based APIs with SSL authentication:

```bash
pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA> --ssl-authentication-string ssl://ssl_ca=./path/your/ssl/ca-cert.pem?ssl_cert=./path/your/ssl/server-cert.pem?ssl_key=./path/your/ssl/server-key.pem?hostname=<HOST>
```

Generate Aurora Postgres database-based APIs with SSL authentication:

```bash
pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public --ssl-authentication-string ssl://ssl_ca=./path/your/ssl/ca-cert.pem?ssl_cert=./path/your/ssl/server-cert.pem?ssl_key=./path/your/ssl/server-key.pem?hostname=<HOST>
```

### Custom options

#### --result-path:

By default, PythonREST will generate the API on your current directory under a PythonRestAPI folder. To define a custom
path to your generated API please follow the example below:

```bash
pythonrest generate --mysql-connection-string <mysql_connection_string> --result-path C:\<YOUR_DESIRED_PATH_HERE>
```

The above will generate your API inside a PythonRestAPI folder created on the provided path.
The following folders/files will be modified(content deleted and recreated) if a PythonREST project is already in place:

- src/c_Domain
- src/a_Presentation/a_Domain
- src/b_Application/b_Service/a_Domain
- src/d_Repository/a_Domain
- src/a_Presentation/d_Swagger
- src/e_Infra/d_Validators/a_Domain
- src/e_Infra/g_Environment
- src/e_Infra/b_Builders/FlaskBuilder.py
- config
- app.py

This allows you to make customizations or enhancements on your generated API and new upgrades will only affect CRUD API feature folders

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

#### --project-name:

This options allows the user to define a custom name for his project, which will be displayed on the Swagger and Redoc
pages. If not defined, the default value for this parameter is `PythonREST`:

```bash
pythonrest generate --postgres-connection-string <POSTGRES_CONNECTION_STRING> --project-name MarketPlaceAPI
```

#### --uid-type:

This options allows the user to define if the Unique Identifier generation of the API will generate a UUIDv7 or a ULID.
the allowed values are `uuid` and `ulid`. If not defined, the default value for this parameter is `uuid`:

```bash
pythonrest generate --sqlserver-connection-string <SQLSERVER_CONNECTION_STRING> --uid-type ulid
```

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

## Add Environment Variables to use flask admin panel

    To access the administration panel you have to add the two environment variables below:
    ```
    os.environ['admin_panel_user'] = 'admin'
    os.environ['admin_panel_password'] = 'admin'
    ```

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
  <img src="https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihbQK1U9v54G2lToTwVSHhjxIi_5vHX4K2DYolaqNlddxBe6EDQGCvNMnHfIxN8a_9fDcUjvSYBke6IfJUwxJl3m_d769XFMDA=w1920-h922-rw-v1" alt="Swagger Select all Users"/>
</div>

### Insert Table Entry

<hr>
From the same swagger page we were in, the next route is the post /<table_name>, in which when you hit "try it out" it will present you with a sample JSON body to insert an entry on your table. The JSON body sent on the request is a list, so if you wish to you can provide multiple entries at once on table with the same request, below is an example of a request inserting three entries on a simple pre-designed USER table with 'id_user', 'username' and 'date_joined' fields:

<br>

<div align="center">
  <img src="https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihaavUYFGCNkfS22MbYfhqOdA8rJFTrGKKVb0xiGOb7JkcD5GNZUHba70ChHKh2mLOpcnOjmA-EEIwbGWWcVQwa-CFIDk3YKcfk=w1920-h922-rw-v1" alt="Swagger Insert User"/>
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
  <img src="https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihZfYl9MfsivfZV5uoP1v0yIqjCp4Bul9Lr4hrGouIIIdIesfKLjrUSAeybCKnVxB38hKRGpuM6Nzx5kUDNXlM4wFRAUnDTr4cI=w1920-h922-rw-v1" alt="Swagger Delete User"/>
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
  <img src="https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihZsD73oX2ZxfkoyN3tcLzilSRJ5p2GfbSWklJ5TuWhngXa0VgIBVbq5uX1jT5QXGaqGT1WKL5zgE7sLsjjtpLB9rRcsQUcohUE=w1920-h922-rw-v1" alt="Swagger Main Screen"/>
</div>

### /swagger/tablename

<hr>
For each table on your database, PythonREST creates an openapi page documentation for it, in which you can make your database queries targetting each table. To access them, simply append to the swagger endpoint url your table name in *flatcase* (**ALL WORDS TOGETHER IN LOWER CASE WITH NO SEPARATORS**).
<div align="center">
  <img src="https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihZsD73oX2ZxfkoyN3tcLzilSRJ5p2GfbSWklJ5TuWhngXa0VgIBVbq5uX1jT5QXGaqGT1WKL5zgE7sLsjjtpLB9rRcsQUcohUE=w1920-h922-rw-v1" alt="Swagger User Screen"/>
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

# Model Context Protocol (MCP) Endpoints

This project includes endpoints under the /mcp prefix that allow interaction with the Model Context Protocol, primarily for managing Language Model (LLM) configurations and interacting with the LLM agent.

1. LLM Configuration Endpoint: /mcp/ask/configure
This endpoint allows you to view and modify the runtime configuration for the LLM providers used by the application. This configuration overrides the default settings loaded from environment variables.

URL: /mcp/ask/configure
Purpose: Manage dynamic LLM settings (default provider, model, temperature) without restarting the application. API keys are not managed here; they must be set as environment variables.
1.1. Getting the Current Configuration (GET Request)
You can retrieve the currently effective LLM configuration by sending a GET request to this endpoint.

* Method: GET
Request: No request body is needed.
Response: A JSON object detailing the effective configuration, including the determined default provider, the source of the configuration (runtime file or environment variables), provider-specific settings (model, temperature), and the path to the runtime config file. API keys are excluded for security.

Example using curl:

curl -X GET http://localhost:5000/mcp/ask/configure

Example Response:

{
  "determined_default_provider": "openai",
  "config_source_default_provider": "runtime (llm_config.json)",
  "providers": {
    "gemini": {
      "model": "Service Default",
      "model_source": "Service Default",
      "temperature": "Service Default",
      "temperature_source": "Service Default"
    },
    "openai": {
      "model": "gpt-4o",
      "model_source": "runtime (llm_config.json)",
      "temperature": 0.7,
      "temperature_source": "runtime (llm_config.json)"
    },
    "anthropic": {
      "model": "claude-3-opus",
      "model_source": "environment default",
      "temperature": 0.9,
      "temperature_source": "runtime (llm_config.json)"
    }
  },
  "llm_config_file_path": "config/llm_config.json"
}

1.2. Setting the Runtime Configuration (POST Request)
You can modify the runtime LLM configuration by sending a POST request with a JSON payload specifying the desired actions.

* Method: POST
Request: A JSON payload with one or more of the following keys:
"set_runtime_default_provider"
"update_provider_settings"
"clear_provider_settings"
"clear_all_runtime_settings"
Response: A JSON object indicating the actions performed and any errors encountered.
Here's what each action key in the JSON payload does:

"set_runtime_default_provider":

Purpose: Sets the primary LLM provider to use.
Value: A string ("gemini", "openai", "anthropic") or null to revert to the environment variable default.
Example: "set_runtime_default_provider": "openai"
"update_provider_settings":

Purpose: Updates specific settings (model, temperature) for one or more providers.
Value: A dictionary where keys are provider names ("gemini", "openai", "anthropic") and values are dictionaries with settings ("model": string, "temperature": float).

Example:

"update_provider_settings": {
  "openai": {
    "model": "gpt-4o",
    "temperature": 0.7
  },
  "anthropic": {
    "temperature": 0.9
  }
}


"clear_provider_settings":

Purpose: Removes all runtime settings for a specific provider, causing it to use environment variable defaults again.
Value: A string representing the provider name ("gemini", "openai", or "anthropic").
Example: "clear_provider_settings": "gemini"
"clear_all_runtime_settings":

Purpose: Clears the entire runtime configuration file, reverting all settings to environment variable defaults.
Value: The boolean value true.
Example: "clear_all_runtime_settings": true
Example POST Request Payload (combined actions):

{
  "set_runtime_default_provider": "openai",
  "update_provider_settings": {
    "openai": {
      "model": "gpt-4o",
      "temperature": 0.7
    },
    "anthropic": {
      "temperature": 0.9
    }
  },
  "clear_provider_settings": "gemini"
}

Example using curl (to set default provider to openai):

curl -X POST \
  http://localhost:5000/mcp/ask/configure \
  -H 'Content-Type: application/json' \
  -d '{
    "set_runtime_default_provider": "openai"
  }'


2. LLM Ask Endpoint: /mcp/ask
This endpoint allows you to send natural language questions or requests to the LLM agent and receive a generated response.

URL: /mcp/ask

Purpose: Interact with the LLM for tasks like getting explanations, code examples, or information based on the system's context.

* Method: POST

Request: A JSON payload with a single key "question" containing your query as a string.

Example Payload:

{
    "question": "Show me how to get a list of users"
}


Response: A JSON object with a single key "answer". The value is an array of strings, where each string is a part of the LLM's response. This can include explanations, code blocks (often formatted with Markdown), or other relevant information.

Example using curl:

curl -X POST \
  http://localhost:5000/mcp/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Show me how to get a list of users"
  }'


Example Response (based on your provided output):

{
  "answer": [
      "To obtain a list of users, you can use the `/users` endpoint with the `GET` method.\n\nHere is an example curl command:",
      "```bash\ncurl -X GET '<API_BASE_URL_NOT_DEFINED_IN_SPEC>/users' \\\n     -H 'accept: application/json' \\\n     -H 'Authorization: Bearer <API_TOKEN>'\n```",
      "\n\n**Note:** The API base URL was not defined in the OpenAPI specification. Please replace `<API_BASE_URL_NOT_DEFINED_IN_SPEC>` with the actual base URL of the API."
  ]
}

This /mcp/ask endpoint is a powerful way to interact with the LLM's understanding of your project's API and capabilities.

<br>

## API Environment Variables

Generated API environment variables can be found on src/e_Infra/g_Environment/EnvironmentVariables.py and each one has the following utility:

- **domain_like_left** – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "%COLUMN_VALUE" search behavior whenever it's value is defined on a query parameter.
  Example: - Test - 1Test - NameTest - Example-Test

- **domain_like_right** – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "COLUMN_VALUE%" search behavior whenever it's value is defined on a query parameter.
  Example: - Test - Test1 - Test Name - Test-Example

- **domain_like_full** – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "%COLUMN_VALUE%" search behavior whenever a it's value is defined on a query parameter.
  Example: - Test - Test1 - TestName - Test-Example - 1Test - NameTest - Example-Test

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

- **query_limit** – Global result limiting of GET requests CRUD routes can return. Default value '_' means your CRUD GET requests won't have a maximum limit and will retrieve all data from a specified query even if your pagination or query limit parameters are not set. Valid values are any integer natural numbers (greater than 0) or '_'

- **display_stacktrace_on_error** – When enabled, the original Python exception appears in the JSON response when an error occurs in the request. Valid values are "True" or "False"

- **origins** – Defines allowed CORS origins, separated by comma.

- **headers** – Defines allowed CORS origins headers values, separated by comma.

- main_db_conn - Specifies the database type (mysql, pgsql, mssql, mariadb) of the database your custom API accesses. Should not be messed around to avoid breaking the code. Valid values are: mysql, pgsql, mssql and mariadb

- <PROJECT_DATABASE_TYPE>\_user - User to authenticate on API's database sessions.

- <PROJECT_DATABASE_TYPE>\_password - Password to authenticate on API's database sessions.

- <PROJECT_DATABASE_TYPE>\_host - The endpoint of your database.

- <PROJECT_DATABASE_TYPE>\_port - Port that is allowed access to your database.

- <PROJECT_DATABASE_TYPE>\_schema - On MySQL, MariaDB and SQLServer, this is the name of your database. On PostgreSQL, this is the schema inside of your database.

- pgsql_database_name - On PostgreSQL, this is the database name in which your selected schema resides.
  <br></br>

## Odd Column names behaviour

Starting from version 0.2.7 pythonrest added support for column names with unusual separators such as:

["-", " ", ".", "/", "\\", ":", "~", "*", "+", "|", "@"]

As such, they will be mapped on the API replacing all instances of those separators with the underscore separator, so 
that errors do not occur in the Python code. This mapping does not affect your database structure in any way.

Starting from version 0.2.9, support for python reserved keywords as column names was added. Any columns named with these
words will be mapped on the pythonrest generated API with a suffix "_prcolkey", for example:    

```python
columnname = 'class'
withsuffix = 'class_prcolkey'
```

This also does not affect your database structure in any way.

Below is a list of the words which will have the suffix "_prcolkey":

[
"False", "None", "True", "and", "as", "assert", "async", "await",
"break", "class", "continue", "def", "del", "elif", "else", "except",
"finally", "for", "from", "global", "if", "import", "in", "is",
"lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
"while", "with", "yield"
]

**NOTE:** Beware these suffixes and separators mapping affects the name of these columns on the request and response bodies.

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
- 'rsa==4.9'
- 'cryptography==42.0.7'
- 'cffi==1.16.0'
- 'pycparser==2.22'
- 'pyasn1==0.6.0'
- 'psycopg2==2.9.9'
- 'psycopg2-binary==2.9.9'
- 'pymssql==2.2.11'
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

# For Contributors: How to run this project on terminal and VSCode

To run using the command line, you need to open this project root folder on the terminal and run the project startup file
(pythonrest.py) with Python, that way you can test any modifications you made to the project without needing to build the
binary everytime, just run the command below, remembering to replace the test database properties on it:

```bash
python pythonrest.py generate --mysql-connection-string mysql://<user_name>:<password>@<endpoint>:<port>/<schema>
```

Also, if you wish to debug this project, and you usually use VSCode with Microsoft's Python extension, you can create a
launch configuration and put a structure similar to the below, only replacing the test database properties:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "pythonrest.py",
      "args": [
        "generate",
        "--mysql-connection-string",
        "mysql://<user_name>:<password>@<endpoint>:<port>/<schema>"
      ],
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

<br></br>

# For Contributors: How to Build Your Own Binaries and Installers

It is very important that you have all of the libraries used by the project (listed on requirements.txt) installed on your
machine or on venv, because pyinstaller uses the versions of the libraries installed on your machine to build the binaries.

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
    --collect-submodules rsa ^
    --collect-submodules cryptography ^
    --collect-submodules cffi ^
    --collect-submodules pycparser ^
    --collect-submodules pyasn1 ^
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
    --collect-submodules rsa \
    --collect-submodules cryptography \
    --collect-submodules cffi \
    --collect-submodules pycparser \
    --collect-submodules pyasn1 \
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
python setup.py sdist
```

This will use the setup.py from the root folder to build a tar.gz version of the library on a dist folder, from there you
can install the library with:

```commandline
pip install dist/pythonrest3-<VERSION>.tar.gz
```
replace the <VERSION> with the one on the setup.py file.

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
pip uninstall pythonrest3
```

When reinstalling the local pip package for tests, make sure to delete any of the following folders: `build`, `dist` and `*.egg.info` generated on the root folder of the project,
as retaining those can lead to the project being built using that folder and not catching any changes you made to
the project files.

# For Contributors: How to proceed with a PR
* The Pull Requests must be done from your forked repository to our main.
* The PR commit messages must follow the pattern: `versionx.x.x`
* The next version should consider the [last package manager published version](https://pypi.org/project/pythonrest3/#history) + 0.0.1 eg.: 0.2.7 on pypi + 0.0.1 =  0.2.8

<br></br>

## If you find our solution helpful, consider donating on our [Patreon campaign](https://www.patreon.com/seventechnologies)!

## Thank you for riding with us! Feel free to use and contribute to our project. PythonREST CLI Tool generates a COMPLETE API for a relational database based on a connection string. It reduces your API development time by 40-60% and it's OPEN SOURCE!

## Don't forget to star rate this repo if you like our job!
