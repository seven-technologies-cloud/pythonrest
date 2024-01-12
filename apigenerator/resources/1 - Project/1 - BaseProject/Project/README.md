# PythonREST API

# How to Run

## venv run
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