import logging
from src.e_Infra.CustomVariables import (
    ENV_DEFAULT_LLM_PROVIDER,
    GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY,
    ENV_DEFAULT_GEMINI_MODEL_NAME, ENV_DEFAULT_OPENAI_MODEL_NAME, ENV_DEFAULT_ANTHROPIC_MODEL_NAME,
    ENV_DEFAULT_GEMINI_TEMPERATURE, ENV_DEFAULT_OPENAI_TEMPERATURE, ENV_DEFAULT_ANTHROPIC_TEMPERATURE
)
from src.e_Infra.k_ConfigManager.LlmConfigManager import LlmConfigManager
from src.e_Infra.g_GeminiClient.GeminiService import GeminiService
from src.e_Infra.h_OpenAIClient.OpenAIService import OpenAIService
from src.e_Infra.i_AnthropicClient.AnthropicService import AnthropicService
from .LlmServiceBase import LlmServiceBase

logger = logging.getLogger(__name__)

class LlmServiceFactory:
    """
    Factory class to create and provide instances of LLM services.
    It uses a combination of environment variables (for API keys and initial defaults)
    and a runtime JSON configuration file (for dynamic overrides of defaults and provider settings).
    """

    @staticmethod
    def get_llm_service(x_provider_header: str = None) -> LlmServiceBase:
        """
        Gets an instance of the LLM service based on header override, runtime config, or env defaults.

        Args:
            x_provider_header (str, optional): Value from 'X-Provider' header to override default provider.

        Returns:
            LlmServiceBase: An instance of the configured LLM service.

        Raises:
            ValueError: If no provider can be determined, if the selected provider is unsupported,
                        or if the required API key for the selected provider is missing.
            RuntimeError: If there's an error during the instantiation of the LLM service.
        """
        config_manager = LlmConfigManager() # Uses default config file path from CustomVariables

        # 1. Determine the provider
        chosen_provider_name = None
        source_of_provider_choice = "unknown"

        if x_provider_header:
            chosen_provider_name = x_provider_header.lower()
            source_of_provider_choice = "X-Provider header"
        else:
            runtime_default_provider = config_manager.get_runtime_default_provider()
            if runtime_default_provider:
                chosen_provider_name = runtime_default_provider.lower()
                source_of_provider_choice = "runtime_config (llm_config.json)"
            elif ENV_DEFAULT_LLM_PROVIDER:
                chosen_provider_name = ENV_DEFAULT_LLM_PROVIDER.lower()
                source_of_provider_choice = "environment (ENV_DEFAULT_LLM_PROVIDER)"

        if not chosen_provider_name:
            logger.error("No LLM provider specified by X-Provider header, runtime_config, or ENV_DEFAULT_LLM_PROVIDER.")
            raise ValueError("No LLM provider configured. Please set ENV_DEFAULT_LLM_PROVIDER or configure via API.")

        logger.info(f"Attempting to get LLM service for provider: '{chosen_provider_name}' (Source: {source_of_provider_choice})")

        # 2. Get API Key for the chosen provider (from environment ONLY)
        api_key = None
        if chosen_provider_name == "gemini": api_key = GEMINI_API_KEY
        elif chosen_provider_name == "openai": api_key = OPENAI_API_KEY
        elif chosen_provider_name == "anthropic": api_key = ANTHROPIC_API_KEY

        if not api_key:
            err_msg = f"API key for selected provider '{chosen_provider_name}' is not configured in environment variables."
            logger.error(err_msg)
            raise ValueError(err_msg)

        # 3. Get Model Name and Temperature for the chosen provider
        # Order: runtime_config -> env_default -> service_internal_default (by passing None to constructor)
        provider_runtime_settings = config_manager.get_provider_settings(chosen_provider_name) or {}

        model_name = provider_runtime_settings.get("model")
        temperature_str = provider_runtime_settings.get("temperature") # Stored as string/float in JSON potentially

        if not model_name: # Fallback to environment default model name
            if chosen_provider_name == "gemini": model_name = ENV_DEFAULT_GEMINI_MODEL_NAME
            elif chosen_provider_name == "openai": model_name = ENV_DEFAULT_OPENAI_MODEL_NAME
            elif chosen_provider_name == "anthropic": model_name = ENV_DEFAULT_ANTHROPIC_MODEL_NAME

        temperature = None
        if temperature_str is not None: # If runtime config has temperature
            try:
                temperature = float(temperature_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid temperature '{temperature_str}' in runtime config for {chosen_provider_name}. Will try env default.")
                temperature_str = None # Force fallback to env default or service default

        if temperature is None: # Fallback to environment default temperature if runtime was missing or invalid
            env_temp_str = None
            if chosen_provider_name == "gemini": env_temp_str = ENV_DEFAULT_GEMINI_TEMPERATURE
            elif chosen_provider_name == "openai": env_temp_str = ENV_DEFAULT_OPENAI_TEMPERATURE
            elif chosen_provider_name == "anthropic": env_temp_str = ENV_DEFAULT_ANTHROPIC_TEMPERATURE

            if env_temp_str is not None:
                try:
                    temperature = float(env_temp_str)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid temperature '{env_temp_str}' in environment for {chosen_provider_name}. Service will use its default.")
                    # temperature remains None, service will use its hardcoded default

        # 4. Instantiate the service
        logger.info(f"Instantiating {chosen_provider_name} service with: model='{model_name or 'Service Default'}', temperature={temperature if temperature is not None else 'Service Default'}")
        try:
            if chosen_provider_name == "gemini":
                return GeminiService(api_key=api_key, model_name=model_name, temperature=temperature)
            elif chosen_provider_name == "openai":
                return OpenAIService(api_key=api_key, model_name=model_name, temperature=temperature)
            elif chosen_provider_name == "anthropic":
                return AnthropicService(api_key=api_key, model_name=model_name, temperature=temperature)
            else:
                err_msg = f"Unsupported LLM provider: '{chosen_provider_name}'. Supported: 'gemini', 'openai', 'anthropic'."
                logger.error(err_msg)
                raise ValueError(err_msg)
        except Exception as e:
            logger.error(f"Failed to instantiate {chosen_provider_name}Service: {e}", exc_info=True)
            raise RuntimeError(f"Error initializing {chosen_provider_name}Service: {e}")


# Example Usage (for testing purposes, not typically run directly)
# if __name__ == '__main__':
#     # This example requires:
#     # 1. `llm_config.json` to potentially exist or be created.
#     # 2. Environment variables for API keys and potentially defaults to be set.
#     #    (e.g., os.environ['GEMINI_API_KEY'] = 'your_key')
#     #    (e.g., os.environ['ENV_DEFAULT_LLM_PROVIDER'] = 'gemini')
#
#     logging.basicConfig(level=logging.INFO)
#     # Test scenarios would involve mocking CustomVariables and LlmConfigManager,
#     # or setting up actual environment variables and llm_config.json file.
#
#     # Example: Assuming ENV_DEFAULT_LLM_PROVIDER="gemini" and GEMINI_API_KEY is set
#     try:
#         print("\n--- Scenario: Default provider from ENV ---")
#         # Mock CustomVariables for this test if needed, or ensure env vars are set
#         # For example, to test without X-Provider and no runtime config:
#         # CustomVariables.ENV_DEFAULT_LLM_PROVIDER = "gemini"
#         # CustomVariables.GEMINI_API_KEY = "actual_or_mock_key"
#         # CustomVariables.OPENAI_API_KEY = None
#         # CustomVariables.ANTHROPIC_API_KEY = None
#
#         # Ensure LlmConfigManager returns no runtime default for this specific test case
#         # This might involve creating a temporary empty llm_config.json or mocking LlmConfigManager
#         # temp_config_path = "temp_test_llm_config.json"
#         # with open(temp_config_path, "w") as f: json.dump({}, f)
#         # original_config_path = CustomVariables.LLM_CONFIG_FILE_PATH
#         # CustomVariables.LLM_CONFIG_FILE_PATH = temp_config_path
#
#         llm_service = LlmServiceFactory.get_llm_service()
#         print(f"Got service: {type(llm_service).__name__}")
#         # print(f"Service model: {llm_service.model_name}, temp: {llm_service.temperature}")
#
#         # print("\n--- Scenario: Provider from X-Provider header ---")
#         # CustomVariables.OPENAI_API_KEY = "actual_or_mock_key_for_openai" # Ensure key for openai is set
#         # llm_service_openai = LlmServiceFactory.get_llm_service(x_provider_header="openai")
#         # print(f"Got service from header: {type(llm_service_openai).__name__}")
#
#         # print("\n--- Scenario: Provider from runtime config (llm_config.json) ---")
#         # manager = LlmConfigManager(config_file_path=temp_config_path)
#         # manager.set_runtime_default_provider("anthropic")
#         # manager.update_provider_settings("anthropic", {"model": "claude-test", "temperature": 0.1})
#         # CustomVariables.ANTHROPIC_API_KEY = "actual_or_mock_key_for_anthropic"
#         # llm_service_anthropic = LlmServiceFactory.get_llm_service()
#         # print(f"Got service from runtime config: {type(llm_service_anthropic).__name__}")
#         # print(f"Service model: {llm_service_anthropic.model_name}, temp: {llm_service_anthropic.temperature}")
#
#     except ValueError as e:
#         print(f"CONFIG ERROR: {e}")
#     except RuntimeError as e:
#         print(f"RUNTIME ERROR: {e}")
#     except Exception as e:
#         print(f"UNEXPECTED ERROR: {e}")
#     # finally:
#         # if os.path.exists(temp_config_path): os.remove(temp_config_path)
#         # CustomVariables.LLM_CONFIG_FILE_PATH = original_config_path # Restore
#     # Mock environment variables for testing different scenarios
#     # Note: To run this, you'd need to temporarily set these os.environ values
#     # or ensure CustomVariables.py can pick them up if it's modified to also check os.environ directly for this test.
#
#     # Scenario 1: Gemini
#     # os.environ['LLM_PROVIDER'] = 'gemini'
#     # os.environ['GEMINI_API_KEY'] = 'fake_gemini_key'
#
#     # Scenario 2: OpenAI
#     # os.environ['LLM_PROVIDER'] = 'openai'
#     # os.environ['OPENAI_API_KEY'] = 'fake_openai_key'
#
#     # Scenario 3: Anthropic
#     # os.environ['LLM_PROVIDER'] = 'anthropic'
#     # os.environ['ANTHROPIC_API_KEY'] = 'fake_anthropic_key'
#
#     # Scenario 4: Provider not set (should raise ValueError)
#     # if 'LLM_PROVIDER' in os.environ: del os.environ['LLM_PROVIDER']
#
#     # Scenario 5: Unsupported provider (should raise ValueError)
#     # os.environ['LLM_PROVIDER'] = 'unsupported_llm'
#
#     # Scenario 6: Provider set, but key missing (should raise ValueError)
#     # os.environ['LLM_PROVIDER'] = 'gemini'
#     # if 'GEMINI_API_KEY' in os.environ: del os.environ['GEMINI_API_KEY']
#
#     # Reload CustomVariables if they only read os.getenv at import time and you're setting os.environ here
#     # import importlib
#     # from src.e_Infra import CustomVariables
#     # importlib.reload(CustomVariables)
#     # LLM_PROVIDER = CustomVariables.LLM_PROVIDER # etc.
#
#     logging.basicConfig(level=logging.INFO)
#     try:
#         print(f"Configured LLM_PROVIDER: {LLM_PROVIDER}")
#         print(f"GEMINI_API_KEY available: {'Yes' if GEMINI_API_KEY else 'No'}")
#         print(f"OPENAI_API_KEY available: {'Yes' if OPENAI_API_KEY else 'No'}")
#         print(f"ANTHROPIC_API_KEY available: {'Yes' if ANTHROPIC_API_KEY else 'No'}")
#
#         llm_service_instance = LlmServiceFactory.get_llm_service()
#         print(f"Successfully obtained LLM service: {type(llm_service_instance).__name__}")
#
#         # Example: Test check_connection (would make actual API call if keys were real)
#         # if llm_service_instance.check_connection():
#         #     print("Connection check successful.")
#         # else:
#         #     print("Connection check failed.")
#
#     except ValueError as ve:
#         print(f"Configuration Error: {ve}")
#     except RuntimeError as re:
#         print(f"Runtime Error during service initialization: {re}")
#     except Exception as ex:
#         print(f"An unexpected error occurred: {ex}")
#
#     # Clean up environment variables if set for test
#     # if 'LLM_PROVIDER' in os.environ: del os.environ['LLM_PROVIDER']
#     # ... and for API keys
#
#     # This example assumes CustomVariables are updated when os.env changes.
#     # In a real test, you might mock CustomVariables or use a dedicated test config.
