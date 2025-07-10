import logging
from src.e_Infra.g_McpInfra import LlmConfigManager
from src.e_Infra.g_McpInfra.c_GeminiClient.GeminiService import GeminiService
from src.e_Infra.g_McpInfra.d_OpenAIClient.OpenAIService import OpenAIService
from src.e_Infra.g_McpInfra.e_AnthropicClient.AnthropicService import AnthropicService
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
        config_manager = LlmConfigManager()

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
            elif os.getenv("SELECTED_LLM_PROVIDER"):
                chosen_provider_name = os.getenv("SELECTED_LLM_PROVIDER").lower()
                source_of_provider_choice = "environment (SELECTED_LLM_PROVIDER)"
            else:
                 # Default if no env var is set
                 chosen_provider_name = "gemini"
                 source_of_provider_choice = "environment (SELECTED_LLM_PROVIDER default)"


        if not chosen_provider_name:
            logger.error("No LLM provider specified by X-Provider header, runtime_config, or SELECTED_LLM_PROVIDER env var.")
            raise ValueError("No LLM provider configured. Please set SELECTED_LLM_PROVIDER env var or configure via API.")

        logger.info(f"Attempting to get LLM service for provider: '{chosen_provider_name}' (Source: {source_of_provider_choice})")

        # 2. Get API Key for the chosen provider (from Environment Variables)
        api_key = None
        if chosen_provider_name == "gemini": api_key = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY_PLACEHOLDER")
        elif chosen_provider_name == "openai": api_key = os.getenv("OPENAI_API_KEY", "OPENAI_API_KEY_PLACEHOLDER")
        elif chosen_provider_name == "anthropic": api_key = os.getenv("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_PLACEHOLDER")

        # Check for empty string or placeholder values for API keys
        api_key_placeholders = [
            "GEMINI_API_KEY_PLACEHOLDER",
            "OPENAI_API_KEY_PLACEHOLDER",
            "ANTHROPIC_API_KEY_PLACEHOLDER",
            "" # Also treat empty string as missing
        ]
        if not api_key or api_key in api_key_placeholders:
            err_msg = f"API key for selected provider '{chosen_provider_name}' is missing or is a placeholder. Please set the actual API key in environment variables."
            logger.error(err_msg)
            raise ValueError(err_msg)

        # 3. Get Model Name, Temperature, and Max Output Tokens for the chosen provider
        # Order: runtime_config -> env_default -> service_internal_default (by passing None)
        provider_runtime_settings = config_manager.get_provider_settings(chosen_provider_name) or {}

        # Model Name
        model_name = provider_runtime_settings.get("model")
        if not model_name: # Fallback to environment default model name
            if chosen_provider_name == "gemini": model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            elif chosen_provider_name == "openai": model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            elif chosen_provider_name == "anthropic": model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

        # Temperature
        temperature_val_from_runtime = provider_runtime_settings.get("temperature")
        temperature = None
        if temperature_val_from_runtime is not None:
            try: temperature = float(temperature_val_from_runtime)
            except (ValueError, TypeError):
                logger.warning(f"Invalid temperature '{temperature_val_from_runtime}' in runtime config for {chosen_provider_name}. Trying env default.")

        if temperature is None: # Fallback to environment default temperature
            if chosen_provider_name == "gemini": temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.4"))
            elif chosen_provider_name == "openai": temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
            elif chosen_provider_name == "anthropic": temperature = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))
            # os.getenv with float conversion handles parsing and default values

        # Max Output Tokens
        max_tokens_val_from_runtime = provider_runtime_settings.get("max_output_tokens")
        max_output_tokens = None
        if max_tokens_val_from_runtime is not None:
            try: max_output_tokens = int(max_tokens_val_from_runtime)
            except (ValueError, TypeError):
                logger.warning(f"Invalid max_output_tokens '{max_tokens_val_from_runtime}' in runtime config for {chosen_provider_name}. Trying env default.")

        if max_output_tokens is None: # Fallback to environment default max_tokens
            if chosen_provider_name == "gemini": max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
            elif chosen_provider_name == "openai": max_output_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2000"))
            elif chosen_provider_name == "anthropic": max_output_tokens = int(os.getenv("ANTHROPIC_MAX_OUTPUT_TOKENS", "2048"))
            # os.getenv with int conversion handles parsing and default values

        # 4. Instantiate the service
        # Parameters (model_name, temperature, max_output_tokens) will be None if not found in runtime or env,
        # allowing the service constructor to use its own internal defaults.
        logger.info(f"Instantiating {chosen_provider_name} service with: "
                    f"model='{model_name or 'Service Default'}', "
                    f"temperature={temperature if temperature is not None else 'Service Default'}, "
                    f"max_output_tokens={max_output_tokens if max_output_tokens is not None else 'Service Default'}")
        try:
            if chosen_provider_name == "gemini":
                return GeminiService(api_key=api_key, model_name=model_name, temperature=temperature, max_output_tokens=max_output_tokens)
            elif chosen_provider_name == "openai":
                return OpenAIService(api_key=api_key, model_name=model_name, temperature=temperature, max_output_tokens=max_output_tokens)
            elif chosen_provider_name == "anthropic":
                return AnthropicService(api_key=api_key, model_name=model_name, temperature=temperature, max_output_tokens=max_output_tokens)
            else: # Should be caught by initial provider check, but as a safeguard:
                err_msg = f"Unsupported LLM provider: '{chosen_provider_name}'. Supported: 'gemini', 'openai', 'anthropic'."
                logger.error(err_msg)
                raise ValueError(err_msg)
        except Exception as e:
            logger.error(f"Failed to instantiate {chosen_provider_name}Service: {e}", exc_info=True)
            raise RuntimeError(f"Error initializing {chosen_provider_name}Service: {e}")
