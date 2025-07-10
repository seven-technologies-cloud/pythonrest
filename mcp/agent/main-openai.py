from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import os
from dotenv import load_dotenv
from config import MODEL, TEMPERATURE, get_config

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize the LLM model
model = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    api_key=API_KEY
)

# Define the agent's prompt
system_message = SystemMessage(content="""
    You are Sete, a helpful agent.
    You have access to tools for querying and storing notes.
    1. Store important insights using write_supabase_note
    2. Query previous notes when needed using read_supabase_note
""")

# Initialize MCP client and create the agent
async def main():
    # Using MultiServerMCPClient for connection
    async with MultiServerMCPClient() as client:
        # Connect to Hawk server
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        mcp_server_path = os.path.join(root_dir, "mcp_servers", "mcp_server.py")

        await client.connect_to_server(
            "SevenTechAgent",
            command="python",
            args=[mcp_server_path]
        )

        # Create the agent with MultiServerMCPClient tools
        agent = create_react_agent(model, client.get_tools(), checkpointer=MemorySaver())

        messages = [system_message]

        print("Welcome to the chat! Type your message (or 'exit' to quit):")

        while True:
            # Read user input asynchronously
            user_input = await asyncio.to_thread(input, "> ")

            # Check if user wants to exit
            if user_input.lower() == "exit":
                print("Ending chat. Goodbye!")
                break

            messages.append(HumanMessage(content=user_input))

            # Process the message with the agent
            config = get_config()
            result = await agent.ainvoke({"messages": messages}, config)

            messages = result["messages"]

            # Display the responses
            for m in messages:
                m.pretty_print()

if __name__ == "__main__":
    asyncio.run(main()) 