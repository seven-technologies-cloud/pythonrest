MODEL="gemini-1.5-flash"
TEMPERATURE=0.7

def get_config(thread_id: str = "user_main_thread") -> dict:
    """
    Generates the configuration dictionary for LangGraph agent invocation.

    This configuration is essential for checkpointers (like MemorySaver)
    to correctly track the state of a conversation thread.

    Args:
        thread_id (str): A unique identifier for the conversation thread.
                         Defaults to "user_main_thread".
a
    Returns:
        dict: A configuration dictionary containing the thread_id under
              the 'configurable' key, suitable for agent.ainvoke/invoke.
    """
    return {
        "configurable": {
            "thread_id": thread_id,
            # You can add other configurable parameters here if needed by
            # specific LangChain/LangGraph components used within your agent.
            # For example:
            # "user_id": "some_user_identifier",
            # "some_other_config": "value"
        }
    }