from src.e_Infra.b_Builders.FlaskBuilder import *


# Methods to create main Redoc docs #
@redoc_blueprint.route('/redoc')
def redoc():
    redoc_spec_url = '/redoc/spec'
    return render_template('redoc.html', spec_url=redoc_spec_url)


@redoc_blueprint.route('/redoc/spec')
def spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'swagger.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content