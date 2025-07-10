# System Imports #
import os

# ------------------------------------------ Database ------------------------------------------ #

# Database start configuration #

# Configuration for database connection #


# ------------------------------------------ Domain ------------------------------------------ #

# UID Generation Type #

# Filter generation environment variables #
os.environ['domain_like_left'] = ''
os.environ['domain_like_right'] = ''
os.environ['domain_like_full'] = ''

# Datetime valid masks #
os.environ['date_valid_masks'] = "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y"
os.environ['time_valid_masks'] = "%H:%M:%S, %I:%M:%S %p, %H:%M, %I:%M %p, %I:%M:%S%p, %I:%M%p, %H:%M:%S%z, %I:%M:%S %p%z, %H:%M%z, %I:%M %p%z, %I:%M:%S%p%z, %I:%M%p%z, %H:%M:%S.%f, %I:%M:%S.%f %p, %H:%M:%S.%f%z, %I:%M:%S.%f %p%z, %H:%M:%S.%fZ, %I:%M:%S.%f %pZ, %H:%M:%S.%f %Z, %I:%M:%S.%f %p %Z"

os.environ['query_limit'] = '*'

# ------------------------------------------ Trace ------------------------------------------ #

# Comment this variable bellow for NO STACKTRACE (production mode off) #
os.environ['display_stacktrace_on_error'] = 'False'

# ------------------------------------------ Origins ------------------------------------------ #

# Origins enabled #
os.environ['origins'] = '*'
os.environ['headers'] = '*'

# ------------------------------------------ MCP ------------------------------------------ #

os.environ['GEMINI_API_KEY'] = 'mock-gemini-api-key'
os.environ['OPENAI_API_KEY'] = 'mock-openai-api-key'
os.environ['ANTHROPIC_API_KEY'] = 'mock-anthropic-api-key'

os.environ['GEMINI_MODEL'] = 'gemini-2.5-flash'
os.environ['OPENAI_MODEL'] = 'gpt-4-turbo'
os.environ['ANTHROPIC_MODEL'] = 'claude-3-opus'

os.environ['GEMINI_TEMPERATURE'] = '0.6'
os.environ['OPENAI_TEMPERATURE'] = '0.7'
os.environ['ANTHROPIC_TEMPERATURE'] = '0.9'

os.environ['GEMINI_MAX_OUTPUT_TOKENS'] = '1024'
os.environ['OPENAI_MAX_OUTPUT_TOKENS'] = '2048'
os.environ['ANTHROPIC_MAX_OUTPUT_TOKENS'] = '4096'

os.environ['SELECTED_LLM_PROVIDER'] = 'gemini'

os.environ['LLM_CONFIG_FILE_PATH'] = 'config/llm_config.json'

ENV_DEFAULT_LLM_PROVIDER = 'SELECTED_LLM_PROVIDER'
ENV_DEFAULT_GEMINI_MODEL_NAME = 'GEMINI_MODEL'
ENV_DEFAULT_OPENAI_MODEL_NAME = 'OPENAI_MODEL'
ENV_DEFAULT_ANTHROPIC_MODEL_NAME = 'ANTHROPIC_MODEL'
ENV_DEFAULT_GEMINI_TEMPERATURE = 'GEMINI_TEMPERATURE'
ENV_DEFAULT_OPENAI_TEMPERATURE = 'OPENAI_TEMPERATURE'
ENV_DEFAULT_ANTHROPIC_TEMPERATURE = 'ANTHROPIC_TEMPERATURE'