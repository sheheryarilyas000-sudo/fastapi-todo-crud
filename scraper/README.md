# Polite Scraper - Books to Scrape

This is a polite web scraping pipeline built in Python that extracts book data from a practice sandbox environment. 

## Target Classification
* **Target Site:** https://books.toscrape.com
* **Scope:** Only the first 3 catalogue pages.
* **Data Collected:** Book title, product URL, price, availability, rating, and description.
* **Robots.txt:** Checked `https://books.toscrape.com/robots.txt` - No robots file found (404).
* **Permission:** The target is explicitly a practice sandbox built for scraping. I will not reuse this code on another site without checking its rules and terms first.

## Installation & Running
1. Clone this repository.
2. Install the required tools (Python lane):
   ```bash
   pip install requests beautifulsoup4 pydantic

## Run the scraper:
python src/main.py

## Politeness Rules Followed
User-Agent: Identifies the scraper transparently (FlyRankInternship-A9/1.0).

Delay: Waits at least 0.5 seconds between real network requests.

Timeout: Requests abort after 10 seconds to avoid hanging.

Caching: Development relies on local HTML copies in /cache to prevent hammering the server.

Graceful Failure: 404 errors are skipped gracefully without retrying or crashing the run.

## Record Schema
The extracted records are validated against this structure before saving:

title (String)

product_url (Absolute URL)

price_text (Original string)

price_gbp (Numeric float)

availability_text (String)

rating_text (String, optional)

description (String, optional)

source_page (Absolute URL)

fetched_at (ISO timestamp)

## Why No Browser?
This assignment required no headless browser (like Playwright or Selenium) because all the required data was already present in the static HTML sent by the server. Using a browser would only add unnecessary memory and execution cost.

## Honest Limitation
This scraper is tightly coupled to the current HTML structure of Books to Scrape. If the site changes its CSS classes (e.g., changing price_color), the extraction will fail.

## Ethics Note
Always use an official API when one exists. Never bypass logins, paywalls, or rate blocks. Collect only the data you absolutely need and store it securely.

## Run Report Evidence
Here is the proof of a successful run skipping one intentionally injected broken URL:

```json
{
  "start_time": "2026-10-06T05:49:40.453553+00:00",
  "duration_seconds": 3.12,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}