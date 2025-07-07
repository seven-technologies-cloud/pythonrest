from langchain_google_genai import ChatGoogleGenerativeAI
# Imports from the centralized EnvironmentVariables module
from src.e_Infra.g_Environment.EnvironmentVariables import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_OUTPUT_TOKENS
)
import logging

logger = logging.getLogger(__name__)

# Check if API key is a placeholder or empty, and only initialize if valid
if GEMINI_API_KEY and GEMINI_API_KEY != "GEMINI_API_KEY_PLACEHOLDER":
    try:
        google_ai_model = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=GEMINI_TEMPERATURE,
            # The ChatGoogleGenerativeAI class uses 'max_output_tokens'
            max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            google_api_key=GEMINI_API_KEY, # Parameter name is google_api_key
            # convert_system_message_to_human=True # May be needed depending on ReAct agent behavior with system messages
        )
        logger.info(f"GoogleAI (Gemini) model '{GEMINI_MODEL}' initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize GoogleAI (Gemini) model '{GEMINI_MODEL}': {e}", exc_info=True)
        google_ai_model = None # Ensure it's None if initialization fails
else:
    logger.warning("GoogleAI (Gemini) API Key is not configured or is a placeholder. Model not initialized.")
    google_ai_model = None
