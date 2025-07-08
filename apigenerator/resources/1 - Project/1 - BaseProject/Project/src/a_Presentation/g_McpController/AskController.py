import os
from flask import Blueprint, request, jsonify
import logging
from typing import List, Dict # For type hinting BaseMessage list
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

# Import the new McpAgentService
from src.b_Application.b_Service.c_McpService.McpAgentService import McpAgentService
# For healthcheck, to log which provider/model is configured
# ModelLoader might not be needed here if McpAgentService handles its own model status for healthcheck

logger = logging.getLogger(__name__)
ask_bp = Blueprint('ask_bp', __name__)

# Lazy initialization for McpAgentService
_mcp_agent_service_instance: McpAgentService = None
_mcp_agent_service_init_error: Exception = None

def get_mcp_agent_service() -> McpAgentService:
    global _mcp_agent_service_instance, _mcp_agent_service_init_error
    if _mcp_agent_service_instance is None and _mcp_agent_service_init_error is None:
        logger.info("First request or retry after error: Initializing McpAgentService...")
        try:
            _mcp_agent_service_instance = McpAgentService()
            logger.info("McpAgentService initialized successfully for AskController.")
        except Exception as e:
            _mcp_agent_service_init_error = e
            logger.critical(f"Failed to initialize McpAgentService for AskController: {e}", exc_info=True)
            # Do not raise here; let endpoint handle it to return proper HTTP error

    if _mcp_agent_service_init_error:
        # If there was an init error on previous attempt, raise it so each request doesn't retry indefinitely
        # if the error is persistent (e.g. bad API key).
        # For some errors, we might want a retry mechanism, but for now, fail fast after first error.
        raise RuntimeError(f"McpAgentService previously failed to initialize: {_mcp_agent_service_init_error}")

    if _mcp_agent_service_instance is None : # Should be caught by the raise above if error occurred
         raise RuntimeError("McpAgentService is not available and no initialization error was caught. This state should not be reached.")

    return _mcp_agent_service_instance

@ask_bp.route('/ask', methods=['POST'])
def ask_mcp_agent():
    """
    Handles natural language questions using the MCP LangGraph Agent.
    Also provides a healthcheck for the agent's core components.
    """
    data = request.get_json()
    if not data or 'question' not in data:
        logger.warning("'/ask' endpoint called with missing 'question' in payload.")
        return jsonify({"error": "Missing 'question' in request payload"}), 400

    question_text = data['question']

    # --- Healthcheck Logic ---
    if question_text.lower() == "healthcheck":
        logger.info("Healthcheck requested for /mcp/ask.")
        health_status = {"answer": "no", "provider_configured": os.getenv("SELECTED_LLM_PROVIDER", "Not Set"), "details": ""}
        try:
            service = get_mcp_agent_service() # This attempts initialization

            # Check LLM (part of agent)
            if service.llm_for_healthcheck: # Accessing the LLM instance from the agent service
                health_status["llm_status"] = f"{type(service.llm_for_healthcheck).__name__} loaded."
            else: # Should not happen if service init succeeded without error
                health_status["llm_status"] = "LLM instance not found in service (unexpected)."
                health_status["details"] += "LLM instance missing post-initialization. "

            # Check Spec Provider & aggregated spec
            if service.spec_provider_for_healthcheck:
                spec = service.spec_provider_for_healthcheck.get_aggregated_spec()
                if spec and spec.get("info", {}).get("title", "").startswith("Error:"):
                    health_status["spec_status"] = f"Error state: {spec.get('info', {}).get('title')}"
                    health_status["details"] += f"Spec aggregation issue: {spec.get('info', {}).get('description', '')}. "
                elif spec and spec.get("paths"):
                    health_status["spec_status"] = f"Aggregated (found {len(spec.get('paths',{}))} paths)."
                else:
                    health_status["spec_status"] = "Aggregated spec is empty or has no paths."
                    health_status["details"] += "Aggregated spec seems empty. "
            else: # Should not happen
                health_status["spec_status"] = "SpecProviderService instance not found (unexpected)."
                health_status["details"] += "SpecProviderService missing. "

            # If we reached here without major exceptions from get_mcp_agent_service()
            # and the above checks are reasonable, consider it 'yes'
            if "Error" not in health_status.get("spec_status", "") and "not found" not in health_status.get("llm_status", "") :
                 health_status["answer"] = "yes"
                 health_status["details"] = health_status["details"] or "McpAgentService components appear initialized."
            else: # One of the components reported an issue
                 health_status["details"] = health_status["details"] or "One or more components reported an issue."


            logger.info(f"Healthcheck result: {health_status}")
            return jsonify(health_status), 200

        except Exception as e: # Catch errors from get_mcp_agent_service() or during checks
            logger.error(f"Healthcheck: Critical failure during McpAgentService access or checks: {e}", exc_info=True)
            health_status["details"] = f"Critical failure: {str(e)}"
            return jsonify(health_status), 200 # Still 200 for healthcheck, but indicates failure

    # --- Standard Question Logic ---
    # For this version, conversation history is stateless per request.
    # McpAgentService prepends its own system message.
    history: List[BaseMessage] = [HumanMessage(content=question_text)]

    try:
        service = get_mcp_agent_service() # Get (or initialize) the service

        response_messages = service.process_message(history)

        ai_reply = "Sorry, I couldn't generate a response from the agent."
        if response_messages:
            for msg in reversed(response_messages): # Find the last AIMessage
                if isinstance(msg, AIMessage):
                    ai_reply = msg.content
                    break

        return jsonify({"answer": ai_reply}), 200

    except RuntimeError as re: # Errors from McpAgentService initialization or processing
        logger.error(f"MCP Agent Service runtime error for question '{question_text}': {re}", exc_info=True)
        return jsonify({"error": f"An error occurred: {re}"}), 503 # Service Unavailable if agent can't run
    except Exception as e:
        logger.error(f"Unexpected error in /ask endpoint for question '{question_text}': {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred."}), 500

# Removed /ask/configure GET and POST routes and their functions.
# All configuration is now via environment variables.
