# System Imports #
import os

# ------------------------------------------ Database ------------------------------------------ #

# Database start configuration #
os.environ['main_db_conn'] = 'pgsql'

# Configuration for database connection #
os.environ['pgsql_user'] = 'seven-technologies-web-app_owner'
os.environ['pgsql_password'] = 'npg_mAO6G3TCyiqJ'
os.environ['pgsql_host'] = 'ep-delicate-boat-ackruksg-pooler.sa-east-1.aws.neon.tech'
os.environ['pgsql_port'] = '5432'
os.environ['pgsql_database_name'] = 'seven-technologies-web-app'
os.environ['pgsql_schema'] = 'public'


# ------------------------------------------ Domain ------------------------------------------ #

# UID Generation Type #
os.environ['id_generation_method'] = 'ulid'

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

# ------------------------------------------ MCP  ------------------------------------------ #
GEMINI_API_KEY = "mock-gemini-api-key"
OPENAI_API_KEY = "mock-openai-api-key"
ANTHROPIC_API_KEY = "mock-anthropic-api-key"

GEMINI_MODEL = "gemini-2.5-flash"
OPENAI_MODEL = "gpt-4-turbo"
ANTHROPIC_MODEL = "claude-3-opus"

GEMINI_TEMPERATURE = 0.6
OPENAI_TEMPERATURE = 0.7
ANTHROPIC_TEMPERATURE = 0.9

GEMINI_MAX_OUTPUT_TOKENS = 1024
OPENAI_MAX_OUTPUT_TOKENS = 2048
ANTHROPIC_MAX_OUTPUT_TOKENS = 4096

SELECTED_LLM_PROVIDER = "gemini"

# Caminho para o arquivo de configuração do LLM
os.environ['LLM_CONFIG_FILE_PATH'] = 'config/llm_config.json'

# Nomes das variáveis de ambiente para configurações padrão do LLM
ENV_DEFAULT_LLM_PROVIDER = 'SELECTED_LLM_PROVIDER'
ENV_DEFAULT_GEMINI_MODEL_NAME = 'GEMINI_MODEL'
ENV_DEFAULT_OPENAI_MODEL_NAME = 'OPENAI_MODEL'
ENV_DEFAULT_ANTHROPIC_MODEL_NAME = 'ANTHROPIC_MODEL'
ENV_DEFAULT_GEMINI_TEMPERATURE = 'GEMINI_TEMPERATURE'
ENV_DEFAULT_OPENAI_TEMPERATURE = 'OPENAI_TEMPERATURE'
ENV_DEFAULT_ANTHROPIC_TEMPERATURE = 'ANTHROPIC_TEMPERATURE'

