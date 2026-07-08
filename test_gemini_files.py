import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# List all uploaded files
for file in genai.list_files():
    print(f"Name: {file.display_name}")
    print(f"URI: {file.uri}")
    print(f"API Name: {file.name}") # This is the ID used to reference/delete it
    print(f"State: {file.state.name}")
    print("-" * 20)