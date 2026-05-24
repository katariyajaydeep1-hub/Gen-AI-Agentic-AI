# Use Groq
from groq import Groq

# Read the key from the file
api_key_path = r"E:\Lenovo Ideapad 330\company-material\digital-workforce-transformation\ai-upskill-4\key-vault\groq\groq-api-key.txt"
f = open(api_key_path, "r")
api_key = f.read().strip()
f.close()

# Intialize the Groq client
client = Groq(api_key=api_key)

# Select a model
MODEL = "llama-3.1-8b-instant"


### VIBE CODED USING GITHUB COPILOT
# Create a function to generate responses from the model

def chat():
    # Welcome message
    print("\nWelcome to the Chat Bot powered By Groq")
    print("-"*80, "\n\n")

    # Messages list and initialize with system message
    # messages = [
    #     { 
    #         "role": "system", 
    #         "content": """
    #         You are a helpful food recipe assistant, 
    #         only answer queries on recipes, 
    #         any other queries say that you are not allowed to answer such queries
    #         """
    #     }
    # ]

    messages = [
        { 
            "role": "system", 
            "content": """
            You are a helpful language translator 
            """
        }
    ]

    # Loop
    while True:

        # Use input
        user_input = input("You: ")

        # Check if it is an exit condition
        if user_input.lower() in ["end", "quit"]:
            break

        # Add the user message to messages list
        messages.append({"role": "user", "content":user_input})

        # Exception handler
        try:
            # Make the LLM call and get the response
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            # Extract the message from the response
            ai_reply = response.choices[0].message.content

            # Add the AI reply to the messages
            messages.append({"role": "assistant", "content":ai_reply})

            # Show it to the user
            print("AI :", ai_reply)
        
        except Exception as e:
            print("Chat failed with message: ", e)


# Launch the model
if __name__ == "__main__":
    chat()
    