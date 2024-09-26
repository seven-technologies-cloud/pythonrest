
# Methods to build declarative_meta Redoc docs #
@redoc_blueprint.route('/redoc/meta_string')
def meta_string_redoc():
    redoc_spec_url = '/redoc/spec/meta_string'
    return render_template('redoc.html', spec_url=redoc_spec_url)


@redoc_blueprint.route('/redoc/spec/meta_string')
def meta_string_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'declarative_meta.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content