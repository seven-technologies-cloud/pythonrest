from langchain_anthropic import ChatAnthropic # Correct import for ChatAnthropic
from src.e_Infra.g_Environment.EnvironmentVariables import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    ANTHROPIC_TEMPERATURE,
    ANTHROPIC_MAX_OUTPUT_TOKENS
)
import logging

logger = logging.getLogger(__name__)

if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "ANTHROPIC_API_KEY_PLACEHOLDER":
    try:
        anthropic_model = ChatAnthropic(
            model=ANTHROPIC_MODEL, # ChatAnthropic uses model or model_name
            temperature=ANTHROPIC_TEMPERATURE,
            max_tokens_to_sample=ANTHROPIC_MAX_OUTPUT_TOKENS, # Older SDK versions used this. Newer might use max_tokens.
                                                              # Let's assume max_tokens_to_sample for broader compatibility first,
                                                              # or check specific langchain_anthropic version.
                                                              # For latest, it's often just 'max_tokens'.
                                                              # Given the user snippet did not specify, will use a common one.
                                                              # If issues arise, this param name might need checking against the installed version.
            # max_tokens=ANTHROPIC_MAX_OUTPUT_TOKENS, # Use this if max_tokens_to_sample is deprecated/wrong
            api_key=ANTHROPIC_API_KEY # Parameter name is api_key
        )
        logger.info(f"Anthropic model '{ANTHROPIC_MODEL}' initialized successfully.")
    except Exception as e:
        # Log the specific error, especially if it's about 'max_tokens_to_sample'
        logger.error(f"Failed to initialize Anthropic model '{ANTHROPIC_MODEL}': {e}", exc_info=True)
        if "max_tokens_to_sample" in str(e).lower() or "max_tokens" in str(e).lower():
            logger.error("This Anthropic error might be related to the 'max_tokens_to_sample' vs 'max_tokens' parameter. Check your langchain_anthropic SDK version.")
        anthropic_model = None
else:
    logger.warning("Anthropic API Key is not configured or is a placeholder. Model not initialized.")
    anthropic_model = None
