from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import MODEL, TEMPERATURE, get_config
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GOOGLE_API_KEY")
# Inicializa o modelo LLM
model = ChatGoogleGenerativeAI(
    model=MODEL,
    temperature=TEMPERATURE,
    api_key=API_KEY
)

# Define o prompt do agente
system_message = SystemMessage(content="""
    Você é o Sete, um agente solicitado.
    Você tem acesso a ferramentas para consultar e armazenar notas.
    1. Armazenar insights importantes usando write_supabase_note
    2. Consultar notas anteriores quando necessário usando read_supabase_note
""")

# Inicializa o cliente MCP e cria o agente
async def main():
    # Usando MultiServerMCPClient para conexão
    async with MultiServerMCPClient() as client:
        # Conecta ao servidor Hawk
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        mcp_server_path = os.path.join(root_dir, "mcp_servers", "mcp_server.py")

        await client.connect_to_server(
            "SevenTechAgent",
            command="python",
            args=[mcp_server_path]
        )

        # Cria o agente com as ferramentas do MultiServerMCPClient
        agent = create_react_agent(model, client.get_tools(), checkpointer=MemorySaver())

        messages = [system_message]

        print("Bem-vindo ao chat! Digite sua mensagem (ou 'sair' para encerrar):")

        while True:
            # Lê a entrada do usuário de forma assíncrona
            user_input = await asyncio.to_thread(input, "> ")

            # Verifica se o usuário quer sair
            if user_input.lower() == "sair":
                print("Encerrando o chat. Até logo!")
                break

            messages.append(HumanMessage(content=user_input))

            # Processa a mensagem com o agente
            config = get_config()
            result = await agent.ainvoke({"messages": messages}, config)

            messages = result["messages"]

            # Exibe as respostas
            for m in messages:
                m.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())
