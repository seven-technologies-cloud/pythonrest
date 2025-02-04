# Method that contains the Swagger html definition used on the Flask render template #
def build_swagger_html(api_title, swagger_json):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{api_title}</title>
        <link rel="stylesheet" type="text/css" 
              href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.1.0/swagger-ui.min.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.1.0/swagger-ui-bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.1.0/swagger-ui-standalone-preset.min.js"></script>
        <script>
            window.onload = function() {{
                const ui = SwaggerUIBundle({{
                    spec: {swagger_json},
                    dom_id: "#swagger-ui",
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    layout: "StandaloneLayout"
                }});
            }};
        </script>
    </body>
    </html>
    """