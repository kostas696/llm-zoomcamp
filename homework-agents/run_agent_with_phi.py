# run_agent_with_phi.py

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import chat_assistant
import mcp_client

load_dotenv()

# Start MCP client and weather server
client = mcp_client.MCPClient(["python", "weather_server.py"])
client.start_server()
client.initialize()
client.initialized()

# Wrap MCP tools for LangChain-style agent use
tools = mcp_client.MCPTools(mcp_client=client)

# Set up Ollama (phi model)
llm = ChatOllama(model="phi", base_url="http://localhost:11434")

# Developer prompt to guide behavior
developer_prompt = """
You are a weather assistant. You MUST use the available tools to answer the user's question.
Do NOT try to answer weather-related questions directly.

If the user asks about the weather in a city, call the `get_weather` tool.
If the user wants to update the weather, use `set_weather`.

Always use function calls instead of answering on your own.
""".strip()

# UI + chat loop
chat_interface = chat_assistant.ChatInterface()

chat = chat_assistant.ChatAssistant(
    tools=tools,
    developer_prompt=developer_prompt,
    chat_interface=chat_interface,
    client=llm
)

# Run the agent loop
chat.run()