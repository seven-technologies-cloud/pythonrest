# System imports #
import json
import yaml

# Infra Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *
from src.e_Infra.b_Builders.ApiSpecBuilder import build_redoc_html


# /redoc route #
@app_handler.route('/redoc', methods=['GET'])
def redoc_ui():
    with open("config/swagger.yaml", "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    api_title = data.get("info", {}).get("title")

    redoc_json = json.dumps(data)

    return render_template_string(build_redoc_html(api_title, redoc_json)), 200, {'Content-Type': 'text/html'}
