import requests
import os
import hashlib

def get_cached_webpage(url, cache_dir=".cache"):
    """
    Get webpage content from cache or download it if not cached.
    Returns the webpage content as a string.
    """
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create a unique filename based on the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{url_hash}.html")
    
    # Check if cache exists
    if os.path.exists(cache_file):
        print("Using cached webpage...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Download the webpage if cache doesn't exist
    print("Downloading webpage...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the webpage: Status code {response.status_code}")
    
    # Save to cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text

def scrape_and_save(url, conference_name, filename_prefix):
    data = scrape_sessions(url, conference_name)
    if data:
        save_to_json(data, f"{filename_prefix}.json")
        save_to_notion_format(data, f"{filename_prefix}.notion.txt")
        print(f"Scraping completed successfully! ({filename_prefix})")
    else:
        print(f"Scraping failed. ({filename_prefix})")
