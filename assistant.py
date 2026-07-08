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

def upload_files_to_gemini(directory_path="articles"):
    print(f"Scanning {directory_path} for Markdown files...")
    md_files = glob.glob(os.path.join(directory_path, "*.md"))
    
    uploaded_files = []
    
    # Upload files to Gemini's storage using the new SDK
    for file_path in md_files:
        print(f"Uploading {file_path}...")
        gemini_file = client.files.upload(
            file=file_path, 
            config={'display_name': os.path.basename(file_path)}
        )
        uploaded_files.append(gemini_file)
        # Sleep briefly to respect API rate limits during bulk upload
        time.sleep(2) 
        
    print(f"\nSuccessfully uploaded and embedded {len(uploaded_files)} files.")
    return uploaded_files

def run_sanity_check(uploaded_files):
    print("\nInitializing OptiBot...")
    
    # The sanity check question required by the assignment
    question = "How do I add a YouTube video?"
    print(f"User: {question}\n")
    
    # Combine the uploaded file objects and the user question into a single list
    prompt_contents = uploaded_files + [question]
    
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

if __name__ == "__main__":
    files = upload_files_to_gemini()
    run_sanity_check(files)