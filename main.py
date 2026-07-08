import requests
import json
import os
import re
from markdownify import markdownify as md
from google import genai
from dotenv import load_dotenv

API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
STATE_FILE = "state.json"
OUTPUT_DIR = "articles"

# Load environment variable from .env (useful for local testing)
load_dotenv()

# Initialize the new GenAI client. 
# It automatically detects GEMINI_API_KEY in your environment, so no config line is needed.
client = genai.Client()

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
            
        # Safely convert title to slug, stripping slashes and special characters
        raw_title = article.get('name', 'untitled')
        title_slug = re.sub(r'[^a-z0-9]+', '-', raw_title.lower()).strip('-')
        
        # Scrape and save Markdown
        md_content = md(article['body'], heading_style="ATX")
        file_path = os.path.join(OUTPUT_DIR, f"{title_slug}.md")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        # Upload to Gemini using the new SDK syntax
        print(f"Uploading new/updated file: {file_path}")
        client.files.upload(file=file_path, config={'display_name': title_slug})
        
        # Update state dictionary
        state[article_id] = live_updated_at
        
    # Save the new state so the next run knows what happened
    save_state(state)
    
    print("Job Complete.")
    print(f"Added: {counts['added']}, Updated: {counts['updated']}, Skipped: {counts['skipped']}")

if __name__ == "__main__":
    run_daily_job()