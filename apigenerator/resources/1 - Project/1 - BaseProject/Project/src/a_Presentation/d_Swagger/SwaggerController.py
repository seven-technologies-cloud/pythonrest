# System imports #
import json
import yaml

# Flask Imports #
from flask import request
from src.e_Infra.b_Builders.FlaskBuilder import *


# /swaggerdata route #
@app_handler.route('/swaggerdata', methods=['GET'])
def swagger_route():
    # Routing request to /swaggerdata GET method #
    if request.method == 'GET':

        yaml_file = open("config/swagger.yaml")
        data = yaml.safe_load(yaml_file)

        try:
            stage = request.aws_stage_name
        except:
            stage = None
        data['servers'] = [{"url": "/" + stage}] if stage is not None else [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}
