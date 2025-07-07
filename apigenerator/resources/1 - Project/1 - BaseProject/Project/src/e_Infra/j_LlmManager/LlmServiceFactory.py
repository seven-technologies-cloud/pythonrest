import logging
from src.e_Infra.CustomVariables import LLM_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
from src.e_Infra.g_GeminiClient.GeminiService import GeminiService
from src.e_Infra.h_OpenAIClient.OpenAIService import OpenAIService
from src.e_Infra.i_AnthropicClient.AnthropicService import AnthropicService
from .LlmServiceBase import LlmServiceBase # LlmServiceBase from the same package

logger = logging.getLogger(__name__)

class LlmServiceFactory:
    """
    Factory class to create and provide instances of LLM services based on configuration.
    """

    @staticmethod
    def get_llm_service() -> LlmServiceBase:
        """
        Gets an instance of the configured LLM service.

        Reads the LLM_PROVIDER and corresponding API key from CustomVariables.
        Instantiates and returns the appropriate LLM service client.

        Returns:
            LlmServiceBase: An instance of the configured LLM service.

        Raises:
            ValueError: If LLM_PROVIDER is not set, is unsupported, or if the
                        required API key for the selected provider is missing.
        """
        provider = LLM_PROVIDER
        logger.info(f"Attempting to get LLM service for provider: '{provider}'")

        if not provider:
            logger.error("LLM_PROVIDER is not configured in environment variables.")
            raise ValueError("LLM_PROVIDER is not configured. Please set it in environment variables (e.g., 'gemini', 'openai', 'anthropic').")

        provider = provider.lower()

        if provider == "gemini":
            if not GEMINI_API_KEY:
                logger.error("LLM_PROVIDER is 'gemini', but GEMINI_API_KEY is not set.")
                raise ValueError("GEMINI_API_KEY is not configured for the selected 'gemini' provider.")
            try:
                return GeminiService(api_key=GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to instantiate GeminiService: {e}", exc_info=True)
                raise RuntimeError(f"Error initializing GeminiService: {e}")

        elif provider == "openai":
            if not OPENAI_API_KEY:
                logger.error("LLM_PROVIDER is 'openai', but OPENAI_API_KEY is not set.")
                raise ValueError("OPENAI_API_KEY is not configured for the selected 'openai' provider.")
            try:
                return OpenAIService(api_key=OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to instantiate OpenAIService: {e}", exc_info=True)
                raise RuntimeError(f"Error initializing OpenAIService: {e}")

        elif provider == "anthropic":
            if not ANTHROPIC_API_KEY:
                logger.error("LLM_PROVIDER is 'anthropic', but ANTHROPIC_API_KEY is not set.")
                raise ValueError("ANTHROPIC_API_KEY is not configured for the selected 'anthropic' provider.")
            try:
                return AnthropicService(api_key=ANTHROPIC_API_KEY)
            except Exception as e:
                logger.error(f"Failed to instantiate AnthropicService: {e}", exc_info=True)
                raise RuntimeError(f"Error initializing AnthropicService: {e}")

        else:
            logger.error(f"Unsupported LLM_PROVIDER: '{provider}'. Supported providers are 'gemini', 'openai', 'anthropic'.")
            raise ValueError(f"Unsupported LLM_PROVIDER: '{provider}'. Supported providers are 'gemini', 'openai', 'anthropic'.")

# Example Usage (for testing purposes, not typically run directly)
# if __name__ == '__main__':
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
