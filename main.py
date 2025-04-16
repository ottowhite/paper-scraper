import requests
from bs4 import BeautifulSoup
import json
import re
import os
import hashlib
from datetime import datetime, timedelta

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

def scrape_sessions(url, conference_name):
    # Get webpage content (from cache or download)
    html_content = get_cached_webpage(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    sessions = parse_document(soup, conference_name)
    return sessions

def parse_document(soup, conference_name):
    session_divs = soup.find_all('article', class_=lambda c: c and 'node-session' in c)
    return parse_sessions(session_divs, conference_name)

def parse_sessions(session_divs, conference_name):
    sessions = {}

    for session_div in session_divs:
        session_title, papers = parse_session(session_div, conference_name)
        sessions[session_title] = papers
    
    return sessions

def parse_session(session_div, conference_name):
    session_title = session_div.find('h2').get_text(strip=True)

    paper_divs = session_div.find_all('article', class_='node-paper')
    papers = []
    for paper_div in paper_divs:
        papers.append(parse_paper(paper_div, conference_name))

    return session_title, papers

def parse_paper(paper_div, conference_name):
    paper_title = paper_div.find('a').get_text(strip=True)
    paper_link = f"https://www.usenix.org{paper_div.find('a')['href']}"

    authors_div = paper_div.find('div', class_='field-name-field-paper-people-text')
    authors = authors_div.find('p').get_text(strip=True) if authors_div else ""
    # authors = parse_authors_osdi_nsdi_atc(authors)

    abstract_div = paper_div.find('div', class_='field-name-field-paper-description-long')

    if abstract_div is None:
        print(f"abstract_div is None for {paper_title}")
        abstract = []
    else:
        abstract = abstract_div.find_all('p')

    if len(abstract) >= 1:
        abstract = "\n".join([p.get_text(strip=True) for p in abstract])
    elif len(abstract) == 0:
        abstract = ""
    
    return {
        "title": paper_title,
        "authors": authors,
        "abstract": abstract,
        "link": paper_link
    }

def parse_authors_intitution_pair(author_institution_pair):
    authors_processed = []

    institution = author_institution_pair.split(",")[-1]
    authors = author_institution_pair.split(",")[:-1]
    for author in authors:
        author = author.strip()
        institution = institution.strip()

        if author.startswith("and"):
            author = author[4:].strip()

        authors_processed.append({
            "name": author,
            "institution": institution
        })

    return authors_processed

def parse_authors_osdi_nsdi_atc(authors):
    if authors == "":
        return []

    authors_processed = []
    if ";" in authors:
        author_institutions = authors.split(";")
        for author_institution_pair in author_institutions:
            authors_processed.extend(parse_authors_intitution_pair(author_institution_pair))
    else:
        authors_processed.extend(parse_authors_intitution_pair(authors))
    
    return authors_processed

def save_to_notion_format(data, filename="osdi24_sessions.notion.txt"):
    """Save the scraped data to a Notion format file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for session_title, papers in data.items():
            f.write(f" - {session_title}\n")
            for paper in papers:
                
                if isinstance(paper['authors'], list):
                    for author in paper['authors']:
                        f.write(f"     - {author['name']} ({author['institution']})\n")
                else:
                    f.write(f"     - {paper['authors']}\n")
                f.write(f"     - {paper['abstract']}\n")
                f.write(f"     - {paper['link']}\n")

def save_to_json(data, filename="osdi24_sessions.json"):
    """Save the scraped data to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")

def scrape_and_save(url, conference_name, filename_prefix):
    data = scrape_sessions(url, conference_name)
    if data:
        save_to_json(data, f"{filename_prefix}.json")
        save_to_notion_format(data, f"{filename_prefix}.notion.txt")
        print(f"Scraping completed successfully! ({filename_prefix})")
    else:
        print(f"Scraping failed. ({filename_prefix})")

if __name__ == "__main__":
    # for year in range(20, 25):
    #     scrape_and_save(f"https://www.usenix.org/conference/osdi{year}/technical-sessions", "osdi", f"osdi{year}_sessions")
        # scrape_and_save(f"https://www.usenix.org/conference/atc{year}/technical-sessions", "atc", f"atc{year}_sessions")
    
    scrape_and_save("https://www.usenix.org/conference/atc21/technical-sessions", "atc", "atc21_sessions")


    # for year in range(20, 26):
    #     scrape_and_save(f"https://www.usenix.org/conference/nsdi{year}/technical-sessions", "nsdi", f"nsdi{year}_sessions")

 
