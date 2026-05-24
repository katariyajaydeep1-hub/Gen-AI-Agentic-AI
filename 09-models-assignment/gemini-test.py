from google import genai
from dotenv import load_dotenv
import os

# ==========================================
# Load API Key
# ==========================================
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found")

print("API KEY LOADED")

# ==========================================
# Create Client
# ==========================================
client = genai.Client(api_key=api_key)

# ==========================================
# Generate Response
# ==========================================
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain transformers simply"
)

print("\nAI RESPONSE:\n")
print(response.text)