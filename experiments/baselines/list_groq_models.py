"""
List available Groq models
"""

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not found")
    exit(1)

client = Groq(api_key=api_key)

print("Listing available Groq models...")
print("=" * 60)

try:
    models = client.models.list()
    print(f"Type of models: {type(models)}")
    print(f"Models: {models}")
except Exception as e:
    print(f"Error listing models: {e}")
