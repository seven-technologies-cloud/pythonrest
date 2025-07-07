from flask import Blueprint, request, jsonify, current_app
import logging

# Assuming CustomVariables are directly importable from src.e_Infra
# Adjust the import path if your project structure resolves it differently at runtime
from src.e_Infra.CustomVariables import GEMINI_API_KEY, OPENAPI_SPEC_PATH
from src.e_Infra.g_GeminiClient.GeminiService import GeminiService
from src.b_Application.b_Service.c_McpService.ApiQueryService import ApiQueryService

# Configure logging for this module
logger = logging.getLogger(__name__)

# Define the Blueprint
# The URL prefix can be defined here or when registering the blueprint in app.py
# For example, if registered with url_prefix='/mcp', this route '/ask' becomes '/mcp/ask'
ask_bp = Blueprint('ask_bp', __name__)

@ask_bp.route('/ask', methods=['POST'])
def ask_api_question():
    """
    Handles natural language questions about the API.
    Also provides a healthcheck for the Gemini API connection.
    """
    data = request.get_json()
    if not data or 'question' not in data:
        logger.warn("'/ask' endpoint called with missing 'question' in payload.")
        return jsonify({"error": "Missing 'question' in request payload"}), 400

    question = data['question']

    # --- Healthcheck Logic ---
    if question.lower() == "healthcheck":
        if not GEMINI_API_KEY:
            logger.info("Healthcheck: GEMINI_API_KEY not configured.")
            return jsonify({"answer": "no", "reason": "GEMINI_API_KEY not configured"}), 200

        try:
            gemini_service = GeminiService(api_key=GEMINI_API_KEY)
            if gemini_service.check_connection():
                logger.info("Healthcheck: Gemini connection successful.")
                return jsonify({"answer": "yes"}), 200
            else:
                logger.warn("Healthcheck: Gemini API connection test failed.")
                return jsonify({"answer": "no", "reason": "Gemini API connection test failed"}), 200
        except ValueError as ve: # Catch GeminiService init errors (e.g. empty API key)
            logger.error(f"Healthcheck: Error initializing GeminiService: {ve}", exc_info=True)
            return jsonify({"answer": "no", "reason": f"Error initializing Gemini client: {ve}"}), 200
        except RuntimeError as re: # Catch GeminiService init or connection errors
            logger.error(f"Healthcheck: Runtime error with GeminiService: {re}", exc_info=True)
            return jsonify({"answer": "no", "reason": f"Runtime error with Gemini client: {re}"}), 200
        except Exception as e:
            logger.error(f"Healthcheck: Unexpected error: {e}", exc_info=True)
            return jsonify({"answer": "no", "reason": f"An unexpected error occurred during healthcheck: {e}"}), 200

    # --- Standard Question Logic ---
    if not GEMINI_API_KEY:
        logger.error("Cannot answer question: GEMINI_API_KEY not configured.")
        return jsonify({"error": "Service not configured: Missing API Key"}), 503 # 503 Service Unavailable

    if not OPENAPI_SPEC_PATH: # Though it has a default in CustomVariables
        logger.error("Cannot answer question: OPENAPI_SPEC_PATH not configured.")
        return jsonify({"error": "Service not configured: Missing OpenAPI spec path"}), 503

    try:
        gemini_service = GeminiService(api_key=GEMINI_API_KEY)
        # Consider how often ApiQueryService is instantiated.
        # If spec parsing is expensive and file doesn't change often,
        # you might cache ApiQueryService instance or its parsed spec.
        # For now, instantiating per request for simplicity in a template.
        api_query_service = ApiQueryService(
            gemini_service=gemini_service,
            openapi_spec_path=OPENAPI_SPEC_PATH
        )

        answer = api_query_service.answer_api_question(question)
        return jsonify({"answer": answer}), 200

    except FileNotFoundError as fnfe:
        logger.error(f"OpenAPI spec file not found: {fnfe}", exc_info=True)
        return jsonify({"error": f"API Specification file not found at {OPENAPI_SPEC_PATH}. Please configure the path correctly."}), 503
    except ValueError as ve: # Could be from GeminiService init or ApiQueryService
        logger.error(f"Configuration or input error: {ve}", exc_info=True)
        return jsonify({"error": f"Invalid configuration or input: {ve}"}), 400 # Or 500 if server config issue
    except RuntimeError as re: # Errors from GeminiService or ApiQueryService during operation
        logger.error(f"Service runtime error: {re}", exc_info=True)
        return jsonify({"error": f"An error occurred while processing your question: {re}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in /ask endpoint: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred."}), 500

# Note on imports:
# The paths like `from src.e_Infra.CustomVariables ...` assume that when the Flask app runs,
# the 'src' directory (or its parent 'Project') is in PYTHONPATH or recognized as the root package.
# This is a common setup for Flask projects structured this way.
# If issues arise at runtime, these import paths might need adjustment based on how the
# generated app's execution environment is configured.
