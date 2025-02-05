# System imports #
import json
import yaml

# Infra Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *
from src.e_Infra.b_Builders.ApiSpecBuilder import build_swagger_html


# /swagger route #
@app_handler.route('/swagger', methods=['GET'])
def swagger_ui():
    with open("config/swagger.yaml", "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    api_title = data.get("info", {}).get("title")

    data['servers'] = [{"url": ''}]
    swagger_json = json.dumps(data)

    return render_template_string(build_swagger_html(api_title, swagger_json)), 200, {'Content-Type': 'text/html'}
