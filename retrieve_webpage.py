import requests
import os
import hashlib
import time
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

semantic_scholar_rate_limit_sleep_time = 2
other_rate_limit_sleep_time = 60

DEBUG = False

def get_cached_webpage(url, params=None, headers=None, cache_dir=".cache", response_type="html", target_url="other", pre_render=False):
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
    if target_url == "other":
        if headers is None:
            headers = {}

        headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"

        if pre_render:
            session = HTMLSession()
            response = session.get(url, headers=headers, params=params)
            response.html.render()
            response_text = response.html.raw_html
        else:
            response = requests.get(url, headers=headers, params=params)
            response_text = response.text

    if response.status_code != 200:
        if response.status_code == 429:
            # Rate limit exceeded
            if target_url == "semantic_scholar":
                print(f"Rate limited at {semantic_scholar_rate_limit_sleep_time}s, doubling the sleep time to {2 * semantic_scholar_rate_limit_sleep_time}s.")
                semantic_scholar_rate_limit_sleep_time *= 2
            else:
                print(f"Rate limited at {other_rate_limit_sleep_time}s, doubling the sleep time to {2 * other_rate_limit_sleep_time}s.")
                other_rate_limit_sleep_time *= 2

            return get_cached_webpage(url, params, cache_dir, response_type, pre_render)

        raise Exception(f"Failed to retrieve the webpage: Status code {response.status_code}, output: {response_text}")
    
    # Save to cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(response_text)
    
    return response_text

def get_cached_webpage_via_selenium(url):
    assert "dl.acm.org" in url

    # Cache the webpage
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(".cache", f"{url_hash}.html")
    if DEBUG:
        print(f"Cache file: {cache_file}")
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()

    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

	# Ensure that the webpage has rendered fully
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.minimize_window()
    # Wait for 60 seconds for the page to load, and for the request to look less suspicious
    print(f"Sleeping for {other_rate_limit_sleep_time}s...")
    # Wait for 5 seconds to ensure the page is loaded
    time.sleep(5)
    # Save to cache
    html = driver.page_source
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Wait for the remaining time to not be rate limited
    time.sleep(other_rate_limit_sleep_time - 5)

    driver.quit()

    return html
