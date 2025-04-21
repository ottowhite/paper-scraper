import requests
from bs4 import BeautifulSoup
import json
import re
import os
import hashlib
from datetime import datetime, timedelta
from retrieve_webpage import get_cached_webpage
from saving import save_to_notion_format, save_to_json
from retrieve_paper_info import get_info_from_semantic_scholar, get_abstract_from_osdi_nsdi_atc_link
from dotenv import load_dotenv

def scrape_sessions_sosp24(url):
    # Get webpage content (from cache or download)
    html_content = get_cached_webpage(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    return parse_document_sosp24(soup)

def parse_document_sosp24(soup):
    session_titles = []
    schedule_div = soup.find('section', id='schedule').find('div', class_='container')
    session_title_h4s = soup.find_all('h4', class_='sch')

    for session_title_h4 in session_title_h4s:
        if "Session" not in session_title_h4.text or "Poster" in session_title_h4.text:
            continue

        session_title = session_title_h4.text.strip().split("\n")[0].strip()
        session_titles.append(session_title)

    titles = soup.find_all('a', href=lambda h: 'assets/papers/' in h)
    papers = []

    for title in titles:
        print(title.text.strip())
        authors = title.parent.find_next('em').text.strip()
        print(authors)
        abstract, link = get_info_from_semantic_scholar(title.text.strip())
        papers.append({
            "title": title.text.strip(),
            "authors": authors,
            "abstract": abstract,
            "link": link
        })

    papers_in_each_session = [4, 4, 5, 4, 4, 4, 5, 4, 4, 5]
    assert len(papers_in_each_session) == len(session_titles)
    session_titles_and_paper_counts = list(zip(session_titles, papers_in_each_session))
    assert len(papers) == sum(papers_in_each_session)

    sessions = {}
    for session_title, papers_in_session in session_titles_and_paper_counts:
        sessions[session_title] = papers[:papers_in_session]
        papers = papers[papers_in_session:]

    return sessions

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
        abstract, _ = get_info_from_semantic_scholar(paper_title)
        if abstract == "":
            abstract = get_abstract_from_osdi_nsdi_atc_link(paper_link)
    else:
        abstract_paragraphs = abstract_div.find_all('p')

        if len(abstract_paragraphs) >= 1:
            abstract = "\n".join([p.get_text(strip=True) for p in abstract_paragraphs])
        else:
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

def scrape_and_save(url, conference_name, filename_prefix):
    if conference_name == "atc" or conference_name == "nsdi" or conference_name == "osdi":
        data = scrape_sessions(url, conference_name)
    elif conference_name == "sosp24":
        data = scrape_sessions_sosp24(url)

    save_to_json(data, f"{filename_prefix}.json")
    save_to_notion_format(data, f"{filename_prefix}.notion.txt")
    print(f"Scraping completed successfully! ({filename_prefix})")


if __name__ == "__main__":
    load_dotenv()
    assert os.getenv("SEMANTIC_SCHOLAR_API_KEY") is not None

    # for year in range(20, 25):
    #     scrape_and_save(f"https://www.usenix.org/conference/osdi{year}/technical-sessions", "osdi", f"osdi{year}_sessions")
    #     scrape_and_save(f"https://www.usenix.org/conference/atc{year}/technical-sessions", "atc", f"atc{year}_sessions")
    
    # scrape_and_save("https://sigops.org/s/conferences/sosp/2024/schedule.html", "sosp24", "sosp24_sessions")


    # for year in range(20, 26):
    #     scrape_and_save(f"https://www.usenix.org/conference/nsdi{year}/technical-sessions", "nsdi", f"nsdi{year}_sessions")

    scrape_and_save("https://www.usenix.org/conference/nsdi25/technical-sessions", "nsdi", "nsdi25_sessions")
