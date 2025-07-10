import json
import os
import logging
import threading # For basic thread safety on file access
import json
import os
import logging
import threading # For basic thread safety on file access

logger = logging.getLogger(__name__)

class LlmConfigManager:
    """
    Manages dynamic LLM configurations stored in a JSON file.
    It allows reading and writing runtime configurations that can override
    initial defaults set by environment variables.
    API keys themselves are NOT managed here; they are sourced from EnvironmentVariables (env vars).
    """
    _lock = threading.Lock() # Class-level lock for file operations
    DEFAULT_RUNTIME_CONFIG_PATH = './config/llm_runtime_config.json'

    def __init__(self, config_file_path: str = None):
        """
        Initializes the LlmConfigManager.

        Args:
            config_file_path (str, optional): Path to the LLM config JSON file.
                                              Defaults to LLM_CONFIG_FILE_PATH from Environment Variables.
        """
        self.config_file_path = config_file_path or os.environ.get('LLM_CONFIG_FILE_PATH')
        if not self.config_file_path:
             raise ValueError("LLM_CONFIG_FILE_PATH is not set in environment variables.")

        # Ensure the directory for the config file exists
        os.makedirs(os.path.dirname(self.config_file_path) or '.', exist_ok=True)


    def _load_config(self) -> dict:
        """
        Loads the configuration from the JSON file.
        Handles file not found by returning a default structure.
        """
        with self._lock:
            try:
                if os.path.exists(self.config_file_path):
                    with open(self.config_file_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        logger.info(f"LLM runtime config loaded from {self.config_file_path}")
                        return config
                else:
                    logger.info(f"LLM runtime config file not found at {self.config_file_path}. Returning empty default structure.")
                    return {"runtime_default_provider": None, "providers": {}} # Default structure
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {self.config_file_path}. Returning empty default structure.", exc_info=True)
                return {"runtime_default_provider": None, "providers": {}}
            except Exception as e:
                logger.error(f"Error loading LLM runtime config from {self.config_file_path}: {e}", exc_info=True)
                return {"runtime_default_provider": None, "providers": {}}

    def _save_config(self, config_data: dict):
        """
        Saves the configuration data to the JSON file.
        """
        with self._lock:
            try:
                with open(self.config_file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4)
                logger.info(f"LLM runtime config saved to {self.config_file_path}")
            except Exception as e:
                logger.error(f"Error saving LLM runtime config to {self.config_file_path}: {e}", exc_info=True)
                # Depending on desired robustness, might re-raise or handle
                raise RuntimeError(f"Failed to save LLM runtime configuration: {e}")

    def get_runtime_default_provider(self) -> str | None:
        """Gets the runtime_default_provider from the JSON config."""
        config = self._load_config()
        return config.get("runtime_default_provider")

    def set_runtime_default_provider(self, provider_name: str | None):
        """Sets the runtime_default_provider in the JSON config."""
        if provider_name is not None and not isinstance(provider_name, str):
            raise TypeError("provider_name must be a string or None.")
        config = self._load_config()
        config["runtime_default_provider"] = provider_name.lower() if provider_name else None
        self._save_config(config)
        logger.info(f"Runtime default LLM provider set to: {config['runtime_default_provider']}")

    def get_provider_settings(self, provider_name: str) -> dict | None:
        """Gets specific config (model, temp) for a provider from JSON config."""
        if not provider_name or not isinstance(provider_name, str):
            logger.warning("get_provider_settings called with invalid provider_name.")
            return None
        config = self._load_config()
        return config.get("providers", {}).get(provider_name.lower())

    def update_provider_settings(self, provider_name: str, settings: dict):
        """
        Updates a provider's specific settings (model, temperature) in the JSON config.
        Only updates keys present in the `settings` dict.
        """
        if not provider_name or not isinstance(provider_name, str):
            raise ValueError("provider_name must be a non-empty string.")
        if not isinstance(settings, dict):
            raise TypeError("settings must be a dictionary.")

        config = self._load_config()
        provider_name_lower = provider_name.lower()

        if "providers" not in config:
            config["providers"] = {}
        if provider_name_lower not in config["providers"]:
            config["providers"][provider_name_lower] = {}

        # Update only specified settings
        for key, value in settings.items():
            if key in ["model", "temperature"]: # Whitelist configurable settings
                 config["providers"][provider_name_lower][key] = value
            else:
                 logger.warning(f"Attempted to update unsupported setting '{key}' for provider '{provider_name_lower}'. Ignoring.")

        self._save_config(config)
        logger.info(f"Runtime settings updated for LLM provider: {provider_name_lower} with {settings}")

    def get_effective_config(self) -> dict:
        """
        Merges runtime config from JSON with environment variable defaults
        to show the currently effective configuration.
        Does NOT include API Keys.
        """
        runtime_config = self._load_config()
        effective_config = {
            "determined_default_provider": self.get_runtime_default_provider() or os.environ.get("ENV_DEFAULT_LLM_PROVIDER") or "Not Set",
            "config_source_default_provider": "runtime (llm_runtime_config.json)" if self.get_runtime_default_provider() else \
                                           "environment (ENV_DEFAULT_LLM_PROVIDER)" if os.environ.get("ENV_DEFAULT_LLM_PROVIDER") else "None",
            "providers": {
                "gemini": {}, "openai": {}, "anthropic": {}
            },
            "llm_config_file_path": self.config_file_path
        }

        for provider in ["gemini", "openai", "anthropic"]:
            runtime_provider_settings = runtime_config.get("providers", {}).get(provider, {})

            # Model
            model = runtime_provider_settings.get("model")
            model_source = "runtime (llm_runtime_config.json)"
            if not model:
                if provider == "gemini": model = os.environ.get("ENV_DEFAULT_GEMINI_MODEL_NAME")
                elif provider == "openai": model = os.environ.get("ENV_DEFAULT_OPENAI_MODEL_NAME")
                elif provider == "anthropic": model = os.environ.get("ENV_DEFAULT_ANTHROPIC_MODEL_NAME")
                model_source = "environment default"
            # Service will have its own hardcoded default if still None here
            effective_config["providers"][provider]["model"] = model or "Service Default"
            effective_config["providers"][provider]["model_source"] = model_source if model else "Service Default"

            # Temperature
            temp_str = runtime_provider_settings.get("temperature")
            temp_source = "runtime (llm_runtime_config.json)"
            if temp_str is None: # Check for None, not just falsy, as 0.0 is valid temp
                if provider == "gemini": temp_str = os.environ.get("ENV_DEFAULT_GEMINI_TEMPERATURE")
                elif provider == "openai": temp_str = os.environ.get("ENV_DEFAULT_OPENAI_TEMPERATURE")
                elif provider == "anthropic": temp_str = os.environ.get("ENV_DEFAULT_ANTHROPIC_TEMPERATURE")
                temp_source = "environment default"

            temp_val = None
            if temp_str is not None:
                try:
                    temp_val = float(temp_str)
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse temperature '{temp_str}' for {provider} as float.")
                    temp_val = "Invalid Format" # Or None to let service use its default

            effective_config["providers"][provider]["temperature"] = temp_val if temp_val is not None else "Service Default"
            effective_config["providers"][provider]["temperature_source"] = temp_source if temp_str is not None else "Service Default"

        return effective_config

    def clear_provider_settings(self, provider_name: str):
        """Clears all runtime settings for a specific provider."""
        config = self._load_config()
        provider_name_lower = provider_name.lower()
        if "providers" in config and provider_name_lower in config["providers"]:
            del config["providers"][provider_name_lower]
            if not config["providers"]: # if providers dict becomes empty
                del config["providers"]
            self._save_config(config)
            logger.info(f"Cleared all runtime settings for provider: {provider_name_lower}")

    def clear_all_runtime_settings(self):
        """Clears all runtime configurations, reverting to environment defaults."""
        empty_config = {"runtime_default_provider": None, "providers": {}}
        self._save_config(empty_config)
        logger.info("Cleared all runtime LLM configurations. System will use environment defaults.")

# Example:
# manager = LlmConfigManager()
# manager.set_runtime_default_provider("openai")
# manager.update_provider_settings("openai", {"model": "gpt-4o", "temperature": 0.5})
# print(json.dumps(manager.get_effective_config(), indent=2))
