from bs4 import BeautifulSoup
from retrieve_paper_info import get_info_from_semantic_scholar
from retrieve_webpage import get_cached_webpage

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