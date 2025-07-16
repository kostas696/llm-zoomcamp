import mcp_client

client = mcp_client.MCPClient(["python", "weather_server.py"])
client.start_server()
client.initialize()
client.initialized()

tools = client.get_tools()

print("Available tools:")
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")