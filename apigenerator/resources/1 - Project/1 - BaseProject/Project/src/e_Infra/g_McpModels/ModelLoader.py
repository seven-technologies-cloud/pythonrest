import os
import logging
from .GoogleAI import google_ai_model
from .OpenAI import openai_model
from .AnthropicAI import anthropic_model
# Ollama is explicitly not supported based on user feedback.

logger = logging.getLogger(__name__)

# These globals are for informational purposes, reflecting what model_loader *would* load.
# The actual model instance is returned by load_model().
CURRENT_CONFIGURED_MODEL_NAME: str = "Not Set"
CURRENT_CONFIGURED_TEMPERATURE: float | None = None

def load_model(provider_name: str = None):
    """
    Load and return a pre-initialized Langchain ChatModel based on the provider_name.
    If provider_name is None, it uses SELECTED_LLM_PROVIDER from environment variables.
    It also updates global variables CURRENT_CONFIGURED_MODEL_NAME and CURRENT_CONFIGURED_TEMPERATURE
    for informational/logging purposes elsewhere if needed.

    Args:
        provider_name (str, optional): The name of the LLM provider to load
                                       ("gemini", "openai", "anthropic").
                                       Defaults to SELECTED_LLM_PROVIDER.

    Returns:
        A Langchain ChatModel instance (e.g., ChatGoogleGenerativeAI, ChatOpenAI)
        or None if the selected provider's model failed to initialize (e.g., missing API key).

    Raises:
        ValueError: If the determined provider_name is not supported or if the model instance is None.
    """
    global CURRENT_CONFIGURED_MODEL_NAME, CURRENT_CONFIGURED_TEMPERATURE

    effective_provider = (provider_name or os.getenv("SELECTED_LLM_PROVIDER", "gemini")).lower()

    selected_model_instance = None

    if effective_provider == "gemini": # "google" was in user snippet, using "gemini" for consistency
        CURRENT_CONFIGURED_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        CURRENT_CONFIGURED_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.4"))
        selected_model_instance = google_ai_model
        logger.info(f"Loading Gemini (Google) model: {CURRENT_CONFIGURED_MODEL_NAME}, Temp: {CURRENT_CONFIGURED_TEMPERATURE}")
    elif effective_provider == "openai":
        CURRENT_CONFIGURED_MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        CURRENT_CONFIGURED_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
        selected_model_instance = openai_model
        logger.info(f"Loading OpenAI model: {CURRENT_CONFIGURED_MODEL_NAME}, Temp: {CURRENT_CONFIGURED_TEMPERATURE}")
    elif effective_provider == "anthropic":
        CURRENT_CONFIGURED_MODEL_NAME = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        CURRENT_CONFIGURED_TEMPERATURE = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))
        selected_model_instance = anthropic_model
        logger.info(f"Loading Anthropic model: {CURRENT_CONFIGURED_MODEL_NAME}, Temp: {CURRENT_CONFIGURED_TEMPERATURE}")
    else:
        logger.error(f"Unsupported LLM provider specified: '{effective_provider}'. Supported: gemini, openai, anthropic.")
        raise ValueError(f"LLM Provider '{effective_provider}' is not supported. Choose from 'gemini', 'openai', or 'anthropic'.")

    if selected_model_instance is None:
        err_msg = (f"The selected LLM provider '{effective_provider}' was chosen, but its model instance "
                   f"({CURRENT_CONFIGURED_MODEL_NAME}) could not be initialized. "
                   "This usually means the API key is missing, invalid, or a placeholder. "
                   "Please check environment variables and application logs.")
        logger.error(err_msg)
        raise ValueError(err_msg)

    return selected_model_instance

# Example of how it might be called by other parts of the system:
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     # Test with default provider (from SELECTED_LLM_PROVIDER env var, or its default "gemini")
#     try:
#         print(f"\n--- Testing with default provider (SELECTED_LLM_PROVIDER: {SELECTED_LLM_PROVIDER}) ---")
#         default_llm = load_model()
#         print(f"Loaded default model: {type(default_llm).__name__}")
#         print(f"Effective Model: {CURRENT_CONFIGURED_MODEL_NAME}, Temp: {CURRENT_CONFIGURED_TEMPERATURE}")
#     except ValueError as e:
#         print(f"Error: {e}")

#     # Test with a specific provider override
#     try:
#         print("\n--- Testing with specific provider: openai ---")
#         openai_llm = load_model("openai") # Assumes OPENAI_API_KEY is set (or placeholder)
#         print(f"Loaded OpenAI model: {type(openai_llm).__name__}")
#         print(f"Effective Model: {CURRENT_CONFIGURED_MODEL_NAME}, Temp: {CURRENT_CONFIGURED_TEMPERATURE}")
#     except ValueError as e:
#         print(f"Error: {e}")
#     except Exception as ex: # Catch other init errors if API key is placeholder
#         print(f"General Error during OpenAI load: {ex}")
#         if openai_model is None:
#             print("OpenAI model instance is None, likely due to API key issue.")

#     # Test with an unsupported provider
#     try:
#         print("\n--- Testing with unsupported provider: foobar ---")
#         unsupported_llm = load_model("foobar")
#     except ValueError as e:
#         print(f"Error as expected: {e}")
