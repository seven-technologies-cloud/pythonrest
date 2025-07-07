# This package groups all MCP (Multi-LLM Chat/Query Platform) related infrastructure services.

# Re-export key classes for easier access from higher application/presentation layers.
from .a_ConfigManager.LlmConfigManager import LlmConfigManager
from .b_LlmManager.LlmServiceBase import LlmServiceBase
from .b_LlmManager.LlmServiceFactory import LlmServiceFactory
# Individual LLM services can also be re-exported if they are ever needed directly,
# but typically the factory or the base class are the primary interfaces from outside.
# from .c_GeminiClient.GeminiService import GeminiService
# from .d_OpenAIClient.OpenAIService import OpenAIService
# from .e_AnthropicClient.AnthropicService import AnthropicService

__all__ = [
    "LlmConfigManager",
    "LlmServiceBase",
    "LlmServiceFactory",
    # "GeminiService", # Add if re-exported
    # "OpenAIService", # Add if re-exported
    # "AnthropicService" # Add if re-exported
]
