import json
from IPython.display import display, HTML
import markdown
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Tools:
    def __init__(self):
        self.tools = {}
        self.functions = {}

    def add_tool(self, function, description):
        self.tools[function.__name__] = description
        self.functions[function.__name__] = function

    def get_tools(self):
        return list(self.tools.values())

    def function_call(self, tool_call_response):
        function_name = tool_call_response.name
        arguments = json.loads(tool_call_response.arguments)

        f = self.functions[function_name]
        result = f(**arguments)

        return {
            "type": "function_call_output",
            "call_id": tool_call_response.call_id,
            "output": json.dumps(result, indent=2),
        }


def shorten(text, max_length=50):
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


class ChatInterface:
    def input(self):
        question = input("You: ")
        return question

    def display(self, message):
        print(message)

    def display_function_call(self, entry, result):
        call_html = f"""
            <details>
            <summary>Function call: <tt>{entry.name}({shorten(entry.arguments)})</tt></summary>
            <div>
                <b>Call</b>
                <pre>{entry}</pre>
            </div>
            <div>
                <b>Output</b>
                <pre>{result['output']}</pre>
            </div>
            </details>
        """
        display(HTML(call_html))

    def display_response(self, entry):
        print(f"Assistant: {entry.content}")


class ChatAssistant:
    def __init__(self, tools, developer_prompt, chat_interface, client):
        self.tools = tools
        self.developer_prompt = developer_prompt
        self.chat_interface = chat_interface
        self.client = client

    def format_for_langchain(self, messages):
        formatted = []
        for msg in messages:
            role = msg["role"]
            if role == "user":
                formatted.append(HumanMessage(content=msg["content"]))
            elif role in {"developer", "system"}:
                formatted.append(SystemMessage(content=msg["content"]))
            elif role == "assistant":
                formatted.append(AIMessage(content=msg["content"]))
        return formatted

    def gpt(self, chat_messages):
        formatted_messages = self.format_for_langchain(chat_messages)
        response = self.client.invoke(formatted_messages)
        return {
            "output": [AIMessage(content=response.content)]
        }

    def run(self):
        chat_messages = [{"role": "developer", "content": self.developer_prompt}]

        while True:
            question = self.chat_interface.input()
            if question.strip().lower() == 'stop':
                self.chat_interface.display("Chat ended.")
                break

            chat_messages.append({"role": "user", "content": question})

            while True:
                response = self.gpt(chat_messages)
                has_messages = False

                for entry in response["output"]:
                    chat_messages.append(entry)

                    if hasattr(entry, "type") and entry.type == "function_call":
                        result = self.tools.function_call(entry)
                        chat_messages.append(result)
                        self.chat_interface.display_function_call(entry, result)
                    else:
                        self.chat_interface.display_response(entry)
                        has_messages = True

                if has_messages:
                    break