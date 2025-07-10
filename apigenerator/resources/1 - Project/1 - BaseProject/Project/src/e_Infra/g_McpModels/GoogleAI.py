import os
from langchain_google_genai import ChatGoogleGenerativeAI
# Imports from the centralized EnvironmentVariables module
import logging

logger = logging.getLogger(__name__)

# Check if API key is a placeholder or empty, and only initialize if valid
gemini_api_key = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY_PLACEHOLDER")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
gemini_temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.4"))
gemini_max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))

if gemini_api_key and gemini_api_key != "GEMINI_API_KEY_PLACEHOLDER":
    try:
        google_ai_model = ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=gemini_temperature,
            # The ChatGoogleGenerativeAI class uses 'max_output_tokens'
            max_output_tokens=gemini_max_output_tokens,
            google_api_key=gemini_api_key, # Parameter name is google_api_key
            # convert_system_message_to_human=True # May be needed depending on ReAct agent behavior with system messages
        )
        logger.info(f"GoogleAI (Gemini) model '{gemini_model}' initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize GoogleAI (Gemini) model '{gemini_model}': {e}", exc_info=True)
        google_ai_model = None # Ensure it's None if initialization fails
else:
    logger.warning("GoogleAI (Gemini) API Key is not configured or is a placeholder. Model not initialized.")
    google_ai_model = None
