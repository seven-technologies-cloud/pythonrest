import os
from src.e_Infra.b_Builders.FlaskBuilder import *

# Method to build main Redoc Blueprint #
@redoc_blueprint.route('/redoc')
def spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'swagger.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content