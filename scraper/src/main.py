import os
import requests

# Constants & Configurations
URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")

# Polite User-Agent identifying the scraper
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/sheheryarilyas000-sudo/todo-crud-api)"
}

def fetch_and_cache(url, cache_path):
    """Fetches HTML from a URL or loads it from local cache if available."""
    
    # 1. CACHE CHECK: If file already exists locally, read from it
    if os.path.exists(cache_path):
        print("CACHE HIT: Reading from local cache.")
        with open(cache_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            print(f"Size: {len(html_content)} characters")
            return html_content

    # 2. FETCH: If not cached, download from the internet
    print("FETCH: Downloading page from the internet...")
    
    # Ensure cache directory exists before saving
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Send request with a 10-second timeout to avoid hanging
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    
    # 3. STATUS CHECK: Ensure the server returned a successful response (200 OK)
    if response.status_code == 200:
        html_content = response.text
        
        # 4. SAVE TO CACHE: Store the HTML locally for future runs
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Size: {len(html_content)} characters")
        return html_content
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    html = fetch_and_cache(URL, CACHE_FILE)