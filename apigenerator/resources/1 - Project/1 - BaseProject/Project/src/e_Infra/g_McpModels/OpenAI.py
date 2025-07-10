import os
from langchain_openai import ChatOpenAI # Correct import for ChatOpenAI
import logging

logger = logging.getLogger(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY", "OPENAI_API_KEY_PLACEHOLDER")
openai_model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
openai_max_output_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2000"))

if openai_api_key and openai_api_key != "OPENAI_API_KEY_PLACEHOLDER":
    try:
        openai_model = ChatOpenAI(
            model_name=openai_model_name, # ChatOpenAI uses model_name
            temperature=openai_temperature,
            max_tokens=openai_max_output_tokens, # ChatOpenAI uses max_tokens
            api_key=openai_api_key # Parameter name is api_key
        )
        logger.info(f"OpenAI model '{openai_model_name}' initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI model '{openai_model_name}': {e}", exc_info=True)
        openai_model = None
else:
    logger.warning("OpenAI API Key is not configured or is a placeholder. Model not initialized.")
    openai_model = None
