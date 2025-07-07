from flask import Blueprint, request, jsonify, current_app
import logging

# Assuming CustomVariables are directly importable from src.e_Infra
# Adjust the import path if your project structure resolves it differently at runtime
from src.e_Infra.CustomVariables import OPENAPI_SPEC_PATH # GEMINI_API_KEY is no longer directly used here
from src.e_Infra.j_LlmManager.LlmServiceFactory import LlmServiceFactory
from src.e_Infra.j_LlmManager.LlmServiceBase import LlmServiceBase # For type hinting if needed
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
        try:
            # LlmServiceFactory will check for LLM_PROVIDER and relevant API key
            llm_service_instance = LlmServiceFactory.get_llm_service()
            if llm_service_instance.check_connection():
                logger.info(f"Healthcheck: {type(llm_service_instance).__name__} connection successful.")
                return jsonify({"answer": "yes", "provider": type(llm_service_instance).__name__}), 200
            else:
                logger.warn(f"Healthcheck: {type(llm_service_instance).__name__} API connection test failed.")
                return jsonify({"answer": "no", "reason": f"{type(llm_service_instance).__name__} API connection test failed"}), 200
        except ValueError as ve: # Catch configuration errors from LlmServiceFactory or service init
            logger.error(f"Healthcheck: Configuration error: {ve}", exc_info=True)
            # Return 200 as per original healthcheck spec, but indicate error in body
            return jsonify({"answer": "no", "reason": f"Configuration error: {ve}"}), 200
        except RuntimeError as re: # Catch runtime errors from service init or check_connection
            logger.error(f"Healthcheck: Runtime error with LLM service: {re}", exc_info=True)
            return jsonify({"answer": "no", "reason": f"Runtime error with LLM service: {re}"}), 200
        except Exception as e: # Catch-all for unexpected errors
            logger.error(f"Healthcheck: Unexpected error: {e}", exc_info=True)
            return jsonify({"answer": "no", "reason": f"An unexpected error occurred during healthcheck: {e}"}), 200

    # --- Standard Question Logic ---
    llm_service_instance: LlmServiceBase
    try:
        llm_service_instance = LlmServiceFactory.get_llm_service()
    except ValueError as ve: # Configuration error from factory
        logger.error(f"LLM Service configuration error: {ve}", exc_info=True)
        return jsonify({"error": f"LLM Service not configured correctly: {ve}"}), 503 # Service Unavailable
    except RuntimeError as re: # Service initialization error
        logger.error(f"LLM Service runtime error during initialization: {re}", exc_info=True)
        return jsonify({"error": f"LLM Service initialization failed: {re}"}), 503
    except Exception as e: # Other unexpected errors from factory
        logger.error(f"Unexpected error getting LLM service: {e}", exc_info=True)
        return jsonify({"error": f"Unexpected error configuring LLM service: {e}"}), 500


    if not OPENAPI_SPEC_PATH: # Though it has a default in CustomVariables
        logger.error("Cannot answer question: OPENAPI_SPEC_PATH not configured.")
        # This check might be redundant if CustomVariables always provides a default.
        return jsonify({"error": "Service not configured: Missing OpenAPI spec path"}), 503

    try:
        # ApiQueryService now takes the generic llm_service_instance
        api_query_service = ApiQueryService(
            llm_service=llm_service_instance,
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
