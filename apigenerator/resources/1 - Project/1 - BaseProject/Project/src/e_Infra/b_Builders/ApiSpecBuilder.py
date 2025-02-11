# Method that contains the Swagger html definition used on the Flask render template #
def build_swagger_html(api_title, swagger_json):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{api_title}</title>
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.1.0/swagger-ui.min.css">
        <style>
            .servers {{
                display: none !important;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.1.0/swagger-ui-bundle.min.js"></script>
        <script>
            window.onload = function() {{
                const ui = SwaggerUIBundle({{
                    spec: {swagger_json},
                    dom_id: "#swagger-ui",
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                }});
            }};
        </script>
    </body>
    </html>
    """


# Method that contains the Redoc html definition used on the Flask render template #
def build_redoc_html(api_title, redoc_json):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{api_title}</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <div id="redoc-container"></div>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
        <script>
            window.onload = function() {{
                Redoc.init({redoc_json}, {{
                    hideDownloadButton: true  
                }}, document.getElementById('redoc-container'));
            }};
        </script>
    </body>
    </html>
    """
