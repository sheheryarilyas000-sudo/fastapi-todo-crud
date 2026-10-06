import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone

# Constants & Configurations
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/sheheryarilyas000-sudo/todo-crud-api)"
}

def fetch_and_cache(url, cache_path):
    """Fetches HTML from a URL or loads it from local cache if available."""
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    print(f"FETCH: Downloading {url}...")
    os.makedirs(CACHE_DIR, exist_ok=True)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    
    if response.status_code == 200:
        html_content = response.text
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # POLITE DELAY: Wait 0.5 seconds to avoid hammering the server
        time.sleep(0.5) 
        return html_content
    else:
        print(f"Failed status: {response.status_code}")
        return None

def extract_book_urls(html, current_page_url):
    """Extracts absolute book URLs from the catalogue page."""
    soup = BeautifulSoup(html, "html.parser")
    book_links = []
    
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if a_tag and "href" in a_tag.attrs:
            relative_url = a_tag["href"]
            absolute_url = urljoin(current_page_url, relative_url)
            book_links.append(absolute_url)
            
    return book_links

def get_next_page_url(html, current_page_url):
    """Finds the 'next' page button and returns its absolute URL."""
    soup = BeautifulSoup(html, "html.parser")
    next_button = soup.select_one("li.next a")
    
    if next_button and "href" in next_button.attrs:
        relative_url = next_button["href"]
        return urljoin(current_page_url, relative_url)
    return None

def extract_raw_book_details(html, book_url, source_url):
    """Parses the book detail page and returns an 8-field raw record."""
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Title is inside the main <h1> tag
    title_tag = soup.find("h1")
    title = title_tag.text if title_tag else None
    
    # 2. Price is in a <p> tag with class 'price_color'
    price_tag = soup.find("p", class_="price_color")
    price_text = price_tag.text if price_tag else None
    
    # 3. Availability is in a <p> tag with classes 'instock' and 'availability'
    availability_tag = soup.find("p", class_="instock availability")
    availability_text = availability_tag.text.strip() if availability_tag else None
    
    # 4. Rating is in a <p> tag with class 'star-rating'. The second class is the rating text.
    rating_tag = soup.find("p", class_="star-rating")
    rating_text = rating_tag["class"][1] if rating_tag and len(rating_tag.get("class", [])) > 1 else None
    
    # 5. Description is usually the <p> tag immediately following the 'product_description' div
    description_div = soup.find("div", id="product_description")
    if description_div:
        description_p = description_div.find_next_sibling("p")
        description = description_p.text if description_p else None
    else:
        # Some books lack a description; set to None explicitly
        description = None

    # Construct the raw dictionary with the 8 required fields
    raw_record = {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_url,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }
    
    return raw_record

def run_stage_3():
    """Main execution for Stage 3: Collects books and extracts details."""
    print("--- Starting URL Discovery ---")
    current_url = START_URL
    pages_visited = 0
    all_books = []
    
    # Step A: Discover all 60 book URLs from the first 3 pages
    while current_url and pages_visited < 3:
        pages_visited += 1
        page_name = current_url.split("/")[-1]
        cache_path = os.path.join(CACHE_DIR, f"catalogue-{page_name}")
        
        html = fetch_and_cache(current_url, cache_path)
        if not html:
            break
            
        books_on_page = extract_book_urls(html, current_url)
        all_books.extend(books_on_page)
        
        current_url = get_next_page_url(html, current_url)

    unique_books = list(set(all_books))
    print(f"Discovery complete. Found {len(unique_books)} unique URLs.\n")
    
    # Step B: Extract details from every single book page
    print("--- Starting Detail Extraction ---")
    raw_records = []
    
    for idx, book_url in enumerate(unique_books):
        # Create a unique filename for the cache based on the book URL
        # For example, "a-light-in-the-attic_1000/index.html" -> "book_a-light-in-the-attic_1000.html"
        safe_name = book_url.split("/")[-2]
        cache_path = os.path.join(CACHE_DIR, f"book_{safe_name}.html")
        
        html = fetch_and_cache(book_url, cache_path)
        if html:
            # Note: We pass START_URL as the source_page for simplicity in this stage
            record = extract_raw_book_details(html, book_url, START_URL)
            raw_records.append(record)
            
        # Optional: Print progress so you know the script is running
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx + 1} / {len(unique_books)} books...")

    # Stage 3 Checkpoint Output
    print("\n---------------------------------")
    print(f"detail_pages = {len(raw_records)}")
    print("Sample Record:")
    import json
    # Print the first record nicely formatted to verify all 8 keys are present
    print(json.dumps(raw_records[0], indent=2))
    print("---------------------------------")

if __name__ == "__main__":
    run_stage_3()