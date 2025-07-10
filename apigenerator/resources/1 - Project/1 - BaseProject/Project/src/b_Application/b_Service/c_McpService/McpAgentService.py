import os
import logging
import asyncio # Keep for potential future async agent invocation
from typing import List, Dict, Any

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel

# EnvironmentVariables are used by ModelLoader and SpecProviderService now
from src.e_Infra.g_McpModels.ModelLoader import load_model
from .McpTools import ( # Import refactored tools
    find_endpoint,
    analyze_swagger,
    identify_mentioned_params,
    make_curl,
    review_curl
)
from .SpecProviderService import SpecProviderService # New service to get aggregated spec

logger = logging.getLogger(__name__)

class McpAgentService:
    """
    Service to interact with a LangGraph ReAct agent that uses tools
    to understand and answer questions about locally aggregated API specifications.
    """
    _agent_executor = None
    _agent_lock = None # Placeholder for threading.Lock

    def __init__(self):
        """
        Initializes the McpAgentService if not already initialized.
        - Loads the selected LLM.
        - Initializes SpecProviderService to get aggregated API spec and base URL.
        - Prepares the context for tools.
        - Builds the LangGraph agent.
        This constructor should ideally be called once or use a singleton pattern.
        """
        if McpAgentService._agent_lock is None:
            import threading
            McpAgentService._agent_lock = threading.Lock()

        with McpAgentService._agent_lock:
            if McpAgentService._agent_executor is None:
                logger.info("McpAgentService: First initialization. Building agent...")
                try:
                    selected_provider = os.getenv("SELECTED_LLM_PROVIDER", "gemini").lower()
                    self.llm: BaseChatModel = load_model(selected_provider)
                    logger.info(f"LLM loaded: {type(self.llm).__name__} for provider: {selected_provider}")

                    self.spec_provider = SpecProviderService()
                    self.aggregated_spec: Dict[str, Any] = self.spec_provider.get_aggregated_spec()
                    self.api_base_url: str | None = self.spec_provider.get_api_base_url()

                    if not self.aggregated_spec or self.aggregated_spec.get("info", {}).get("title", "").startswith("Error:"):
                        logger.critical(f"Aggregated API specification is missing or contains errors: {self.aggregated_spec.get('info', {}).get('description', 'Unknown spec error')}. Agent tools relying on spec will fail.")
                        # Allow agent to initialize, but tools will likely return errors. Healthcheck should reflect this.
                    else:
                        logger.info(f"Aggregated API spec loaded successfully. Title: {self.aggregated_spec.get('info', {}).get('title', 'N/A')}")

                    if not self.api_base_url:
                        logger.warning("API base URL could not be determined from the spec's 'servers' object. Curl generation might use placeholders.")


                    self.tools = [
                        find_endpoint(self.aggregated_spec), # Pass aggregated_spec as context
                        analyze_swagger(self.aggregated_spec), # Pass aggregated_spec as context
                        identify_mentioned_params(self.aggregated_spec), # Pass aggregated_spec as context
                        make_curl(self.api_base_url), # Pass api_base_url as context
                        review_curl(self.api_base_url)  # Pass api_base_url as context
                    ]
                    logger.info(f"Loaded {len(self.tools)} tools for the agent.")

                    system_prompt_content = (
                        "You are a helpful AI assistant specialized in analyzing API specifications (Swagger/OpenAPI docs) "
                        "and generating curl commands. Your primary goal is to help users understand how to interact with the API "
                        "defined in the provided specification.\n"
                        "You have access to several tools:\n"
                        "- `find_most_relevant_api_endpoint_path`: Given a user's query, find the best matching API endpoint path from the API specification.\n"
                        "- `analyze_endpoint_path_details`: Once an endpoint path is identified, use this to get its details (methods, params, summary).\n"
                        "- `identify_relevant_parameters_in_query`: For a given endpoint path and user query, list parameters mentioned by the user.\n"
                        "- `generate_curl_command`: Use this to create a sample curl command. You'll need the endpoint path, HTTP method, and optionally query parameters and headers.\n"
                        "- `review_and_regenerate_curl_command`: Similar to generate_curl_command, useful for validating/standardizing a command.\n\n"
                        "General workflow:\n"
                        "1. Use `find_most_relevant_api_endpoint_path` to identify the target endpoint based on the user's question.\n"
                        "2. Use `analyze_endpoint_path_details` to understand the details of that endpoint.\n"
                        "3. If the user mentions specific parameters or values, use `identify_relevant_parameters_in_query`.\n"
                        "4. If the user asks for a curl command or how to make a request, use the information gathered to call `generate_curl_command`.\n"
                        "5. Always provide clear, step-by-step explanations if needed.\n"
                        "The API specification is already loaded and available to your tools. Do not ask to fetch or extract it."
                    )
                    # The system message is typically part of the agent's core prompt or passed with messages.
                    # For create_react_agent, it's often implicitly handled by the default prompt,
                    # but we can prepend it to the message list if needed, or ensure the LLM is good at following initial instructions.
                    # Storing it here for potential use if we manually construct message lists.
                    self.system_message_content = system_prompt_content


                    # create_react_agent does not take messages_modifier directly in newer versions.
                    # The system prompt is usually part of the initial messages list or integrated into the LLM prompt.
                    McpAgentService._agent_executor = create_react_agent(model=self.llm, tools=self.tools)
                    logger.info("LangGraph ReAct agent created and cached successfully.")

                except Exception as e:
                    logger.critical(f"Failed to initialize McpAgentService components (LLM, Spec, Tools, Agent): {e}", exc_info=True)
                    McpAgentService._agent_executor = None # Ensure it's None if init fails
                    raise RuntimeError(f"McpAgentService initialization failed critically: {e}") from e

        if McpAgentService._agent_executor is None:
             # This case means initialization failed on first attempt and is being called again.
             raise RuntimeError("McpAgentService could not be initialized. Check logs for critical errors during first setup.")

        # Store references for healthcheck or direct access if needed
        self.llm_for_healthcheck = McpAgentService._agent_executor.nodes["agent"].bound # Accessing the actual LLM
        self.spec_provider_for_healthcheck = self.spec_provider # To check spec status


    def process_message(self, current_history: List[BaseMessage]) -> List[BaseMessage]:
        if not McpAgentService._agent_executor:
            logger.error("Agent executor not available. Service may not have initialized correctly.")
            # This should ideally be caught by the controller trying to get an instance.
            error_response = AIMessage(content="Error: The agent service is not available. Please check server logs.")
            return current_history + [error_response]

        if not current_history or not isinstance(current_history[-1], HumanMessage):
            logger.error("process_message called without a valid HumanMessage at the end of history.")
            error_response = AIMessage(content="Error: Invalid message history provided to agent.")
            return current_history + [error_response]

        logger.info(f"Processing message with agent. History length: {len(current_history)}. Last message: '{current_history[-1].content[:100]}'")

        # Prepend system message if not intrinsically part of the agent's default prompt structure.
        # For many ReAct agents, the initial instruction/persona comes from the system message in the history.
        messages_for_agent = [SystemMessage(content=self.system_message_content)] + current_history

        try:
            config = {"configurable": {"session_id": "mcp_global_session"}} # Using a fixed session_id for statelessness for now
            result = McpAgentService._agent_executor.invoke({"messages": messages_for_agent}, config=config)

            response_messages = result.get("messages", [])
            # Filter out the prepended SystemMessage from the final history if it was added here
            # Or, if the agent itself adds it, that's fine.
            # For now, assuming the agent returns the full history including the system message if it used it.
            # The important part is that the AIMessage is the last one.
            logger.info(f"Agent invocation successful. Agent returned {len(response_messages)} total messages.")
            return response_messages

        except Exception as e:
            logger.error(f"Error during agent invocation: {e}", exc_info=True)
            error_response = AIMessage(content=f"Sorry, an error occurred while processing your request with the agent: {str(e)}")
            return current_history + [error_response] # Return original history + error AIMessage
