from flask import request, jsonify
import logging
from . import mcp_configure_bp # Import the blueprint from this package's __init__

# Assuming LlmConfigManager is in the k_ConfigManager package within e_Infra
from src.e_Infra.k_ConfigManager.LlmConfigManager import LlmConfigManager

logger = logging.getLogger(__name__)

# Note: No explicit security is added to these endpoints as per user instruction.
# In a production environment, these should be appropriately secured.

@mcp_configure_bp.route('/ask/configure', methods=['GET'])
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

@mcp_configure_bp.route('/ask/configure', methods=['POST'])
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
