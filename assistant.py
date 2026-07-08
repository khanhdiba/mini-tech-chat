import google.generativeai as genai
import os
import glob
import time
from dotenv import load_dotenv

load_dotenv()

# Configure the API key
API_KEY = os.getenv("GEMINI_API_KEY")
print(f"Gemini API Key: {API_KEY}")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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
    
    # Upload files to Gemini's storage
    for file_path in md_files:
        print(f"Uploading {file_path}...")
        # Gemini handles chunking and indexing natively via the File API
        gemini_file = genai.upload_file(path=file_path, display_name=os.path.basename(file_path))
        uploaded_files.append(gemini_file)
        # Sleep briefly to respect API rate limits during bulk upload
        time.sleep(2) 
        
    print(f"\nSuccessfully uploaded and embedded {len(uploaded_files)} files.")
    return uploaded_files

def run_sanity_check(uploaded_files):
    # Initialize the model with the uploaded context and strict system instructions
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    print("\nInitializing OptiBot...")
    # The sanity check question required by the assignment
    question = "How do I add a YouTube video?"
    print(f"User: {question}\n")
    
    # Generate the response using the uploaded files as context
    response = model.generate_content([*uploaded_files, question])
    
    print(f"OptiBot:\n{response.text}")

if __name__ == "__main__":
    files = upload_files_to_gemini()
    run_sanity_check(files)