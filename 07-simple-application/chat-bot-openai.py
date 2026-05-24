import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

client = OpenAI(api_key=api_key)

MODEL = "gpt-4o-mini"

def chat():
    print("\nWelcome to OpenAI Chatbot\n")

    messages = [
        {"role": "system", "content": "You are a helpful assistant"}
    ]

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "end"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )

            reply = response.choices[0].message.content
            print("Bot:", reply, "\n")

            messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            print("Error:", e)
            messages.pop()

if __name__ == "__main__":
    chat()