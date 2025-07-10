import json
import os
import logging
import threading # For basic thread safety on file access
# Import new PathResolver utility
from src.e_Infra.g_McpInfra.PathResolver import get_llm_runtime_config_path
# Updated to import from EnvironmentVariables.py (LLM_CONFIG_FILE_PATH removed from here)

logger = logging.getLogger(__name__)

class LlmConfigManager:
    """
    Manages dynamic LLM configurations stored in a JSON file.
    The path to this JSON file is now determined by PathResolver.
    It allows reading and writing runtime configurations that can override
    initial defaults set by environment variables.
    API keys themselves are NOT managed here; they are sourced from EnvironmentVariables.py.
    """
    _lock = threading.Lock() # Class-level lock for file operations

    def __init__(self):
        """
        Initializes the LlmConfigManager.
        The config file path is determined internally using PathResolver.
        """
        self.config_file_path = get_llm_runtime_config_path()
        # Ensure the directory for the config file exists
        # get_llm_runtime_config_path() returns an absolute path, so os.path.dirname will work.
        config_dir = os.path.dirname(self.config_file_path)
        if not os.path.exists(config_dir): # Check if dir exists before trying to create
             os.makedirs(config_dir, exist_ok=True) # exist_ok=True handles race conditions
        logger.info(f"LlmConfigManager initialized. Config file: {self.config_file_path}")


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
            if key in ["model", "temperature", "max_output_tokens"]: # Whitelist configurable settings
                if key == "max_output_tokens":
                    try:
                        config["providers"][provider_name_lower][key] = int(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid value '{value}' for max_output_tokens for provider '{provider_name_lower}'. Must be an integer. Ignoring update for this key.")
                        # Optionally, raise an error or skip setting this specific key
                        continue
                elif key == "temperature":
                    try:
                        config["providers"][provider_name_lower][key] = float(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid value '{value}' for temperature for provider '{provider_name_lower}'. Must be a float. Ignoring update for this key.")
                        continue
                else: # model
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
            "determined_default_provider": self.get_runtime_default_provider() or os.getenv("SELECTED_LLM_PROVIDER", "gemini").lower() or "Not Set",
            "config_source_default_provider": "runtime (llm_config.json)" if self.get_runtime_default_provider() else \
                                           f"environment (SELECTED_LLM_PROVIDER: {os.getenv('SELECTED_LLM_PROVIDER', 'gemini').lower()})" if os.getenv("SELECTED_LLM_PROVIDER") else "None",
            "providers": {
                "gemini": {}, "openai": {}, "anthropic": {}
            }
        }

        provider_env_defaults = {
            "gemini": {
                "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.4")),
                "max_output_tokens": int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
            },
            "openai": {
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
                "max_output_tokens": int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2000"))
            },
            "anthropic": {
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
                "max_output_tokens": int(os.getenv("ANTHROPIC_MAX_OUTPUT_TOKENS", "2048"))
            }
        }

        for provider_key in ["gemini", "openai", "anthropic"]:
            runtime_settings = runtime_config.get("providers", {}).get(provider_key, {})
            env_defaults = provider_env_defaults[provider_key]

            effective_settings = {}

            # Model
            effective_settings["model"] = runtime_settings.get("model", env_defaults["model"])
            effective_settings["model_source"] = "runtime (llm_config.json)" if "model" in runtime_settings else \
                                                 "environment default" if env_defaults["model"] else "Service Default"
            if not effective_settings["model"]: effective_settings["model"] = "Service Default"


            # Temperature
            temp_val = runtime_settings.get("temperature")
            temp_source = "runtime (llm_config.json)"
            if temp_val is None:
                # Directly use env_defaults which are already converted
                temp_val = env_defaults["temperature"]
                temp_source = "environment default"

            if temp_val is not None:
                # No need for try-except here as env_defaults are already converted floats
                effective_settings["temperature"] = float(temp_val)
                effective_settings["temperature_source"] = temp_source
            else: # Should use service default
                effective_settings["temperature"] = "Service Default"
                effective_settings["temperature_source"] = "Service Default"


            # Max Output Tokens
            tokens_val = runtime_settings.get("max_output_tokens")
            tokens_source = "runtime (llm_config.json)"
            if tokens_val is None:
                 # Directly use env_defaults which are already converted
                tokens_val = env_defaults["max_output_tokens"]
                tokens_source = "environment default"

            if tokens_val is not None:
                # No need for try-except here as env_defaults are already converted ints
                effective_settings["max_output_tokens"] = int(tokens_val)
                effective_settings["max_output_tokens_source"] = tokens_source
            else: # Should use service default
                effective_settings["max_output_tokens"] = "Service Default"
                effective_settings["max_output_tokens_source"] = "Service Default"

            effective_config["providers"][provider_key] = effective_settings

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
