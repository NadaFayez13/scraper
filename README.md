# Books to Scrape - Robust ETL Scraper

A robust, cached, and validated web scraper built with Python, BeautifulSoup4, and Pydantic to extract book data from [Books to Scrape](https://books.toscrape.com/).

## 📌 Features
- **Page Discovery & Pagination:** Automatically scans catalog pages and extracts book detail URLs.
- **Local File Caching:** Implements HTML caching to respect rate limits and allow instant offline re-runs.
- **Data Normalization & Validation:** Cleans currency symbols, extracts star ratings, and enforces schema integrity using Pydantic.
- **Error Handling & Reporting:** Captures parsing exceptions cleanly and outputs an execution report (`run-report.json`).

## 📁 Output Structure
- `output/books.json`: Validated book records.
- `output/errors.json`: Logged errors for failed URLs.
- `output/run-report.json`: Scraping session metadata and stats.

## 🚀 How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt