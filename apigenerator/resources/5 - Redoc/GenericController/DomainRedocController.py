

# /redoc/meta_string route #
@app_handler.route('/redoc/meta_string', methods=['GET'])
def redoc_ui_meta_string():
    with open("config/declarative_meta.yaml", "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    api_title = data.get("info", {}).get("title")

    redoc_json = json.dumps(data)

    return render_template_string(build_redoc_html(api_title, redoc_json)), 200, {'Content-Type': 'text/html'}
