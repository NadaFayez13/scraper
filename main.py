import os
import time
import requests

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
    response.raise_for_status()  # يتأكد إن الـ Status Code هو 200 OK
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
        
    return response.text

if __name__ == '__main__':
    html_content = fetch_page(URL_PAGE_1, 'catalogue-page-1.html')
    print(" Done! Page 1 fetched and cached successfully.")