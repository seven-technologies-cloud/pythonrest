from flask import request, jsonify, current_app
from pythonrest.apigenerator.resources.app.api.ask import bp # Or app.api.ask if structure changes
from pythonrest.apigenerator.resources.app.mcp_module.client import MCPClient # Or app.mcp_module.client

# TODO: Determine the correct path for swagger_spec_path
# This might come from app.config or be a fixed relative path
# once the API generation process is known.
# For now, using a placeholder.
DEFAULT_SWAGGER_SPEC_PATH = "swagger.yaml" # Or openapi.yaml

@bp.route('/ask', methods=['POST'])
def ask_mcp():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question' in request payload"}), 400

    question = data['question']

    gemini_api_key = current_app.config.get('GEMINI_API_KEY')

    if question == "healthcheck":
        if not gemini_api_key:
            current_app.logger.warn("Healthcheck failed: GEMINI_API_KEY not configured.")
            return jsonify({"answer": "no", "reason": "GEMINI_API_KEY not configured"}), 200 # Or 503 Service Unavailable

        # For healthcheck, swagger_spec_path might not be strictly necessary for MCPClient
        # if check_gemini_connection doesn't use it, but MCPClient constructor requires it.
        # Using a default or configured path.
        swagger_spec_path = current_app.config.get('SWAGGER_SPEC_PATH', DEFAULT_SWAGGER_SPEC_PATH)
        try:
            # We need to instantiate the client to test its connection,
            # even if the spec path isn't strictly used by check_gemini_connection.
            # The MCPClient's __init__ might raise ValueError if api_key is None, but we checked above.
            mcp_client_health_check = MCPClient(api_key=gemini_api_key, swagger_spec_path=swagger_spec_path)
            if mcp_client_health_check.check_gemini_connection():
                return jsonify({"answer": "yes"}), 200
            else:
                current_app.logger.warn("Healthcheck failed: Gemini API connection test failed.")
                return jsonify({"answer": "no", "reason": "Gemini API connection test failed"}), 200 # Or 503
        except ValueError as ve: # Catch init errors like missing spec path if MCPClient evolves
            current_app.logger.error(f"Healthcheck MCPClient initialization error: {ve}")
            return jsonify({"answer": "no", "reason": f"MCPClient initialization error: {ve}"}), 200 # Or 500
        except Exception as e:
            current_app.logger.error(f"Healthcheck unexpected error: {e}", exc_info=True)
            return jsonify({"answer": "no", "reason": "Unexpected error during healthcheck"}), 200 # Or 500
    else:
        # Regular question processing
        if not gemini_api_key:
            current_app.logger.error("GEMINI_API_KEY not configured for a non-healthcheck question.")
            return jsonify({"error": "Server configuration error: Missing Gemini API Key"}), 500

        swagger_spec_path = current_app.config.get('SWAGGER_SPEC_PATH', DEFAULT_SWAGGER_SPEC_PATH)
        # In a real generated app, ensure this path is correct.
        # For development/template, it might point to a default or example spec.
        # Consider adding a check here if the file exists, though MCPClient also does a basic check.
        # if not os.path.exists(swagger_spec_path):
        #     current_app.logger.error(f"Swagger spec file not found at {swagger_spec_path}")
        #     return jsonify({"error": "Server configuration error: Swagger spec not found"}), 500
        try:
            mcp_client = MCPClient(api_key=gemini_api_key, swagger_spec_path=swagger_spec_path)
            answer = mcp_client.ask_question(question)
            return jsonify({"answer": answer})
        except ValueError as ve: # Catch initialization errors from MCPClient
            current_app.logger.error(f"MCPClient initialization error: {ve}")
            return jsonify({"error": f"MCPClient error: {ve}"}), 500
    except Exception as e:
        current_app.logger.error(f"Error during MCP query: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred processing your question."}), 500

# Note: The import paths like 'pythonrest.apigenerator.resources.app.api.ask'
# are based on the assumption that the 'pythonrest/apigenerator/resources/' directory
# will be part of the PYTHONPATH or the project root when the generated app runs.
# If the generation process alters the structure or how it's added to sys.path,
# these imports might need to be relative, e.g., 'from ..mcp_module.client import MCPClient'.
# For a template, absolute paths assuming a certain root are common.
