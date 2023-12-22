

# /swaggerdata/meta_string route #
@app_handler.route('/swaggerdata/meta_string', methods=['GET'])
def swagger_route_meta_string():
    # Routing request to /meta_string GET method #
    if request.method == 'GET':

        yaml_file = open("config/declarative_meta.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}
