import subprocess
import json

# Start the server subprocess
proc = subprocess.Popen(
    ["python", "weather_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Initialize
init = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {"listChanged": True},
            "sampling": {}
        },
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

proc.stdin.write(json.dumps(init) + "\n")
proc.stdin.flush()
print("Sent: initialize")

# Read response
response = proc.stdout.readline()
print("Received:", response.strip())

# Notify initialized
proc.stdin.write(json.dumps({
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}) + "\n")
proc.stdin.flush()
print("Sent: initialized")

# Call get_weather
call_weather = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "get_weather",
        "arguments": {
            "city": "berlin"
        }
    }
}

proc.stdin.write(json.dumps(call_weather) + "\n")
proc.stdin.flush()
print("Sent: tools/call")

# Read the weather response
weather_response = proc.stdout.readline()
print("Response:", weather_response.strip())

# Cleanup
proc.terminate()