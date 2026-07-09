import os
import glob
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variable from .env
load_dotenv()

# Initialize the new GenAI client. 
# It automatically detects GEMINI_API_KEY in your environment.
client = genai.Client()

# The exact system prompt required by the assignment
SYSTEM_PROMPT = """
You are OptiBot, the customer-support bot for OptiSigns.com.
Tone: helpful, factual, concise.
Only answer using the uploaded docs.
Max 5 bullet points; else link to the doc.
Cite up to 3 "Article URL:" lines per reply.
"""


def run_sanity_check():
    print("\nInitializing OptiBot...")
    
    # 1. Fetch all active files directly from your Gemini API storage
    print("Fetching active files from Gemini cloud storage...")
    
    # client.files.list() returns an iterator, so we wrap it in list()
    active_files = list(client.files.list())
    print(f"Found {len(active_files)} files ready for context.")
    
    # The sanity check question required by the assignment
    question = "How do I add a YouTube video?"
    print(f"User: {question}\n")
    
    # 2. Combine the fetched file objects and the user question into a single list
    prompt_contents = active_files + [question]
    
    # Generate the response using the new client syntax
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt_contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.0 # Good practice for factual RAG bots
        )
    )
    
    print(f"OptiBot:\n{response.text}")

def clear_all_files():
    print("Fetching all active files from Gemini cloud storage...")
    
    # Retrieve the list of all files
    active_files = list(client.files.list())
    
    if not active_files:
        print("No files found. Your storage is already empty!")
        return
        
    print(f"Found {len(active_files)} files. Starting deletion...")
    
    deleted_count = 0
    for file in active_files:
        print(f"Deleting: {file.display_name} ({file.name})")
        
        # Delete the file using its unique name identifier
        client.files.delete(name=file.name)
        deleted_count += 1
        
    print(f"\nSuccess! Permanently deleted {deleted_count} files.")

if __name__ == "__main__":
    run_sanity_check()
    # clear_all_files()