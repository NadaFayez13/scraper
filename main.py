import os
import time
from bs4 import BeautifulSoup
import requests 
from urllib.parse import urljoin
from datetime import datetime, timezone
import hashlib


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
    
    print("\n[TEST] Parsing first book record...")
    sample_record = parse_book_page(all_books[0], 'https://books.toscrape.com/catalogue/page-1.html')
    
    import json
    print(json.dumps(sample_record, indent=2, ensure_ascii=False))