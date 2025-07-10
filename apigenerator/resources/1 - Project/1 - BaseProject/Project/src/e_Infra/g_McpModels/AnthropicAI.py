import os
from langchain_anthropic import ChatAnthropic # Correct import for ChatAnthropic
import logging

logger = logging.getLogger(__name__)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_PLACEHOLDER")
anthropic_model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
anthropic_temperature = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))
anthropic_max_output_tokens = int(os.getenv("ANTHROPIC_MAX_OUTPUT_TOKENS", "2048"))

if anthropic_api_key and anthropic_api_key != "ANTHROPIC_API_KEY_PLACEHOLDER":
    try:
        anthropic_model = ChatAnthropic(
            model=anthropic_model_name, # ChatAnthropic uses model or model_name
            temperature=anthropic_temperature,
            max_tokens_to_sample=anthropic_max_output_tokens, # Older SDK versions used this. Newer might use max_tokens.
                                                               # Let's assume max_tokens_to_sample for broader compatibility first,
                                                               # or check specific langchain_anthropic version.
                                                               # For latest, it's often just 'max_tokens'.
                                                               # Given the user snippet did not specify, will use a common one.
                                                               # If issues arise, this param name might need checking against the installed version.
            # max_tokens=anthropic_max_output_tokens, # Use this if max_tokens_to_sample is deprecated/wrong
            api_key=anthropic_api_key # Parameter name is api_key
        )
        logger.info(f"Anthropic model '{anthropic_model_name}' initialized successfully.")
    except Exception as e:
        # Log the specific error, especially if it's about 'max_tokens_to_sample'
        logger.error(f"Failed to initialize Anthropic model '{anthropic_model_name}': {e}", exc_info=True)
        if "max_tokens_to_sample" in str(e).lower() or "max_tokens" in str(e).lower():
            logger.error("This Anthropic error might be related to the 'max_tokens_to_sample' vs 'max_tokens' parameter. Check your langchain_anthropic SDK version.")
        anthropic_model = None
else:
    logger.warning("Anthropic API Key is not configured or is a placeholder. Model not initialized.")
    anthropic_model = None
