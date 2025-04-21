import requests
import os
import hashlib
import time

rate_limit_sleep_time = 60

def get_cached_webpage(url, params=None, cache_dir=".cache", response_type="html"):
    """
    Get webpage content from cache or download it if not cached.
    Returns the webpage content as a string.
    """
    global rate_limit_sleep_time
    assert response_type in ["html", "json"]

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    print(f"Retrieving webpage {url}")
    
    # Create a unique filename based on the URL and params if present
    if params:
        hash_input = url + str(params)
    else:
        hash_input = url
    url_hash = hashlib.md5(hash_input.encode()).hexdigest()

    if response_type == "html":
        cache_file = os.path.join(cache_dir, f"{url_hash}.html")
    else:
        cache_file = os.path.join(cache_dir, f"{url_hash}.json")
    print(f"Cache file: {cache_file}")

    # Check if cache exists
    if os.path.exists(cache_file):
        print("Using cached webpage...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()

    # Wait 2s on the retrieve path to avoid being blocked by the server
    print(f"Sleeping for {rate_limit_sleep_time}s...")
    time.sleep(rate_limit_sleep_time)
    
    # Download the webpage if cache doesn't exist
    print("Downloading webpage...")
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    headers = None
    if params is not None:
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 429:
            # Rate limit exceeded
            print(f"Rate limited at {rate_limit_sleep_time}s, doubling the sleep time to {2 * rate_limit_sleep_time}s.")
            print(response.text)
            rate_limit_sleep_time *= 2

            return get_cached_webpage(url, params, cache_dir, response_type)

        raise Exception(f"Failed to retrieve the webpage: Status code {response.status_code}")
    
    # Save to cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text