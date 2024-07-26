
# Method to build declarative_meta Redoc Blueprint #
@redoc_blueprint.route('/spec')
def meta_string_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'declarative_meta.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content