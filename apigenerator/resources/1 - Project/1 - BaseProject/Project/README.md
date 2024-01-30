# PythonREST API

## How to Run with venv (Python virtual environment)
This project was initially built to run using a Python virtual environment, below we'll provide you a full installation guide to run your API on any OS:
## Windows(CMD/Powershell):
1. Creating VENV

    First of all, you should open this project on your terminal and run the following commands on the root folder of your project.
Below is the command to create a python venv:
    ```commandline
    python -m venv venv
    ```
2. Activating your Virtual Environment

    Run the command below to activate your venv on your current terminal session:
    ```commandline
    .\venv\Scripts\activate
    ```
    The above command works fine for CMD or Powershell. If you are using Git Bash to run these commands, run the following command:

      ```bash
      source venv/Scripts/activate
      ```

3. Install Required Libraries for Your API

    This project requires a number of libraries stored on PyPi to run, these are all listed under the requirements.txt file on the root folder of the generated project. To install them, run the command below:
      ```commandline
      pip install -r requirements.txt
      ```

4. Run app.py

    After completing libraries installation, you can use the below command to run the project:
    ```commandline
    python app.py
    ```
    From there you can access the URL localhost:5000, which is the base endpoint to go to the project routes and make requests following the **API Usage Examples** section on this readme, our [blog](https://medium.com/@seventechnologiescloud/) and documentation at[readthedocs](https://readthedocs.org/projects/pythonrest/) 

<br>

## Linux/Mac(Bash/Zsh):
1. Creating VENV:

    On Debian/Ubuntu systems, you need to have the python3-venv package installed, which you can do with the following commands:
    ```bash
    apt-get update
    apt install python3.8-venv
    ```
    Now you can create your venv with the following command:
    ```bash
    python3 -m venv venv
    ```

2. Activate Your Virtual Environment

    The below command is how to activate your venv for use on your current terminal session:
    ```bash
    source venv/bin/activate
    ```

3. Install required libraries for API to run

    This project requires a number of libraries stored on PyPi to run, these are all listed under the requirements.txt file on the root folder of the generated project. To install them, run the command below:
    ```bash
    pip install -r requirements.txt
    ```

4. Run app.py

    After the libraries installation is complete, you can use the command below to run the project:
    ```bash
    python app.py
    ```

    From there you can access the URL localhost:5000, which is the base endpoint to go to the project routes and make requests following the **API Usage Examples** section on this readme, our [blog](https://medium.com/@seventechnologiescloud/) and documentation at[readthedocs](https://readthedocs.org/projects/pythonrest/) 

<br>

## Run and Debug Using VENV on VSCode
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
For each table on your database, PythonREST creates an openapi page documentation for it, in which you can make your database queries targetting each table. To access them, simply append to the swagger endpoint url your table name in flatcase(all words together in lower case with no separators).
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