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
# SCHEMA (Data Validation Recipe)
# ==========================================
class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float          # Normalized numeric price for operations
    availability_text: str
    rating_text: Optional[str]
    description: Optional[str] # Description can be null
    source_page: HttpUrl
    fetched_at: str

# ==========================================
# FETCHING & EXTRACTION LOGIC (Stages 1-3)
# ==========================================
def fetch_and_cache(url, cache_path):
    """Fetches HTML from URL or loads from local cache."""
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        return None
    
    if response.status_code == 200:
        html_content = response.text
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        time.sleep(0.5) 
        return html_content
    return None

def extract_book_urls(html, current_page_url):
    """Extracts absolute book URLs from the catalogue page."""
    soup = BeautifulSoup(html, "html.parser")
    book_links = []
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if a_tag and "href" in a_tag.attrs:
            absolute_url = urljoin(current_page_url, a_tag["href"])
            book_links.append(absolute_url)
    return book_links

def get_next_page_url(html, current_page_url):
    """Finds the 'next' page button and returns its absolute URL."""
    soup = BeautifulSoup(html, "html.parser")
    next_button = soup.select_one("li.next a")
    if next_button and "href" in next_button.attrs:
        return urljoin(current_page_url, next_button["href"])
    return None

def extract_raw_book_details(html, book_url, source_url):
    """Parses the book detail page and returns raw string records."""
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

# ==========================================
# STAGE 4: NORMALIZATION & VALIDATION
# ==========================================
def normalize_price(price_text):
    """Extracts numeric value from price string (e.g., '£51.77' -> 51.77)."""
    if not price_text:
        return 0.0
    
    # Use RegEx to filter out currency symbols and keep only digits and decimal
    match = re.search(r'[\d\.]+', price_text)
    if match:
        return float(match.group())
    return 0.0

def run_stage_4():
    """Main execution: Discovers URLs, extracts details, normalizes, and validates."""
    print("--- Starting URL Discovery ---")
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
    print(f"Found {len(unique_books)} unique URLs.")
    
    print("--- Starting Detail Extraction & Validation ---")
    good_records = []
    bad_records = []
    
    for book_url in unique_books:
        safe_name = book_url.split("/")[-2]
        cache_path = os.path.join(CACHE_DIR, f"book_{safe_name}.html")
        html = fetch_and_cache(book_url, cache_path)
        
        if html:
            raw_record = extract_raw_book_details(html, book_url, START_URL)
            
            # NORMALIZATION: Add clean float field for price
            raw_record["price_gbp"] = normalize_price(raw_record["price_text"])
            
            # VALIDATION: Validate against Pydantic schema
            try:
                valid_record = BookRecord(**raw_record)
                good_records.append(json.loads(valid_record.json()))
            except ValidationError as e:
                bad_records.append({"url": book_url, "error": str(e)})

    # STORE: Persist validated records and errors to JSON files
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(os.path.join(OUTPUT_DIR, "books.json"), "w", encoding="utf-8") as f:
        json.dump(good_records, f, indent=2)
        
    with open(os.path.join(OUTPUT_DIR, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(bad_records, f, indent=2)

    # Stage 4 Checkpoint Output
    print("\n---------------------------------")
    print(f"Total Unique Checked: {len(good_records) + len(bad_records)}")
    print(f"Valid Records Saved (books.json): {len(good_records)}")
    print(f"Failed Records Saved (errors.json): {len(bad_records)}")
    print("---------------------------------")

if __name__ == "__main__":
    run_stage_4()