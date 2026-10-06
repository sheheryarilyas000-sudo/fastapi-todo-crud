import os
import time
import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Optional

# Constants & Configurations
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/sheheryarilyas000-sudo/todo-crud-api)"
}

# ==========================================
# METRICS TRACKING (For Stage 5 Run Report)
# ==========================================
run_metrics = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "failed_pages": 0,
    "valid_records": 0,
    "invalid_records": 0
}

# ==========================================
# SCHEMA (Data Validation Recipe)
# ==========================================
class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str]
    description: Optional[str]
    source_page: HttpUrl
    fetched_at: str

# ==========================================
# FETCHING LOGIC (With Retries)
# ==========================================
def fetch_and_cache(url, cache_path):
    """Fetches HTML with retry logic for 5xx/timeouts, skips 404s, and tracks metrics."""
    if os.path.exists(cache_path):
        run_metrics["cache_hits"] += 1
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Retry logic: Try 1 initial time + 1 retry = max 2 attempts
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                run_metrics["pages_fetched"] += 1
                html_content = response.text
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                time.sleep(0.5) 
                return html_content
            
            elif response.status_code in (403, 404):
                # Do not retry on client errors (Not Found, Forbidden)
                print(f"Skipping {url}: Status {response.status_code}")
                run_metrics["failed_pages"] += 1
                return None
            
            elif response.status_code >= 500:
                # Retry on server errors
                print(f"Server error {response.status_code} for {url}. Retrying...")
                time.sleep(2)
                
        except requests.exceptions.RequestException as e:
            # Retry on network timeouts or drops
            print(f"Network error for {url}: {e}. Retrying...")
            time.sleep(2)
            
    # If all attempts fail, log as a failed page
    run_metrics["failed_pages"] += 1
    return None

# ==========================================
# EXTRACTION & NORMALIZATION LOGIC
# ==========================================
def extract_book_urls(html, current_page_url):
    soup = BeautifulSoup(html, "html.parser")
    book_links = []
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if a_tag and "href" in a_tag.attrs:
            absolute_url = urljoin(current_page_url, a_tag["href"])
            book_links.append(absolute_url)
    return book_links

def get_next_page_url(html, current_page_url):
    soup = BeautifulSoup(html, "html.parser")
    next_button = soup.select_one("li.next a")
    if next_button and "href" in next_button.attrs:
        return urljoin(current_page_url, next_button["href"])
    return None

def extract_raw_book_details(html, book_url, source_url):
    soup = BeautifulSoup(html, "html.parser")
    
    title_tag = soup.find("h1")
    title = title_tag.text if title_tag else None
    
    price_tag = soup.find("p", class_="price_color")
    price_text = price_tag.text if price_tag else None
    
    availability_tag = soup.find("p", class_="instock availability")
    availability_text = availability_tag.text.strip() if availability_tag else None
    
    rating_tag = soup.find("p", class_="star-rating")
    rating_text = rating_tag["class"][1] if rating_tag and len(rating_tag.get("class", [])) > 1 else None
    
    description_div = soup.find("div", id="product_description")
    if description_div:
        description_p = description_div.find_next_sibling("p")
        description = description_p.text if description_p else None
    else:
        description = None

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_url,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def normalize_price(price_text):
    if not price_text: return 0.0
    match = re.search(r'[\d\.]+', price_text)
    if match: return float(match.group())
    return 0.0

# ==========================================
# MAIN EXECUTION (Stage 5)
# ==========================================
def run_stage_5():
    start_time = time.time()
    print("--- Starting Scraper Run ---")
    
    # 1. Discover URLs
    current_url = START_URL
    pages_visited = 0
    all_books = []
    
    while current_url and pages_visited < 3:
        pages_visited += 1
        page_name = current_url.split("/")[-1]
        cache_path = os.path.join(CACHE_DIR, f"catalogue-{page_name}")
        html = fetch_and_cache(current_url, cache_path)
        if not html: break
        all_books.extend(extract_book_urls(html, current_url))
        current_url = get_next_page_url(html, current_url)

    unique_books = list(set(all_books))
    
    # INTENTIONAL FAILURE INJECTION: Add a made-up URL to prove resilience[cite: 7]
    fake_url = "https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html"
    unique_books.append(fake_url)
    
    print(f"Found {len(unique_books) - 1} real URLs, injected 1 fake URL for testing.")
    
    # 2. Extract & Validate
    good_records = []
    bad_records = []
    
    for book_url in unique_books:
        safe_name = book_url.split("/")[-2]
        cache_path = os.path.join(CACHE_DIR, f"book_{safe_name}.html")
        html = fetch_and_cache(book_url, cache_path)
        
        if html:
            raw_record = extract_raw_book_details(html, book_url, START_URL)
            raw_record["price_gbp"] = normalize_price(raw_record["price_text"])
            
            try:
                valid_record = BookRecord(**raw_record)
                good_records.append(json.loads(valid_record.json()))
            except ValidationError as e:
                bad_records.append({"url": book_url, "error": str(e)})

    # 3. Update Final Metrics
    run_metrics["valid_records"] = len(good_records)
    run_metrics["invalid_records"] = len(bad_records)
    end_time = time.time()
    
    # 4. Generate Run Report[cite: 7]
    report = {
        "start_time": datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
        "duration_seconds": round(end_time - start_time, 2),
        "pages_fetched": run_metrics["pages_fetched"],
        "cache_hits": run_metrics["cache_hits"],
        "valid_records": run_metrics["valid_records"],
        "invalid_records": run_metrics["invalid_records"],
        "failed_pages": run_metrics["failed_pages"]
    }
    
    # 5. Store Files
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "books.json"), "w", encoding="utf-8") as f:
        json.dump(good_records, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(bad_records, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "run-report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Stage 5 Checkpoint Output
    print("\n---------------------------------")
    print("RUN COMPLETE")
    print(json.dumps(report, indent=2))
    print("---------------------------------")

if __name__ == "__main__":
    run_stage_5()