import os
import time
from bs4 import BeautifulSoup
import requests 
from urllib.parse import urljoin
from datetime import datetime, timezone
import hashlib
import re
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ValidationError
import json

class BookSchema(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float = Field(..., ge=0)
    availability_text: str
    in_stock: bool
    rating_text: Optional[str] = None
    rating_stars: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str
 
HEADERS = {
    'User-Agent': 'FlyRankInternship-A9/1.0 (Educational Scraping Project; Contact: nada@example.com)'
}
CACHE_DIR = 'cache'
URL_PAGE_1 = 'https://books.toscrape.com/catalogue/page-1.html'

os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_page(url: str, cache_filename: str) -> str:
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    if os.path.exists(cache_path):
        print(f"[CACHE HIT] Reading {cache_filename} from cache...")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    print(f"[FETCHING] Requesting {url} from server...")
    time.sleep(0.5)
    
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
        
    return response.text


def fetch_book_page(url: str) -> str:
    books_cache_dir = os.path.join(CACHE_DIR, 'books')
    os.makedirs(books_cache_dir, exist_ok=True)
    
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_path = os.path.join(books_cache_dir, f"{url_hash}.html")
    
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    time.sleep(0.5) 
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
        
    return response.text


def parse_book_page(url: str, source_page_url: str) -> dict:
    html = fetch_book_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Title
    title = soup.find('h1').text.strip() if soup.find('h1') else None
    
    # 2. Price Text
    price_elem = soup.find('p', class_='price_color')
    price_text = price_elem.text.strip() if price_elem else None
    
    # 3. Availability Text
    avail_elem = soup.find('p', class_='instock availability')
    availability_text = avail_elem.text.strip() if avail_elem else None
    
    # 4. Rating Text
    rating_text = None
    rating_elem = soup.find('p', class_='star-rating')
    if rating_elem:
        classes = rating_elem.get('class', [])
        for c in classes:
            if c != 'star-rating':
                rating_text = c
                break

    # 5. Product Description
    desc_elem = soup.find('div', id='product_description')
    description = None
    if desc_elem and desc_elem.find_next_sibling('p'):
        description = desc_elem.find_next_sibling('p').text.strip()
        
    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page_url,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def normalize_and_validate(raw_record: dict) -> BookSchema:
    """تنظيف البيانات وحساب الحقول المشتفة والتحقق من الـ Schema"""
    
    price_gbp = 0.0
    if raw_record.get('price_text'):
        match = re.search(r'[\d.]+', raw_record['price_text'])
        if match:
            price_gbp = float(match.group())

    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating_stars = rating_map.get(raw_record.get('rating_text'), None)

    in_stock = "In stock" in raw_record.get('availability_text', '')

    cleaned_data = {
        **raw_record,
        "price_gbp": price_gbp,
        "rating_stars": rating_stars,
        "in_stock": in_stock
    }

    return BookSchema(**cleaned_data)


def discover_book_links(max_pages: int = 3):
    
    book_urls = []
    current_url = 'https://books.toscrape.com/catalogue/page-1.html'
    
    for page_num in range(1, max_pages + 1):
        cache_filename = f"catalogue-page-{page_num}.html"
        html = fetch_page(current_url, cache_filename)
        soup = BeautifulSoup(html, 'html.parser')
        
        articles = soup.find_all('article', class_='product_pod')
        for article in articles:
            relative_link = article.find('h3').find('a')['href']

            full_url = urljoin(current_url, relative_link)
            book_urls.append(full_url)
            
        print(f" Page {page_num}: Found {len(articles)} books.")
        
        next_button = soup.find('li', class_='next')
        if next_button and page_num < max_pages:
            next_relative = next_button.find('a')['href']
            current_url = urljoin(current_url, next_relative)
        else:
            break
            
    return book_urls

if __name__ == '__main__':
    all_books = discover_book_links(max_pages=3)
    print(f"\n Total unique book links discovered: {len(all_books)}")
    
    valid_books = []
    error_records = []
    
    os.makedirs('output', exist_ok=True)
    
    print("\n[PROCESSING] Scraping and validating 60 books...")
    for idx, book_url in enumerate(all_books, 1):
        source_page_num = ((idx - 1) // 20) + 1
        source_page_url = f"https://books.toscrape.com/catalogue/page-{source_page_num}.html"
        
        try:
            raw_record = parse_book_page(book_url, source_page_url)
            validated_book = normalize_and_validate(raw_record)

            valid_books.append(validated_book.model_dump(mode='json'))
        except Exception as e:
            error_records.append({
                "url": book_url,
                "error": str(e)
            })
            
    with open('output/books.json', 'w', encoding='utf-8') as f:
        json.dump(valid_books, f, indent=2, ensure_ascii=False)
        
    with open('output/errors.json', 'w', encoding='utf-8') as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)
        
    print(f"\n Finished Successfully!")
    print(f" Saved {len(valid_books)} valid books to output/books.json")
    print(f" Saved {len(error_records)} errors to output/errors.json")