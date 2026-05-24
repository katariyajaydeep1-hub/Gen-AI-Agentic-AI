import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# ==========================================
# Load Environment Variables
# ==========================================
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

# ==========================================
# Create Chat Model
# ==========================================
chat = ChatOpenAI(
    openai_api_key=api_key,
    model="gpt-4o-mini",
    temperature=0.7
)

# ==========================================
# Chat History
# ==========================================
messages = [
    SystemMessage(content="You are a helpful AI assistant.")
]

# ==========================================
# Chat Loop
# ==========================================
print("\nLangChain Chatbot Started")
print("Type 'exit' to quit\n")

while True:

    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    messages.append(HumanMessage(content=user_input))

    response = chat.invoke(messages)

    print("\nAI:", response.content, "\n")

    messages.append(response)