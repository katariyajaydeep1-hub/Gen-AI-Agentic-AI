"""
Assignment 4.2 + 22-agents-assignment
Modern agent using OpenAI's native function-calling API.
This is the cleanest, most reliable agent architecture available today.
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from agent_tools import TOOLS  # the dict of name -> callable

load_dotenv(dotenv_path="../../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# ----------------------------------------------------------------------
# Tool schemas — describe each tool to the LLM in JSON schema format.
# The LLM uses these descriptions to decide WHICH tool to call and
# WHAT arguments to pass.
# ----------------------------------------------------------------------
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date AND time in India (IST). "
                           "Use this whenever the user asks for current "
                           "date+time, or 'now'.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time in India (IST) only.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get today's date in India (IST) only.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_day",
            "description": "Get today's day of the week in India.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for any city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city, e.g. 'Pune'.",
                    }
                },
                "required": ["city"],
            },
        },
    },
]


def run_tool(name, arguments_json):
    """Execute one tool call. Returns the string output."""
    args = json.loads(arguments_json) if arguments_json else {}
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    try:
        if name == "get_weather":
            return TOOLS[name](args.get("city", "Bangalore"))
        return TOOLS[name]()
    except Exception as e:
        return f"Tool error: {e}"


def chat():
    print("=" * 60)
    print("OpenAI Function-Calling Agent")
    print("Tools: datetime, time, date, day, weather")
    print("Type 'exit' to leave.")
    print("=" * 60 + "\n")

    messages = [
        {"role": "system",
         "content": "You are a helpful assistant. Use the tools when "
                    "the user asks about current time, date, day, or "
                    "weather. Always use the EXACT values returned by tools."}
    ]

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit", "end"}:
            print("Goodbye!")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Allow up to 5 rounds in case the LLM chains tool calls
        for _ in range(5):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            # Did the LLM ask to call any tools?
            if msg.tool_calls:
                messages.append(msg)  # record the LLM's tool-call request

                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    tool_args = tc.function.arguments
                    print(f"[Calling tool: {tool_name}({tool_args})]")
                    result = run_tool(tool_name, tool_args)
                    print(f"[Tool result: {result}]")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
                continue  # loop again so the LLM can use the tool result

            # No more tool calls — LLM has the final answer
            print(f"ChatBot: {msg.content}\n")
            messages.append({"role": "assistant", "content": msg.content})
            break


if __name__ == "__main__":
    chat()