from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage
from retrieve_paper_info import get_info_from_semantic_scholar

def scrape_sessions_eurosys(url):
    html_content = get_cached_webpage(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    return parse_document_eurosys(soup)

def parse_document_eurosys(soup):
    session_tds = soup.find_all('td', class_='sch')
    sessions = {}
    for session_td in session_tds:
        if session_td.get("id") is None:
            continue

        if not session_td.get("id").startswith("session_"):
            continue

        session_title = session_td.find("strong").text.split("(")[0].strip()

        sessions[session_title] = []
        
        li_elements = session_td.find_all("li")
        # bs4 gives entire list as a string, as text gives all elements within the div (or similar)
        authors_lists = list(map(lambda li: li.find("small").text.strip(), li_elements))

        # Generate list of paper names
        paper_names = li_elements[0].text.strip()
        for authors_list in authors_lists:
            paper_names = paper_names.replace(authors_list, "")
        
        paper_names = paper_names.split("\n")
        assert len(paper_names) == len(authors_lists)
        
        for paper_name, authors_list in zip(paper_names, authors_lists):
            abstract, link = get_info_from_semantic_scholar(paper_name)
            paper = {
                "title": paper_name,
                "authors": authors_list,
                "abstract": abstract,
                "link": link,
            }
            sessions[session_title].append(paper)
        
    return sessions