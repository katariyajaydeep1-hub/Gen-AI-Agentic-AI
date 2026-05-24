import google.generativeai as genai
from dotenv import load_dotenv
import os

# =========================================================
# Load API Key
# =========================================================
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found")

# Configure Gemini
genai.configure(api_key=api_key)

# =========================================================
# Load Model
# =========================================================
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

# =========================================================
# Chatbot Function
# =========================================================
def chat():

    print("\n====================================")
    print(" GEMINI CHATBOT ")
    print(" Type 'exit' to quit ")
    print("====================================\n")

    # Start chat session
    chat_session = model.start_chat(history=[])

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye!\n")
            break

        if not user_input:
            continue

        try:

            response = chat_session.send_message(user_input)

            print("\nAI:")
            print(response.text)
            print()

        except Exception as e:
            print("\nERROR:", e)


# =========================================================
# Run App
# =========================================================
if __name__ == "__main__":
    chat()
