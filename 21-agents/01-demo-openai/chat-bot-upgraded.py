"""
Assignment 4.2 — Rule-based agent demo, upgraded from Groq to OpenAI.
Also satisfies 22-agents-assignment: handles "what is the current date and time?"
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from agent_tools import agent_router

load_dotenv(dotenv_path="../../.env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-mini"


def chat():
    print("Welcome to the OpenAI Chat Bot with Rule-Based Tools.")
    print("Type 'exit' to quit.\n")

    messages = [
        {"role": "system",
         "content": "You are a helpful assistant. When you receive a "
                    "system message containing a tool's output, use that "
                    "EXACT information in your answer. Never override or "
                    "ignore information provided by tools."}
    ]

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "end"}:
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        # ---------- TOOL LAYER ----------
        tool_output = agent_router(user_input)

        if tool_output:
            print(f"[Tool Output] {tool_output}")
            messages.append({
                "role": "system",
                "content": f"Tool result: {tool_output}. "
                           f"Use this exact information in your answer."
            })
        # --------------------------------

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=200,
            )
            reply = response.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            print(f"ChatBot: {reply}\n")
        except Exception as e:
            print(f"[Error: {e}]\n")
            messages.pop()


if __name__ == "__main__":
    chat()
