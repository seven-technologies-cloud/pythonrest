

# /swagger/meta_string route #
@app_handler.route('/swagger/meta_string', methods=['GET'])
def swagger_ui_meta_string():
    with open("config/declarative_meta.yaml", "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    api_title = data.get("info", {}).get("title")

    data['servers'] = [{"url": ''}]
    swagger_json = json.dumps(data)

    return render_template_string(build_swagger_html(api_title, swagger_json)), 200, {'Content-Type': 'text/html'}
