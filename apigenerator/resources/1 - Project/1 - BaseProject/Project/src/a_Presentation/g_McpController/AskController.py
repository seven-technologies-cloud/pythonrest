from flask import Blueprint, request, jsonify, current_app
import logging

# Assuming CustomVariables are directly importable from src.e_Infra
# Adjust the import path if your project structure resolves it differently at runtime
from src.e_Infra.CustomVariables import OPENAPI_SPEC_PATH
# LlmServiceFactory and LlmServiceBase are now re-exported by g_McpInfra's __init__
from src.e_Infra.g_McpInfra import LlmServiceFactory, LlmServiceBase
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
    # The healthcheck will test the provider determined by X-Provider header, or the configured default.
    if question.lower() == "healthcheck":
        x_provider_header = request.headers.get('X-Provider')
        provider_for_healthcheck = x_provider_header # Can be None

        try:
            # LlmServiceFactory will use header if present, then runtime config, then env default provider
            llm_service_instance = LlmServiceFactory.get_llm_service(x_provider_header=provider_for_healthcheck)
            provider_name_checked = type(llm_service_instance).__name__.replace("Service", "")

            if llm_service_instance.check_connection():
                logger.info(f"Healthcheck: {provider_name_checked} connection successful.")
                return jsonify({"answer": "yes", "provider_checked": provider_name_checked}), 200
            else:
                logger.warn(f"Healthcheck: {provider_name_checked} API connection test failed.")
                return jsonify({"answer": "no", "provider_checked": provider_name_checked, "reason": "API connection test failed"}), 200
        except ValueError as ve: # Catch configuration errors from LlmServiceFactory or service init
            logger.error(f"Healthcheck: Configuration error (Provider attempted: {provider_for_healthcheck or 'determined default'}): {ve}", exc_info=True)
            return jsonify({"answer": "no", "provider_attempted": provider_for_healthcheck or 'determined default', "reason": f"Configuration error: {ve}"}), 200
        except RuntimeError as re: # Catch runtime errors from service init or check_connection
            logger.error(f"Healthcheck: Runtime error with LLM service (Provider attempted: {provider_for_healthcheck or 'determined default'}): {re}", exc_info=True)
            return jsonify({"answer": "no", "provider_attempted": provider_for_healthcheck or 'determined default', "reason": f"Runtime error with LLM service: {re}"}), 200
        except Exception as e: # Catch-all for unexpected errors
            logger.error(f"Healthcheck: Unexpected error (Provider attempted: {provider_for_healthcheck or 'determined default'}): {e}", exc_info=True)
            return jsonify({"answer": "no", "provider_attempted": provider_for_healthcheck or 'determined default', "reason": f"An unexpected error: {e}"}), 200

    # --- Standard Question Logic ---
    x_provider_header = request.headers.get('X-Provider')
    llm_service_instance: LlmServiceBase
    try:
        # LlmServiceFactory handles X-Provider header, runtime config, and env defaults
        llm_service_instance = LlmServiceFactory.get_llm_service(x_provider_header=x_provider_header)
        logger.info(f"Using LLM provider: {type(llm_service_instance).__name__} for question.")
    except ValueError as ve: # Configuration error from factory
        logger.error(f"LLM Service configuration error (X-Provider: {x_provider_header}): {ve}", exc_info=True)
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


# --- Configuration Routes ---
# LlmConfigManager is now re-exported by g_McpInfra's __init__
from src.e_Infra.g_McpInfra import LlmConfigManager

# Note: No explicit security is added to these configuration endpoints as per user instruction.
# In a production environment, these should be appropriately secured.

@ask_bp.route('/ask/configure', methods=['GET'])
def get_llm_configuration():
    """
    Displays the effective current LLM configuration, merging runtime settings
    from llm_config.json with environment variable defaults.
    Does NOT display API keys.
    """
    try:
        manager = LlmConfigManager()
        effective_config = manager.get_effective_config()
        return jsonify(effective_config), 200
    except Exception as e:
        logger.error(f"Error getting LLM configuration: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve LLM configuration", "details": str(e)}), 500

@ask_bp.route('/ask/configure', methods=['POST'])
def set_llm_configuration():
    """
    Sets LLM runtime configurations.
    Payload can specify:
    - "set_runtime_default_provider": "provider_name" (e.g., "gemini", "openai", "anthropic")
    - "update_provider_settings": {
          "provider_name": { (e.g., "openai")
              "model": "model_string",
              "temperature": float_value
          }
      }
    - "clear_provider_settings": "provider_name"
    - "clear_all_runtime_settings": true
    API Keys are NOT configured here; they must be set as environment variables.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    manager = LlmConfigManager()
    actions_performed = []
    errors = []

    try:
        # Set runtime default provider
        if "set_runtime_default_provider" in data:
            provider_to_set_default = data["set_runtime_default_provider"]
            if provider_to_set_default is None or isinstance(provider_to_set_default, str):
                # Basic validation for known providers, could be stricter
                if provider_to_set_default and provider_to_set_default.lower() not in ["gemini", "openai", "anthropic", None]:
                     errors.append(f"Invalid provider name '{provider_to_set_default}' for default. Must be one of 'gemini', 'openai', 'anthropic' or null.")
                else:
                    manager.set_runtime_default_provider(provider_to_set_default)
                    actions_performed.append(f"Runtime default provider set to: {provider_to_set_default or 'None (revert to ENV default)'}")
            else:
                errors.append("'set_runtime_default_provider' must be a string or null.")

        # Update specific provider settings
        if "update_provider_settings" in data:
            provider_updates = data["update_provider_settings"]
            if isinstance(provider_updates, dict):
                for provider_name, settings in provider_updates.items():
                    if isinstance(settings, dict):
                        # Further validation can be added here for model/temp values
                        manager.update_provider_settings(provider_name, settings)
                        actions_performed.append(f"Settings updated for provider: {provider_name} with {settings}")
                    else:
                        errors.append(f"Settings for '{provider_name}' must be a dictionary.")
            else:
                errors.append("'update_provider_settings' must be a dictionary.")

        # Clear settings for a specific provider
        if "clear_provider_settings" in data:
            provider_to_clear = data["clear_provider_settings"]
            if isinstance(provider_to_clear, str) and provider_to_clear:
                manager.clear_provider_settings(provider_to_clear)
                actions_performed.append(f"Cleared runtime settings for provider: {provider_to_clear}")
            else:
                errors.append("'clear_provider_settings' must be a non-empty string (provider name).")

        # Clear all runtime settings
        if data.get("clear_all_runtime_settings") is True:
            manager.clear_all_runtime_settings()
            actions_performed.append("Cleared all runtime LLM configurations. System will use environment defaults.")
            # If other specific actions were requested, they might be redundant now, but process anyway.

        if not actions_performed and not errors:
            return jsonify({"message": "No configuration actions specified or performed.", "valid_actions": ["set_runtime_default_provider", "update_provider_settings", "clear_provider_settings", "clear_all_runtime_settings"]}), 400

        if errors:
            return jsonify({"message": "Configuration updated with some errors.", "actions_performed": actions_performed, "errors": errors}), 400 if actions_performed else 400

        return jsonify({"message": "LLM configuration updated successfully.", "actions_performed": actions_performed}), 200

    except ValueError as ve:
        logger.error(f"ValueError during LLM configuration update: {ve}", exc_info=True)
        errors.append(f"Invalid input: {ve}")
        return jsonify({"message": "Error updating LLM configuration.", "actions_performed": actions_performed, "errors": errors}), 400
    except RuntimeError as re:
        logger.error(f"RuntimeError during LLM configuration update: {re}", exc_info=True)
        errors.append(f"Failed to save configuration: {re}")
        return jsonify({"message": "Error saving LLM configuration.", "actions_performed": actions_performed, "errors": errors}), 500
    except Exception as e:
        logger.error(f"Unexpected error during LLM configuration update: {e}", exc_info=True)
        errors.append(f"An unexpected error occurred: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "actions_performed": actions_performed, "errors": errors}), 500
