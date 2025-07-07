import logging
import asyncio
from typing import List, Dict, Any

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel # For type hinting

# Assuming EnvironmentVariables.py is in src.e_Infra.g_Environment
from src.e_Infra.g_Environment.EnvironmentVariables import (
    SELECTED_LLM_PROVIDER,
    BASE_URL,
    ENDPOINTS
)
# Assuming ModelLoader.py is in src.e_Infra.g_McpModels
from src.e_Infra.g_McpModels.ModelLoader import load_model
# Assuming McpTools.py is in the same directory or package
from . import McpTools # Use relative import if McpTools is in the same package

logger = logging.getLogger(__name__)

class McpAgentService:
    """
    Service to interact with a LangGraph ReAct agent that uses tools
    to understand and answer questions about API specifications.
    """
    def __init__(self):
        """
        Initializes the McpAgentService.
        - Loads LLM configuration from environment variables.
        - Loads the selected LLM.
        - Prepares the context for tools.
        - Builds the LangGraph agent.
        """
        logger.info("Initializing McpAgentService...")

        self.context: Dict[str, Any] = {
            "base_url": BASE_URL,
            "endpoints": ENDPOINTS
        }
        logger.info(f"Tool context initialized with BASE_URL: '{self.context['base_url']}' and {len(self.context['endpoints'])} endpoint(s).")
        if not self.context["base_url"] or not self.context["endpoints"]:
            logger.warning("BASE_URL or ENDPOINTS are not configured in environment variables. Swagger extraction tools may fail.")
            # Allow initialization to continue, but tools will likely error out.

        try:
            self.llm: BaseChatModel = load_model(SELECTED_LLM_PROVIDER)
            logger.info(f"LLM loaded: {type(self.llm).__name__} for provider: {SELECTED_LLM_PROVIDER}")
        except ValueError as e:
            logger.critical(f"Failed to load LLM for provider '{SELECTED_LLM_PROVIDER}': {e}. McpAgentService cannot operate.", exc_info=True)
            # This is a critical failure; the service is unusable.
            raise RuntimeError(f"LLM initialization failed for provider '{SELECTED_LLM_PROVIDER}': {e}") from e


        self.tools = [
            McpTools.extract_swagger_spec(self.context),
            McpTools.find_endpoint(self.context),
            McpTools.analyze_swagger(self.context),
            McpTools.identify_mentioned_params(self.context),
            McpTools.make_curl(self.context),
            McpTools.review_curl(self.context)
        ]
        logger.info(f"Loaded {len(self.tools)} tools for the agent.")

        # Define the system message/prompt for the ReAct agent
        # Using f-string to dynamically insert endpoint list if it's short, or a summary
        endpoints_summary = str(self.context['endpoints'])
        if len(endpoints_summary) > 200: # Truncate if too long for system message
            endpoints_summary = endpoints_summary[:200] + "..."

        system_prompt_content = (
            "You are a helpful AI assistant specialized in analyzing API specifications (Swagger/OpenAPI docs) "
            "and generating curl commands. Your primary goal is to help users understand how to interact with the API.\n"
            "You have access to several tools:\n"
            "- `extract_swagger_specifications`: Use this first if you suspect the local API spec cache is missing or stale. It fetches and saves the latest specs.\n"
            "- `find_most_relevant_api_endpoint`: Given a user's query, find the best matching API endpoint path from the cached specs.\n"
            "- `analyze_endpoint_specification`: Once an endpoint path is identified, use this to get its details (methods, params, summary).\n"
            "- `identify_relevant_parameters_in_query`: For a given endpoint and user query, list parameters mentioned by the user.\n"
            "- `generate_curl_command`: Use this to create a sample curl command. You'll need the endpoint path, HTTP method, and optionally query parameters and headers.\n"
            "- `review_and_regenerate_curl_command`: Similar to generate_curl_command, useful for validating/standardizing a command.\n\n"
            "General workflow:\n"
            "1. If unsure about current API specs, use `extract_swagger_specifications`.\n"
            "2. Use `find_most_relevant_api_endpoint` to identify the target endpoint based on the user's question.\n"
            "3. Use `analyze_endpoint_specification` to understand the details of that endpoint.\n"
            "4. If the user mentions specific parameters or values, use `identify_relevant_parameters_in_query`.\n"
            "5. If the user asks for a curl command or how to make a request, use the information gathered to call `generate_curl_command`.\n"
            "6. Always provide clear, step-by-step explanations if needed.\n"
            f"The known base endpoints this API interacts with are generally related to: {endpoints_summary}\n"
            "If a user asks a general question like 'What is this API about?', first try to extract specs, then analyze a primary endpoint if one seems obvious, or summarize available endpoints."
        )
        self.system_message = SystemMessage(content=system_prompt_content)

        try:
            self.agent_executor = create_react_agent(model=self.llm, tools=self.tools, messages_modifier=self.system_message)
            logger.info("LangGraph ReAct agent created successfully.")
        except Exception as e:
            logger.critical(f"Failed to create LangGraph ReAct agent: {e}", exc_info=True)
            raise RuntimeError(f"Agent creation failed: {e}") from e


    def process_message(self, current_history: List[BaseMessage]) -> List[BaseMessage]:
        """
        Processes a list of messages (including the latest user message) with the agent.
        Langchain's ReAct agent typically expects the full message history.

        Args:
            current_history (List[BaseMessage]): The conversation history, ending with the latest HumanMessage.

        Returns:
            List[BaseMessage]: The updated conversation history including the agent's response(s).
        """
        if not current_history or not isinstance(current_history[-1], HumanMessage):
            logger.error("process_message called without a valid HumanMessage at the end of history.")
            # Return an AIMessage indicating error, appended to history
            error_response = AIMessage(content="Error: Invalid message history provided to agent.")
            return current_history + [error_response]

        logger.info(f"Processing message with agent. History length: {len(current_history)}. Last message: '{current_history[-1].content[:100]}'")

        # The ReAct agent created by `create_react_agent` is usually invoked with a dict like {"messages": ...}
        # It should handle the SystemMessage internally as it was passed during creation.
        # If `messages_modifier` was used with a SystemMessage, it prepends it.
        # If not, and the agent expects system message in the list, we might need to add it:
        # full_messages_for_agent = [self.system_message] + current_history # If system_message not part of agent itself
        # For create_react_agent with messages_modifier, just pass current_history.

        try:
            # LangGraph agents are often async. If this one is, and we're in a sync Flask route,
            # we need to run it appropriately.
            # For simplicity, assuming .invoke() is available and synchronous, or that create_react_agent
            # provides a synchronous invocation method if the underlying model/tools are sync.
            # If it's strictly async, we'd need asyncio.run() or similar if called from sync code.
            # Let's assume for now that the agent can be invoked synchronously or we handle async if needed.

            # The default create_react_agent is async.
            # To call from sync Flask, we'd typically use asyncio.run()
            # However, running asyncio.run() repeatedly in a web server request can be problematic.
            # It's better if the web server itself is async (e.g. Uvicorn with Quart/FastAPI)
            # or if there's a sync wrapper for the agent.
            # For now, let's try a direct invoke and see. If it's an async runnable, this will error.
            # Most Langchain runnables have .invoke() and .ainvoke()

            # Using .invoke for synchronous execution
            config = {"configurable": {"session_id": "mcp_session"}} # Example config, session ID might be useful for some agents
            result = self.agent_executor.invoke({"messages": current_history}, config=config)

            # The result from a create_react_agent graph is typically a dict with "messages" key
            response_messages = result.get("messages", [])
            logger.info(f"Agent invocation successful. Got {len(response_messages) - len(current_history)} new message(s).")
            return response_messages # This should be the full history including new AIMessage(s)

        except Exception as e:
            logger.error(f"Error during agent invocation: {e}", exc_info=True)
            error_response = AIMessage(content=f"Sorry, an error occurred while processing your request: {str(e)}")
            return current_history + [error_response]


# Example for standalone testing (not run by Flask app)
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     # Ensure Environment Variables are set (e.g., GOOGLE_API_KEY, SELECTED_LLM_PROVIDER, BASE_URL, ENDPOINTS)
#     # Example:
#     # os.environ["SELECTED_LLM_PROVIDER"] = "gemini" # or "openai", "anthropic"
#     # os.environ["GEMINI_API_KEY"] = "YOUR_KEY_HERE"
#     # os.environ["BASE_URL"] = "http://localhost:8080" # Your target API's base URL
#     # os.environ["ENDPOINTS"] = "[\"/api/users\", \"/api/products\"]" # List of swagger.json paths relative to /swagger

#     if not BASE_URL or not ENDPOINTS or not SELECTED_LLM_PROVIDER:
#         print("Please set BASE_URL, ENDPOINTS, and SELECTED_LLM_PROVIDER environment variables for testing.")
#     else:
#         try:
#             service = McpAgentService()
#             print("McpAgentService initialized.")
#             print("Agent System Prompt:\n", service.system_message.content)

#             history: List[BaseMessage] = []

#             # First, let's try to extract swagger if cache is empty
#             print("\nSimulating first call to extract swagger:")
#             history.append(HumanMessage(content="Can you make sure you have the latest API specs?"))
#             history = service.process_message(history)
#             print("Agent response after extraction attempt:")
#             for msg in history:
#                 print(f"  {msg.type.upper()}: {msg.content}")

#             print("\nNow, asking a question about the API:")
#             # history.append(HumanMessage(content="What can you tell me about the /api/users endpoint?"))
#             history.append(HumanMessage(content="How do I get a list of products?"))
#             history = service.process_message(history)

#             print("\nConversation History:")
#             for msg in history:
#                 print(f"  {msg.type.upper()}: {msg.content}")

#             print("\nAsking for a curl command:")
#             history.append(HumanMessage(content="Generate a curl command to get all products."))
#             history = service.process_message(history)

#             print("\nConversation History:")
#             for msg in history:
#                 print(f"  {msg.type.upper()}: {msg.content}")

#         except RuntimeError as e:
#             print(f"Service Initialization Error: {e}")
#         except ValueError as e:
#             print(f"Configuration Error: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
