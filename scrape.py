import requests
import os
import re
from markdownify import markdownify as md

API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
OUTPUT_DIR = "articles"

def create_slug(title):
    """Converts an article title into a clean URL-friendly slug for the filename."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug if slug else "untitled-article"

def fetch_and_convert():
    # Ensure our output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # We want at least 30 articles, Zendesk defaults to 30 per page.
    # We'll set per_page=50 to be safe.
    params = {'per_page': 50}
    
    print(f"Fetching articles from {API_URL}...")
    response = requests.get(API_URL, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return

    data = response.json()
    articles = data.get('articles', [])
    
    saved_count = 0
    
    for article in articles:
        # The prompt requires pulling >= 30 articles
        if saved_count >= 35: 
            break
            
        title = article.get('name', 'Untitled')
        html_body = article.get('body', '')
        
        # Skip empty articles
        if not html_body:
            continue
            
        # Convert HTML to clean Markdown (preserves headings, code blocks, relative links)
        markdown_content = md(html_body, heading_style="ATX")
        
        # Save to file <slug>.md
        slug = create_slug(title)
        filepath = os.path.join(OUTPUT_DIR, f"{slug}.md")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(markdown_content)
            
        saved_count += 1
        print(f"Saved: {slug}.md")
        
    print(f"\nSuccess! Converted and saved {saved_count} articles to ./{OUTPUT_DIR}")

if __name__ == "__main__":
    fetch_and_convert()