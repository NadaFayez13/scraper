import os
import time
from bs4 import BeautifulSoup
import requests 
from urllib.parse import urljoin

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
    print("First book link:", all_books[0])