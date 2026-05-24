"""
Assignment 4.2 — ReAct agent demo, upgraded from Groq to OpenAI.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from agent_tools import handle_tool_call

load_dotenv(dotenv_path="../../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

REACT_SYSTEM_PROMPT = """
You are a ReAct-style AI assistant. Use this STRICT format:

Thought: <your reasoning>
Action: <one of: get_time, get_date, get_day, get_datetime, get_weather>
Action Input: <input string or NONE>

After you receive an Observation, you may take another Action or give:
Final Answer: <your final answer to the user, using tool results>

RULES (do not violate):
- Use tools whenever the question involves the current date, time, day,
  or weather. Your training data CANNOT know the current values.
- When you receive a tool Observation, treat its content as ground truth.
  Do NOT override, paraphrase, or substitute from your own knowledge.
- For 'get_weather', pass the city name as Action Input.
- If no tool is needed, jump straight to Final Answer.
"""

def chat():
    print("Welcome to the ReAct ChatBot (OpenAI). Type 'exit' to leave.\n")
    base_messages = [{"role": "system", "content": "You are a helpful assistant."}]

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit", "end"}:
            print("Goodbye!")
            break

        base_messages.append({"role": "user", "content": user_input})

        # Build the working message list with the ReAct prompt injected
        react_messages = base_messages.copy()
        react_messages.append({"role": "system", "content": REACT_SYSTEM_PROMPT})

        reasoning_steps = []
        final_answer = None

        # Allow up to 4 reasoning rounds
        for step in range(4):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=react_messages,
                    temperature=0,
                )
                reply = response.choices[0].message.content.strip()
                react_messages.append({"role": "assistant", "content": reply})
                reasoning_steps.append(reply)

                # If LLM gave a final answer, stop
                if "Final Answer:" in reply:
                    final_answer = reply.split("Final Answer:")[-1].strip()
                    break

                # Otherwise try to execute a tool
                observation = handle_tool_call(reply, step)
                if observation:
                    react_messages.append({"role": "user", "content": observation})
                else:
                    # No action requested — assume the LLM is done
                    break

            except Exception as e:
                print(f"[LLM error: {e}]")
                break

        # Print the reasoning trace
        print("\n--- ReAct Reasoning ---")
        for i, s in enumerate(reasoning_steps, 1):
            print(f"\nStep {i}:\n{s}")

        if final_answer:
            print(f"\nChatBot: {final_answer}")
            base_messages.append({"role": "assistant", "content": final_answer})
        else:
            print("\nChatBot: Sorry, I couldn't complete the reasoning.")


if __name__ == "__main__":
    chat()