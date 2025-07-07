import yaml # For PyYAML
import json # For JSON if needed
import os
import logging
# Now depends on the LlmServiceBase interface, re-exported by g_McpInfra
from src.e_Infra.g_McpInfra import LlmServiceBase

# Configure logging for this module
logger = logging.getLogger(__name__)

class ApiQueryService:
    """
    Service to answer questions about an API using its OpenAPI specification
    and a configured generative AI model through LlmServiceBase.
    """
    def __init__(self, llm_service: LlmServiceBase, openapi_spec_path: str):
        """
        Initializes the ApiQueryService.

        Args:
            llm_service (LlmServiceBase): An instance of a class that implements LlmServiceBase
                                          (e.g., GeminiService, OpenAIService, AnthropicService).
            openapi_spec_path (str): The file path to the OpenAPI specification (YAML or JSON).
        """
        if not isinstance(llm_service, LlmServiceBase):
            logger.error("Invalid LLM service instance provided to ApiQueryService. Must implement LlmServiceBase.")
            raise TypeError("llm_service must be an instance of a class implementing LlmServiceBase.")
        if not openapi_spec_path:
            logger.error("OpenAPI spec path not provided to ApiQueryService.")
            raise ValueError("openapi_spec_path must be provided.")

        self.llm_service = llm_service
        self.openapi_spec_path = openapi_spec_path
        self.api_spec = None  # Will be loaded by _load_and_parse_openapi_spec()
        self._load_and_parse_openapi_spec() # Load spec during initialization

    def _load_and_parse_openapi_spec(self):
        """
        Loads and parses the OpenAPI specification file.
        Supports both YAML and JSON file formats.
        """
        if not os.path.exists(self.openapi_spec_path):
            logger.error(f"OpenAPI spec file not found at: {self.openapi_spec_path}")
            raise FileNotFoundError(f"OpenAPI spec file not found at: {self.openapi_spec_path}")

        try:
            with open(self.openapi_spec_path, 'r', encoding='utf-8') as f:
                if self.openapi_spec_path.endswith(('.yaml', '.yml')):
                    self.api_spec = yaml.safe_load(f)
                elif self.openapi_spec_path.endswith('.json'):
                    self.api_spec = json.load(f)
                else:
                    logger.error(f"Unsupported OpenAPI spec file format: {self.openapi_spec_path}. Must be YAML or JSON.")
                    raise ValueError("Unsupported OpenAPI spec file format. Must be YAML or JSON.")
            logger.info(f"OpenAPI spec loaded and parsed successfully from: {self.openapi_spec_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML OpenAPI spec from {self.openapi_spec_path}: {e}", exc_info=True)
            raise ValueError(f"Error parsing YAML OpenAPI spec: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON OpenAPI spec from {self.openapi_spec_path}: {e}", exc_info=True)
            raise ValueError(f"Error parsing JSON OpenAPI spec: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading/parsing OpenAPI spec from {self.openapi_spec_path}: {e}", exc_info=True)
            raise RuntimeError(f"Could not load or parse OpenAPI spec: {e}")

    def answer_api_question(self, question: str) -> str:
        """
        Answers a question about the API using the loaded OpenAPI spec and Gemini.

        Args:
            question (str): The user's question about the API.

        Returns:
            str: The generated answer.

        Raises:
            RuntimeError: If the API spec is not loaded or if Gemini interaction fails.
        """
        if self.api_spec is None:
            logger.error("API spec is not loaded. Cannot answer question.")
            # Attempt to reload if it wasn't loaded during init for some reason (defensive)
            try:
                self._load_and_parse_openapi_spec()
                if self.api_spec is None: # Still None after attempting reload
                     raise RuntimeError("API specification is not loaded. Cannot answer questions.")
            except Exception as e:
                 raise RuntimeError(f"API specification is not loaded and failed to reload: {e}. Cannot answer questions.")


        if not question:
            logger.warning("Answer_api_question called with an empty question.")
            return "Please provide a question about the API."

        # Construct a prompt for Gemini.
        # This is a crucial part and might need significant refinement for good results.
        # For now, a simple approach: include parts of the spec and the question.
        # A more advanced approach might involve:
        # - Summarizing the spec or extracting relevant sections based on keywords in the question.
        # - Few-shot prompting if you have examples of questions and good answers.

        # Limiting the spec size to avoid overly long prompts.
        # Convert spec to string (JSON is usually more compact for this).
        try:
            spec_str = json.dumps(self.api_spec, indent=2)
            if len(spec_str) > 10000: # Arbitrary limit, adjust as needed
                spec_str = spec_str[:10000] + "\n... (specification truncated)"
        except Exception as e:
            logger.error(f"Could not serialize API spec to string for prompt: {e}")
            spec_str = "Error: Could not serialize API specification."


        prompt = f"""You are an expert AI assistant knowledgeable about a specific API.
Your task is to answer questions about this API based on its OpenAPI specification.

Here is the OpenAPI specification (or a relevant part of it):
--- START OF API SPECIFICATION ---
{spec_str}
--- END OF API SPECIFICATION ---

User's question: "{question}"

Based on the provided API specification and the user's question, please provide a clear, concise, and accurate answer.
If the information is not available in the specification, state that clearly.
Do not make up information not present in the spec.
"""

        try:
            answer = self.llm_service.generate_text(prompt) # Use the generic llm_service
            logger.info(f"Successfully generated answer for question: '{question}' using {type(self.llm_service).__name__}")
            return answer
        except RuntimeError as e: # Catch errors from the LlmServiceBase implementations
            logger.error(f"Failed to get answer from LLM service ({type(self.llm_service).__name__}) for question '{question}': {e}", exc_info=True)
            raise RuntimeError(f"Could not get an answer from the AI service ({type(self.llm_service).__name__}): {e}")
        except Exception as e:
            logger.error(f"Unexpected error in answer_api_question for question '{question}': {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred while trying to answer the question: {e}")

# Example usage (for illustration):
# if __name__ == '__main__':
#     # This requires GEMINI_API_KEY and a dummy openapi.yaml/json in the root or specified path.
#     # Create a dummy openapi.yaml for testing
#     dummy_spec_content = {
#         "openapi": "3.0.0",
#         "info": {"title": "Dummy API", "version": "1.0.0"},
#         "paths": {
#             "/items": {
#                 "get": {"summary": "List all items", "responses": {"200": {"description": "A list of items"}}},
#                 "post": {"summary": "Create a new item"}
#             },
#             "/items/{itemId}": {
#                 "get": {"summary": "Get an item by ID"},
#                 "parameters": [{"name": "itemId", "in": "path", "required": True, "schema": {"type": "integer"}}]
#             }
#         }
#     }
#     with open("dummy_openapi.yaml", "w") as f:
#         yaml.dump(dummy_spec_content, f)
#
#     from src.e_Infra.CustomVariables import GEMINI_API_KEY, OPENAPI_SPEC_PATH
#
#     if not GEMINI_API_KEY:
#         print("Please set the GEMINI_API_KEY environment variable.")
#     else:
#         try:
#             gemini_svc = GeminiService(api_key=GEMINI_API_KEY)
#             # Use the OPENAPI_SPEC_PATH from CustomVariables if it points to the dummy, or override path here
#             # query_svc = ApiQueryService(gemini_service=gemini_svc, openapi_spec_path=OPENAPI_SPEC_PATH)
#             query_svc = ApiQueryService(gemini_service=gemini_svc, openapi_spec_path="dummy_openapi.yaml")
#
#             print("ApiQueryService initialized.")
#
#             test_question = "What can I do with /items?"
#             # test_question = "How do I get a specific item?"
#             # test_question = "Is there an endpoint for users?"
#
#             print(f"Asking: {test_question}")
#             api_answer = query_svc.answer_api_question(test_question)
#             print(f"Answer: {api_answer}")
#
#         except Exception as e:
#             print(f"An error occurred during example usage: {e}")
#         finally:
#             if os.path.exists("dummy_openapi.yaml"):
#                 os.remove("dummy_openapi.yaml")
