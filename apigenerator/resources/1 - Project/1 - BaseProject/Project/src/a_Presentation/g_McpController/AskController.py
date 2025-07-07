from flask import Blueprint, request, jsonify # current_app no longer needed here directly
import logging
from typing import List # For type hinting BaseMessage list
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

# Import the new McpAgentService and ModelLoader (for healthcheck)
from src.b_Application.b_Service.c_McpService.McpAgentService import McpAgentService
from src.e_Infra.g_McpModels.ModelLoader import load_model, CURRENT_CONFIGURED_MODEL_NAME
from src.e_Infra.g_Environment.EnvironmentVariables import SELECTED_LLM_PROVIDER, BASE_URL, ENDPOINTS


logger = logging.getLogger(__name__)
ask_bp = Blueprint('ask_bp', __name__)

# Initialize service instance once, potentially.
# However, if its internal state (like agent or context) could become stale or
# if it's very lightweight to instantiate, creating per request is also an option.
# For an agent that might load specs or models, once per app context or on first use is better.
# Let's try lazy instantiation on first request for now.
mcp_agent_service_instance: McpAgentService = None

def get_mcp_agent_service():
    global mcp_agent_service_instance
    if mcp_agent_service_instance is None:
        logger.info("First request to /mcp/ask, initializing McpAgentService...")
        try:
            mcp_agent_service_instance = McpAgentService()
            logger.info("McpAgentService initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize McpAgentService during first use: {e}", exc_info=True)
            mcp_agent_service_instance = None # Ensure it remains None if init fails
            raise # Re-raise to signal critical failure at controller level
    return mcp_agent_service_instance

@ask_bp.route('/ask', methods=['POST'])
def ask_mcp_agent():
    """
    Handles natural language questions using the MCP Agent.
    Also provides a healthcheck for the configured LLM model initialization.
    """
    data = request.get_json()
    if not data or 'question' not in data:
        logger.warning("'/ask' endpoint called with missing 'question' in payload.")
        return jsonify({"error": "Missing 'question' in request payload"}), 400

    question_text = data['question']

    # --- Healthcheck Logic ---
    if question_text.lower() == "healthcheck":
        logger.info("Healthcheck requested for /mcp/ask.")
        # Try to load the model as a basic health indicator for the selected provider
        # This also implicitly checks if API key is valid (or not a placeholder)
        # and if BASE_URL/ENDPOINTS are set (as McpAgentService init might use them for tool context).
        provider_to_check = SELECTED_LLM_PROVIDER # From EnvironmentVariables
        model_to_check = None
        status = "no"
        reason = ""
        try:
            # Attempt to get service, which initializes model and tools context
            service_for_healthcheck = get_mcp_agent_service() # This will try to init the agent
            if service_for_healthcheck and service_for_healthcheck.llm: # Check if LLM loaded
                 # The tools also need valid context (BASE_URL, ENDPOINTS)
                if not service_for_healthcheck.context.get("base_url") or not service_for_healthcheck.context.get("endpoints"):
                    reason = "BASE_URL or ENDPOINTS not configured for tools."
                    logger.warning(f"Healthcheck: {reason}")
                else:
                    # A more thorough healthcheck for the agent might try a dummy invoke or check tools.
                    # For now, successful McpAgentService init (which loads model and prepares tools) is a good sign.
                    status = "yes"
                    reason = f"McpAgentService initialized successfully with {provider_to_check}."
                    logger.info(f"Healthcheck: {reason}")
            else: # Should not happen if get_mcp_agent_service raises on failure
                reason = f"LLM for provider '{provider_to_check}' (model: {CURRENT_CONFIGURED_MODEL_NAME or 'Unknown'}) failed to initialize properly."
                logger.warning(f"Healthcheck: {reason}")

        except ValueError as ve: # Config errors from ModelLoader or McpAgentService init
            logger.error(f"Healthcheck: Configuration error for provider '{provider_to_check}': {ve}", exc_info=True)
            reason = f"Configuration error for {provider_to_check}: {ve}"
        except RuntimeError as re: # Critical errors during service/agent init
            logger.error(f"Healthcheck: Runtime error initializing service for '{provider_to_check}': {re}", exc_info=True)
            reason = f"Runtime error initializing service for {provider_to_check}: {re}"
        except Exception as e:
            logger.error(f"Healthcheck: Unexpected error for provider '{provider_to_check}': {e}", exc_info=True)
            reason = f"An unexpected error occurred: {str(e)}"

        return jsonify({
            "answer": status,
            "provider_checked": provider_to_check,
            "model_configured": CURRENT_CONFIGURED_MODEL_NAME if status == "yes" else "N/A due to error",
            "reason": reason if status == "no" else "OK"
        }), 200

    # --- Standard Question Logic ---
    # For now, we'll use a stateless approach for history per request.
    # A more advanced version would use Flask sessions or a DB to maintain history.
    # The SystemMessage is part of the agent built by McpAgentService.

    history: List[BaseMessage] = [HumanMessage(content=question_text)]

    try:
        service = get_mcp_agent_service()
        if not service: # Should have been caught by healthcheck's attempt or raised earlier
             return jsonify({"error": "MCP Agent Service is not available due to initialization errors."}), 503

        response_messages = service.process_message(history)

        ai_reply = "Sorry, I couldn't generate a response." # Default if no AIMessage found
        if response_messages:
            # Find the last AIMessage in the response
            for msg in reversed(response_messages):
                if isinstance(msg, AIMessage):
                    ai_reply = msg.content
                    break

        return jsonify({"answer": ai_reply}), 200

    except ValueError as ve: # Config errors if somehow not caught by healthcheck logic / first use
        logger.error(f"LLM Service configuration error for question processing: {ve}", exc_info=True)
        return jsonify({"error": f"LLM Service not configured correctly: {ve}"}), 503
    except RuntimeError as re: # Errors from McpAgentService initialization or processing
        logger.error(f"MCP Agent Service runtime error: {re}", exc_info=True)
        return jsonify({"error": f"An error occurred while processing your question with the agent: {re}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in /ask endpoint: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred."}), 500

# Configuration routes are removed as per the new design focusing on env vars.
# The old /ask/configure GET and POST functions are deleted.

# Note on imports:
# Ensure all necessary langchain components (messages, tools, agent creation)
# and your custom modules (McpAgentService, ModelLoader, EnvironmentVariables)
# are correctly structured and importable.
# The `from . import McpTools` in McpAgentService assumes McpTools.py is in the same directory.
# If `current_app` was used by PathResolver, it would need to be available, but PathResolver was removed.
# McpTools now has its own root path detection.
