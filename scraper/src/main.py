import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Constants & Configurations
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/sheheryarilyas000-sudo/todo-crud-api)"
}

def fetch_and_cache(url, cache_path):
    """Fetches HTML from a URL or loads it from local cache if available."""
    
    # 1. CACHE CHECK: If file exists locally, read from it
    if os.path.exists(cache_path):
        # Cache Hit: No polite delay needed for local file reads
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    # 2. FETCH: If not cached, download from the internet
    print(f"FETCH: Downloading {url}...")
    os.makedirs(CACHE_DIR, exist_ok=True)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    
    # 3. STATUS CHECK: Ensure the server returned a successful response
    if response.status_code == 200:
        html_content = response.text
        
        # Save to cache for future runs
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # POLITE DELAY: Wait 0.5 seconds after a real network request[span_0](start_span)[span_0](end_span)
        time.sleep(0.5) 
        return html_content
    else:
        print(f"Failed status: {response.status_code}")
        return None

def extract_book_urls(html, current_page_url):
    """Extracts book URLs from the HTML and converts them to absolute URLs."""
    soup = BeautifulSoup(html, "html.parser")
    book_links = []
    
    # Book links are located inside <a> tags within <h3> tags
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if a_tag and "href" in a_tag.attrs:
            relative_url = a_tag["href"]
            # Convert relative URL to absolute URL[span_1](start_span)[span_1](end_span)
            absolute_url = urljoin(current_page_url, relative_url)
            book_links.append(absolute_url)
            
    return book_links

def get_next_page_url(html, current_page_url):
    """Finds the 'next' page button and returns its absolute URL."""
    soup = BeautifulSoup(html, "html.parser")
    
    # CSS selector: <a> tag inside an <li> with class 'next'
    next_button = soup.select_one("li.next a")
    if next_button and "href" in next_button.attrs:
        relative_url = next_button["href"]
        return urljoin(current_page_url, relative_url)
    
    return None

def run_stage_2():
    """Main execution for Stage 2: Traverse 3 catalogue pages."""
    current_url = START_URL
    pages_visited = 0
    all_books = []
    
    # Continue while a next page exists and we haven't hit our 3-page limit[span_2](start_span)[span_2](end_span)
    while current_url and pages_visited < 3:
        pages_visited += 1
        
        # Extract page name (e.g., 'page-1.html') to use as cache filename
        page_name = current_url.split("/")[-1]
        cache_path = os.path.join(CACHE_DIR, f"catalogue-{page_name}")
        
        html = fetch_and_cache(current_url, cache_path)
        if not html:
            break
            
        # 1. Extract book links from the current page
        books_on_page = extract_book_urls(html, current_url)
        all_books.extend(books_on_page)
        
        # 2. Find the link to the next catalogue page
        current_url = get_next_page_url(html, current_url)

    # Remove duplicate links using a Set[span_3](start_span)[span_3](end_span)
    unique_books = list(set(all_books))

    # Stage 2 Checkpoint Output[span_4](start_span)[span_4](end_span)
    print("---------------------------------")
    print(f"catalogue_pages = {pages_visited}")
    print(f"discovered = {len(all_books)}")
    print(f"unique_urls = {len(unique_books)}")
    print("---------------------------------")

if __name__ == "__main__":
    run_stage_2()