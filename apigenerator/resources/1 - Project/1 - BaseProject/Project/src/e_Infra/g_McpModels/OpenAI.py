from langchain_openai import ChatOpenAI # Correct import for ChatOpenAI
from src.e_Infra.g_Environment.EnvironmentVariables import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_OUTPUT_TOKENS
)
import logging

logger = logging.getLogger(__name__)

if OPENAI_API_KEY and OPENAI_API_KEY != "OPENAI_API_KEY_PLACEHOLDER":
    try:
        openai_model = ChatOpenAI(
            model_name=OPENAI_MODEL, # ChatOpenAI uses model_name
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_OUTPUT_TOKENS, # ChatOpenAI uses max_tokens
            api_key=OPENAI_API_KEY # Parameter name is api_key
        )
        logger.info(f"OpenAI model '{OPENAI_MODEL}' initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI model '{OPENAI_MODEL}': {e}", exc_info=True)
        openai_model = None
else:
    logger.warning("OpenAI API Key is not configured or is a placeholder. Model not initialized.")
    openai_model = None
