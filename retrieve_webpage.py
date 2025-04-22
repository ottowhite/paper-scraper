import requests
import os
import hashlib
import time

semantic_scholar_rate_limit_sleep_time = 2
other_rate_limit_sleep_time = 60

DEBUG = False

def get_cached_webpage(url, params=None, headers=None, cache_dir=".cache", response_type="html", target_url="other"):
    """
    Get webpage content from cache or download it if not cached.
    Returns the webpage content as a string.
    """
    global semantic_scholar_rate_limit_sleep_time
    global other_rate_limit_sleep_time

    assert response_type in ["html", "json"]
    assert target_url in ["semantic_scholar", "other"]

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    if DEBUG:
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
    if DEBUG:
        print(f"Cache file: {cache_file}")

    # Check if cache exists
    if os.path.exists(cache_file):
        if DEBUG:
            print("Using cached webpage...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()

    # Wait 2s on the retrieve path to avoid being blocked by the server
    if target_url == "semantic_scholar":
        print(f"Sleeping for {semantic_scholar_rate_limit_sleep_time}s...")
        time.sleep(semantic_scholar_rate_limit_sleep_time)
    else:
        print(f"Sleeping for {other_rate_limit_sleep_time}s...")
        time.sleep(other_rate_limit_sleep_time)
    
    # Download the webpage if cache doesn't exist
    if DEBUG:
        print("Downloading webpage...")
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        if response.status_code == 429:
            # Rate limit exceeded
            if target_url == "semantic_scholar":
                print(f"Rate limited at {semantic_scholar_rate_limit_sleep_time}s, doubling the sleep time to {2 * semantic_scholar_rate_limit_sleep_time}s.")
                semantic_scholar_rate_limit_sleep_time *= 2
            else:
                print(f"Rate limited at {other_rate_limit_sleep_time}s, doubling the sleep time to {2 * other_rate_limit_sleep_time}s.")
                other_rate_limit_sleep_time *= 2

            return get_cached_webpage(url, params, cache_dir, response_type)

        raise Exception(f"Failed to retrieve the webpage: Status code {response.status_code}")
    
    # Save to cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text