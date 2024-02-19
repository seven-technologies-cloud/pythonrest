Usage
=====

.. _installation:

Installation
------------

To begin working with PythonREST, you can visit our `website's download page <https://pythonrest.seventechnologies.cloud/en/download>`_ and download the installer for your system or if you're more familiar with package managers, we have options for that below.

Chocolatey
~~~~~~~~~~

.. code-block::

   choco install pythonrest --version=0.1.0

Pip
~~~~~~~~~~

.. code-block::

   pip install pythonrest3

Disclaimer for Mac users
^^^^^^^^^^^^^^^^^^^^^^^^

As of now, pythonrest may fail on installation or present some errors when trying to use it, showing issues with the pymssql library, this is due to the latter having some issues to install on Mac machines, sometimes the library is installed but presents some errors on usage and other times it does not even complete installation. So, if you have issues with it to install/run pythonrest, follow the below steps to fix pymssql:

1. Uninstall any version of pymssql if applicable:

.. code-block::

   pip uninstall pymssql

2. Install necessary software libraries (using brew) to run pymssql:

.. code-block::

   brew install FreeTDS
   brew install openssl

3. Install and/or upgrade some pip libraries used to build pymssql library and used to run pymssql on the machine:

.. code-block::

   pip install --upgrade pip setuptools
   pip install cython --upgrade
   pip install –upgrade wheel
   pip install --upgrade pip
   
4. Finally, install pymssql with the below commands:

.. code-block::

   export CFLAGS="-I$(brew --prefix openssl)/include"
   export LDFLAGS="-L$(brew --prefix openssl)/lib -L/usr/local/opt/openssl/lib"
   export CPPFLAGS="-I$(brew --prefix openssl)/include"
   pip install --pre --no-binary :all: pymssql --no-cache

.. note::

   After a successful installation of pymssql, you can then proceed with the installation of pythonrest using pip

PythonREST CLI Usage
--------------------

Prerequisites
~~~~~~~~~~~~~

To use PythonREST, you must have Python 3.11 installed on your machine. You'll also need access to the your desired database so that the generator can assess it and create your API. If you're not familiar with creating and connecting to relational databases, you can check these `articles <https://medium.com/@seventechnologiescloud/>`_ written by us at Seven Technologies on how to create local databases (MySQL, PostgreSQL, SQLServer and MariaDB) using Docker and connect to it.

Instructions
~~~~~~~~~~~~

Here are some pythonrest usage examples:

Check version:

.. code-block::
   pythonrest version

Generate APIs based on MySQL databases:

.. code-block::
   pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>

Generate APIs based on Postgres databases:

.. code-block::
   pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public

Generate APIs based on SQLServer databases:

.. code-block::
   pythonrest generate --sqlserver-connection-string mssql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>

Generate APIs based on DariaDB databases:

.. code-block::

   pythonrest generate --mariadb-connection-string mariadb://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>

Generate APIs based on Aurora MySQL databases:
.. code-block::

   pythonrest generate --mysql-connection-string mysql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<SCHEMA>

Generate APIs based on Aurora Postgres databases:
.. code-block::

   pythonrest generate --postgres-connection-string postgresql://<USER>:<PASSWORD>@<ENDPOINT>:<PORT>/<DATABASE_NAME>?options=-c%20search_path=<SCHEMA>,public

Custom options
~~~~~~~~~~~~~~

\*\*--result-path\*\*:
By default, PythonREST will generate the API on your current directory under a PythonRestAPI folder. To define a custom path to your generated API please follow the example below:

.. code-block::

   pythonrest generate --mysql-connection-string <mysql_connection_string> --result-path C:\<YOUR_DESIRED_PATH_HERE>

The command above will generate your API on the provided path, and if the folder does not exist the generator will create i. The following folders/files will be modified(content deleted and recreated) if a PythonREST project is already in place:

* src/c_Domain
* src/a_Presentation/a_Domain
* src/b_Application/b_Service/a_Domain
* src/d_Repository/a_Domain
* src/a_Presentation/d_Swagger
* src/e_Infra/b_Builders/a_Swagger
* src/e_Infra/d_Validators/a_Domain
* src/e_Infra/g_Environment
* src/e_Infra/b_Builders/FlaskBuilder.py
* config
* app.py This allows you to make customizations or enhancements on your generated API and new upgrades will only affect CRUD API feature folders

Disclaimer
^^^^^^^^^^

Keep in mind that the provided folder will have all of its files deleted before generating the API, except when a PythonREST project is already in place

\*\*--use-pascal-case\*\*:
This option creates the Python Domain Classes with PascalCase pattern for their names, if this option is provided as --no-use-pascal-case, you will be prompted to provide a name of python class for each table of your database:

.. code-block::

   pythonrest generate --mysql-connection-string <MYSQL_CONNECTION_STRING> --no-use-pascal-case

\*\*--us-datetime\*\*:
If you have a database with datetime formatted to the us pattern of mm-dd-yyyy, you can use this option so that the api will also respect that pattern when validating requests and responses:

.. code-block::

   pythonrest generate --mysql-connection-string <MYSQL_CONNECTION_STRING> --us-datetime

This behavior can be modified on the project's environment variables file(src/e_Infra/g_Environment/EnvironmentVariables.py), modifying the date_valid_masks variable. Some valid values are(more options and details on the API Environment Variables section below):

* "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y" -> This value accepts dates on YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD and DD/MM/YYYY formats
* "%Y-%m-%d, %m-%d-%Y, %Y/%m/%d, %m/%d/%Y" -> This value accepts dates on YYYY-DD-MM, MM-DD-YYYY, YYYY/DD/MM and MM/DD/YYYY formats

Generated API Usage
-------------------

After generating your API, you may open it on your preferred IDE(VSCode, PyCharm, etc) or even the bash/cmd if you wish to, from there you may build your venv like below to run the project.

How to Run with venv (Python virtual environment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project was initially built to run using a Python virtual environment, below we'll provide how to install the virtual environment and run the project on different systems:

Windows(CMD/Powershell)
^^^^^^^^^^^^^^^^^^^^^^^

1. Create the venv First of all, you should open this project on your terminal, from now on all the commands will be run from the root folder of the project. Below is the command to create a python venv:

.. code-block::
   
   python -m venv venv

2. Activate the virtual environment The below command is how to activate your venv for use on your current terminal session:

.. code-block::

   .\venv\Scripts\activate

The command above works fine for CMD or Powershell. If you are using GitBash to run these commands, the only change would be running the below command instead of the above one:

.. code-block::

   source venv/Scripts/activate


3. Install required libraries for API to run This project needs a number of libraries stored on PyPi to run, these are all listed on the requirements.txt file on the root folder of the generated project and to be installed you run the below command:

.. code-block::
   
   pip install -r requirements.txt

4. Run app.py After the libraries installation is complete, you can use the below command to run the project:

.. code-block::

   python app.py

From there you can access the URL localhost:5000, which is the base endpoint to go to the project routes and make requests following the API Usage Examples section on this readme, our `blog <https://medium.com/@seventechnologiescloud/>`_ and our documentation here at `readthedocs <https://readthedocs.org/projects/pythonrest/>`_

Linux/Mac(Bash/Zsh)
^^^^^^^^^^^^^^^^^^^

1. Create the venv: On Debian/Ubuntu systems, you need to have the python3-venv package installed, which you can do with the following commands:

.. code-block::

   apt-get update
   apt install python3.8-venv

And then you can create the venv with the following:

.. code-block::

   python3 -m venv venv

2. Activate the virtual environment The below command is how to activate your venv for use on your current terminal session:

.. code-block::
   
   source venv/bin/activate

3. Install required libraries for API to run This project needs a number of libraries stored on PyPi to run, these are all listed on the requirements.txt file on the root folder of the generated project and to be installed you run the below command:

.. code-block::
   
   pip install -r requirements.txt

4. Run app.py After the libraries installation is complete, you can use the below command to run the project:

.. code-block::
   
   python app.py

From there you can access the URL localhost:5000, which is the base endpoint to go to the project routes and make requests following the API Usage Examples section on this readme, our `blog <https://medium.com/@seventechnologiescloud/>`_ and our documentation here at `readthedocs <https://readthedocs.org/projects/pythonrest/>`_

Run and Debug using venv with VSCode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to go deep and debug the API, or simply wishes to run from VSCode Python extension, you'll want to configure a launch.json file for the API, to do that you'll go to the top bar of VSCode -> Run(if run is not visible, you may find it in the "..." on the title bar) -> Add Configuration. Doing that will generate your launch.json, in which you'll want to add a "python" key, similar to the example below:

.. code-block::
   
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

API Usage Examples
~~~~~~~~~~~~~~~~~~

After following the How to run section to its final steps, with your project running you can finally test the routes it creates, to follow the below examples, if you have a table named user, you would want to access localhost:5000/swagger/user to check the routes provided to that table.

Select All Table Entries
^^^^^^^^^^^^^^^^^^^^^^^^

Starting with a basic use, you go to your swagger/, the first route is the get one, if you just hit "try it out" and then "execute", it will present you with a response equivalent to a SELECT * from query. If you wish to, you can use the available filters to select only the attributes that you want to retrieve, limit the number of results, paginate your results and so on. If you still did not have anything on your database to retrieve, it will just be an empty list, now we can get to our next use case to solve that!

.. image:: https://camo.githubusercontent.com/d57632c63ee303fd01c0b13acfd5a12e55297590fff6adbed26a608b78c30299/68747470733a2f2f6c68332e676f6f676c6575736572636f6e74656e742e636f6d2f752f312f64726976652d7669657765722f4145596d425952784c3868556766656e634d6c4e6a57333548503766785f5a766c68654a5575506a656643697347684475365678453248557439614f465369424d4f5370595865384a354b4b5a5a474e3530564e7438566f6c65457a5f4746773d77323838302d6831343034
    :alt: Swagger Select all Users

Insert Table Entry
^^^^^^^^^^^^^^^^^^

From the same swagger page we were in, the next route is the post /, in which when you hit "try it out" it will present you with a sample JSON body to insert an entry on your table. The JSON body sent on the request is a list, so if you wish to you can provide multiple entries at once on table with the same request, below is an example of a request inserting three entries on a simple pre-designed USER table with 'id_user', 'username' and 'date_joined' fields:

.. image:: https://camo.githubusercontent.com/df1e76abe34b8dc8f519e269af177c549f3ecb12aa573dad33b00653578a92b6/68747470733a2f2f6c68332e676f6f676c6575736572636f6e74656e742e636f6d2f752f312f64726976652d7669657765722f4145596d4259534b4b566d50533543485f4f4341626f6e6f565f444a626a58713249533577477836512d4350416e346449374a6f32572d326b7831393345356c4f6733565372506d4652747a5f31473873596c643868556a54364a756167516a6b513d77323838302d6831343034
    :alt: Swagger Insert User

Example JSON payload:
++++++++++++++++++++

.. code-block::

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


Delete Table Entry
^^^^^^^^^^^^^^^^^^

Now we're talking about the delete /user route, if you hit "try it out" it will also present you with a sample JSON body of a generic object of your table, you can then use that example, modify its values to suit an entry that exists on your database. Note that this is a delete by full match route, so you need to provide the correct values for all of the table collumns on your response, below is an example of JSON body to delete a user table entry that has 3 columns: id_user, username and date_joined:

.. image:: https://camo.githubusercontent.com/7cba8acd0c934b1b67850241197d7522218b5a576c4060af60a95e4f8623fb91/68747470733a2f2f6c68332e676f6f676c6575736572636f6e74656e742e636f6d2f752f312f64726976652d7669657765722f4145596d42595469313165724a666b6e494d6762305232617579616e78645f6733346b6b6f56634e59586653354b637432305352422d6473714f6937704d524739554758565f68416169474f47764c6636434d384c514f78564d44656471474658773d77323838302d6831343034
    :alt: Swagger Delete User

.. code-block::

   [
     {
       "id_user": 2,
       "username": "user2",
       "date_joined": "2000-01-01 12:00:00"
     }
   ]


For more detailed examples, please check our `blog <https://medium.com/@seventechnologiescloud/>`_

Swagger Overview
----------------

When running the API, it will provide you with a localhost url, then you have the following swagger pages accessible:

/swagger
~~~~~~~~

That's the base route for viewing swagger, it contains the documentation of the SQL routes present on the application

.. image:: https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYR_dUffHUELqs1yay5iiqu0ltnAtbLqtPgjwjpsHv5IRhCRfZuhv0B5qVvPG5ZHm0ThT08xu99zsZuCRMblvjuFSasp=w2880-h1508
    :alt: Swagger Main Screen

/swagger/tablename
~~~~~~~~~~~~~~~~~~

For each table on your database, PythonREST creates an openapi page documentation for it, in which you can make your database queries targetting each table. To access them, simply append to the swagger endpoint url your table name in *flatcase* (**ALL WORDS TOGETHER IN LOWER CASE WITH NO SEPARATORS**).

.. image:: https://lh3.googleusercontent.com/u/1/drive-viewer/AEYmBYRfUGgCAiU0KSLZJjLGttaIuBCf5vRNWa8ioShBm7KQtm_EkwwLSHiW-G2hZbi-25SH-x_HtkLKjizLfxafbYMnJ-D0uA=w2880-h1508
    :alt: Swagger User Screen

Postman/cURL
------------

If you're familiar with Postman or using cURL requests directly, you can make requests to the routes shown in the open api specification, using the examples of usage present on it to build your request.
For example, a table user with id_user, username and date_joined fields would have a POST cURL request like:

.. code-block::

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

API Environment Variables
-------------------------

Generated API environment variables can be found on src/e_Infra/g_Environment/EnvironmentVariables.py and each one has the following utility:
* \*\*domain_like_left\*\* – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "%COLUMN_VALUE" search behavior whenever it's value is defined on a query parameter.
Example:
    * Test
    * 1Test
    * NameTest
    * Example-Test

* \*\*domain_like_right\*\* – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "COLUMN_VALUE%" search behavior whenever it's value is defined on a query parameter.
Example:
    * Test
    * Test1
    * Test Name
    * Test-Example

* \*\*domain_like_full\*\* – Defines SQL's "LIKE" operator's behavior in relation to specified table columns. Columns defined here will have "%COLUMN_VALUE%" search behavior whenever a it's value is defined on a query parameter.
Example:
    * Test
    * Test1
    * TestName
    * Test-Example
    * 1Test
    * NameTest
    * Example-Test

* \*\*date_valid_masks\*\* – Specifies the date formats accepted by the API. Valid values are:
    * "%Y-%m-%d" - This value accepts dates on YYYY-MM-DD format
    * "%d-%m-%Y" - This value accepts dates on DD-MM-YYYY format
    * "%Y/%m/%d" - This value accepts dates on YYYY/MM/DD format
    * "%d/%m/%Y" - This value accepts dates on DD/MM/YYYY format
    * "%m-%d-%Y" - This value accepts dates on MM-DD-YYYY format
    * "%m/%d/%Y" - This value accepts dates on MM/DD/YYYY format
    Your end result can be a combination of two or more of the previous options, like the following examples:
    * "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y" This value accepts dates on YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD and DD/MM/YYYY formats(default API generation behavior with us-datetimes set to false)
    * "%Y-%m-%d, %m-%d-%Y, %Y/%m/%d, %m/%d/%Y" This value accepts dates on YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD and MM/DD/YYYY formats(default API generation behavior with us-datetimes set to true)

    ⚠️ Disclaimer
    The previous behavior affects all fields from all database tables, is is not possible at this point to specify these rules for specific table columns

* \*\*time_valid_masks\*\* – Specifies the time formats accepted by the API. Valid values are:
    * "%H:%M:%S" This value accepts times on HH:MM:SS format
    * "%I:%M:%S %p" This value accepts times on HH:MM:SS AM/PM format 
    * "%H:%M" This value accepts times on HH:MM format
    * "%I:%M %p" This value accepts times on HH:MM AM/PM format
    * "%I:%M:%S%p" This value accepts times on HH:MM:SSAM/PM format
    * "%I:%M%p" This value accepts times on HH:MMAM/PM format
    Your end result can be a combination of two or more of the previous options, like the following example(default API generation behavior):
    * "%H:%M:%S, %I:%M:%S %p, %H:%M, %I:%M %p, %I:%M:%S%p, %I:%M%p"

    ⚠️ Disclaimer
    The previous behavior affects all fields from all database tables, is is not possible at this point to specify these rules for specific table columns

* \*\*query_limit\*\* – Global result limiting of GET requests CRUD routes can return. Default value '*' means your CRUD GET requests won't have a maximum limit and will retrieve all data from a specified query even if your pagination or query limit parameters are not set. Valid values are any integer natural numbers (greater than 0) or '*'

* \*\*display_stacktrace_on_error\*\* – When enabled, the original Python exception appears in the JSON response when an error occurs in the request. Valid values are "True" or "False"

* \*\*origins\*\* – Defines allowed CORS origins, separated by comma.

* \*\*headers\*\* – Defines allowed CORS origins headers values, separated by comma.

* main_db_conn - Specifies the database type (mysql, pgsql, mssql, mariadb) of the database your custom API accesses. Should not be messed around to avoid breaking the code. Valid values are: mysql, pgsql, mssql and mariadb

* <PROJECT_DATABASE_TYPE>_user - User to authenticate on API's database sessions.

* <PROJECT_DATABASE_TYPE>_password - Password to authenticate on API's database sessions.

* <PROJECT_DATABASE_TYPE>_host - The endpoint of your database.

* <PROJECT_DATABASE_TYPE>_port - Port that is allowed access to your database.

* <PROJECT_DATABASE_TYPE>_schema - On MySQL, MariaDB and SQLServer, this is the name of your database. On PostgreSQL, this is the schema inside of your database.

* pgsql_database_name - On PostgreSQL, this is the database name in which your selected schema resides.

Generated API Directory Structure
---------------------------------

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

Requirements
~~~~~~~~~~~~

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

Windows
^^^^^^^

.. code-block::

   pip install -r requirements.txt


Linux/Mac
^^^^^^^^^

.. code-block::

   sudo pip install -r requirements.txt


For Contributors: How to Build Your Own Binaries and Installers
---------------------------------------------------------------

Windows
~~~~~~~

Building the CLI exe
^^^^^^^^^^^^^^^^^^^^

Run from the root folder:

.. code-block::

   pyinstaller --onefile
       --add-data "pythonrest.py;."
       --add-data "databaseconnector;databaseconnector"
       --add-data 'domaingenerator;domaingenerator'
       --add-data 'apigenerator;apigenerator'
       --collect-submodules typing
       --collect-submodules re
       --collect-submodules typer
       --collect-submodules yaml
       --collect-submodules parse
       --collect-submodules mergedeep
       --collect-submodules site
       --collect-submodules pymysql
       --collect-submodules psycopg2
       --collect-submodules psycopg2-binary
       --collect-submodules pymssql
       --icon=pythonrestlogo.ico
       pythonrest.py

it will generate a dist folder with the pythonrest.exe file 

Known Issues:
When using pyinstaller with typing installed it generates the following error:

.. code-block::

   The 'typing' package is an obsolete backport of a standard library package and is incompatible with PyInstaller. Please remove this package

Just removing the package and retrying fixes that error.

Building the Installer exe
^^^^^^^^^^^^^^^^^^^^^^^^^^

Move the pythonrest.exe file from the generated dist/ folder to the windowsinstaller/ folder and run from the latter folder:

.. code-block::

   pyinstaller ^
   --onefile ^
   --add-data "pythonrest.exe;."
   --add-data "install_pythonrest.py;."
   --add-data "addpythonresttouserpath.ps1;."
   --icon=../pythonrestlogo.ico
   --name PythonRESTInstaller install_pythonrest.py

Building the Uninstaller exe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run from the windowsinstaller folder:

.. code-block::

   pyinstaller
   --onefile
   --add-data "uninstall_pythonrest.py;."
   --add-data "removepythonrestfromuserpath.ps1;."
   --icon=../pythonrestlogo.ico
   --name PythonRESTUninstaller uninstall_pythonrest.py

Build exe, installer and uninstaller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

run from windowsinstaller/ folder:

.. code-block::

   .\generate_pythonrest_executables.ps1

This will take care of running the above pyinstaller commands and it will generate both installer and uninstaller 
executables on PythonRestExecutables/ directory, which you can then run to install and/or uninstall the cli on your
machine.

Linux/Mac
~~~~~~~~~

Building the CLI binary
^^^^^^^^^^^^^^^^^^^^^^^

Run from the root folder:

.. code-block::

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


it will generate a dist folder with the pythonrest file 

Known Issues:
When using pyinstaller with typing installed it generates the following error:

.. code-block::

   The 'typing' package is an obsolete backport of a standard library package and is incompatible with PyInstaller. Please remove this package

Just removing the package and retrying fixes that error.

Building the Installer binary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Move the pythonrest file from the generated dist/ folder to the linuxinstaller/ or macinstaller/ folder and run from it:

.. code-block::

   pyinstaller \
       --onefile \
       --add-data "pythonrest:." \
       --add-data "install_pythonrest.py:." \
       --add-data "addpythonresttouserpath.sh:." \
       --name PythonRESTInstaller install_pythonrest.py


Building the Uninstaller binary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run from the linuxinstaller/ or macinstaller/ folder:

.. code-block::

   pyinstaller \
       --onefile \
       --add-data "uninstall_pythonrest.py:." \
       --add-data "removepythonrestfromuserpath.sh:." \
       --name PythonRESTUninstaller uninstall_pythonrest.py

Build pythonrest, installer and uninstaller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Go to linuxinstaller/ or macinstaller/ folder and from it add execute permission on the script:

.. code-block::

   chmod +x ./generate_pythonrest_executables.sh


Execute the script:

.. code-block::

   ./generate_pythonrest_executables.sh

This will take care of running the above pyinstaller commands, and it will generate both installer and uninstaller 
binaries on PythonRestExecutables/ directory, which you can then run to install and/or uninstall the cli on your
machine, like below:

.. code-block::

   ./PythonRESTInstaller
   ./PythonRESTUninstaller

Known Issues:
When executing ./generate_pythonrest_executables.sh, there is a possibility that something like this issue occurs:

.. code-block::

   ./generate_pythonrest_executables.sh: line 2: $'\r': command not found                                                   
   ./generate_pythonrest_executables.sh: line 3: syntax error near unexpected token `$'{\r''                                
   '/generate_pythonrest_executables.sh: line 3: `function write_log() {   

That issue is due to a difference in line endings between Windows (CRLF - Carriage Return and Line Feed) and Linux/Unix
(LF - Line Feed) systems. When you transfer or use scripts created on Windows in a Linux environment, these line ending 
characters can cause issues. To fix it you can install and run dos2unix in all of the sh files of the linuxinstaller
folder:

.. code-block::

   sudo apt-get update
   sudo apt-get install dos2unix
   dos2unix generate_pythonrest_executables.sh
   dos2unix addpythonresttouserpath.sh
   dos2unix removepythonrestfromuserpath.sh


Build and install pythonrest local pip package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run from the root folder:

.. code-block::

   pip install .

This will use the setup.py from the root folder to build a library of the pythonrest on the site-packages
of the Python folder.
One thing worth noting is that if you need to add a new folder to the project, e.g. apigenerator/c_NewFolder
you need to add a new entry to the list of the packages property in the setup.py, like this:

.. code-block::

   'pythonrest.apigenerator.c_NewFolder',

And if that folder has files that are not of .py extension, e.g. apigenerator/c_NewFolder/new.yaml and 
apigenerator/c_NewFolder/new2.yaml, you need to add a new entry to the list of the package_data property in the 
setup.py, like this:

.. code-block::

   'pythonrest.apigenerator.c_NewFolder': ['new.yaml', 'new2.yaml'],

All of this must be done to successfully add those files to the pip generated and installed library
To uninstall the local pip package, you can just use a common pip uninstall command:

.. code-block::

   pip uninstall pythonrest

When reinstalling the local pip package for tests, make sure to delete the build folder generated on the root folder of the project,
as retaining that folder can lead to the project being built using that folder and not catching any changes you made to
the project files.

.. note::

   * If you find our solution helpful, consider donating on our `Patreon campaign <https://www.patreon.com/seventechnologiescloud>`_!
   * Thank you for riding with us! Feel free to use and contribute to our project. PythonREST CLI Tool generates a COMPLETE API for a relational database based on a connection string. It reduces your API development time by 40-60% and it's OPEN SOURCE!
   * Don't forget to star rate `our repo <https://github.com/seven-technologies-cloud/pythonrest>`_ if you like our job!