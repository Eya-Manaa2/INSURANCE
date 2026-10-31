"""
List available Gemini models for the API key
"""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found")
    exit(1)

client = genai.Client(api_key=api_key)

print("Listing available models...")
print("=" * 60)

try:
    models = client.models.list()
    for model in models:
        print(f"Model: {model.name}")
        print(f"  Display name: {model.display_name}")
        print(f"  Description: {model.description}")
        print("-" * 60)
except Exception as e:
    print(f"Error listing models: {e}")
