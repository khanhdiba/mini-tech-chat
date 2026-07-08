import requests
import json
import os
import re
from markdownify import markdownify as md
import google.generativeai as genai
from dotenv import load_dotenv

API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
STATE_FILE = "state.json"
OUTPUT_DIR = "articles"

# Load environment variable
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def run_daily_job():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    state = load_state()
    
    response = requests.get(API_URL, params={'per_page': 50})
    articles = response.json().get('articles', [])
    
    counts = {"added": 0, "updated": 0, "skipped": 0}
    
    for article in articles:
        article_id = str(article['id'])
        live_updated_at = article['updated_at']
        
        # DELTA CHECK: Skip if we already processed this exact version
        if state.get(article_id) == live_updated_at:
            counts["skipped"] += 1
            continue
            
        # Determine if new or updated for logging
        if article_id not in state:
            counts["added"] += 1
        else:
            counts["updated"] += 1
            
        # Scrape and save Markdown (from Phase 1 logic)
        # title_slug = article['name'].lower().replace(" ", "-")
        raw_title = article.get('name', 'untitled')
        title_slug = re.sub(r'[^a-z0-9]+', '-', raw_title.lower()).strip('-')
        md_content = md(article['body'], heading_style="ATX")
        file_path = os.path.join(OUTPUT_DIR, f"{title_slug}.md")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        # Upload to Gemini (from Phase 2 logic)
        print(f"Uploading new/updated file: {file_path}")
        genai.upload_file(path=file_path, display_name=title_slug)
        
        # Update state dictionary
        state[article_id] = live_updated_at
        
    # Save the new state so the next run knows what happened
    save_state(state)
    
    print("Job Complete.")
    print(f"Added: {counts['added']}, Updated: {counts['updated']}, Skipped: {counts['skipped']}")

if __name__ == "__main__":
    run_daily_job()