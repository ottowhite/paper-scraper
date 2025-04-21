from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage
from retrieve_paper_info import get_info_from_semantic_scholar

def flat_map(f, xs):
    ys = []
    for x in xs:
        ys.extend(f(x))
    return ys

def scrape_sessions_sosp_old(url, conference_name):
    assert conference_name in ["sosp21", "sosp23", "sosp19"], "Invalid conference name"

    html_content = get_cached_webpage(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    return parse_document_sosp_old(soup, conference_name)

def parse_document_sosp_old(soup, conference_name):
    if conference_name == "sosp19":
        program_div = soup.find('div', class_='main-text')
    else:
        program_div = soup.find('div', class_='program')

    if conference_name == "sosp21":
        days_container_div = program_div.find_all('div', class_='col-md-12')[0]
    elif conference_name in ["sosp23", "sosp19"]:
        days_container_div = program_div.find_all('div', class_='col-md-12')[1]

    table_divs = days_container_div.find_all('table', class_='table-spread')
    table_rows = flat_map(lambda table_div: table_div.find_all('tr'), table_divs)

    sessions = {}

    i = 0
    while i < len(table_rows) and "Closing" not in table_rows[i].text:
        # Find the next session
        while table_rows[i].get('class') != ['info']:
            i += 1
            if i >= len(table_rows):
                break
        
        if i >= len(table_rows):
            break

        if conference_name == "sosp19":
            session_title = table_rows[i].find('strong').text.strip()
            session_title = session_title.split("\n\t")[0]
        else:
            session_title = table_rows[i].find('strong').text.strip()

        papers = []
        # Get all papers in the session
        # Every paper has a link, and then the authors follow it
        while i < len(table_rows) and table_rows[i].get('class') != ['success']:
            # If there is a link in this row, then it's a paper
            if table_rows[i].find('a'):
                # Get the paper name
                paper_name = table_rows[i].find_all('a')[-1].text.strip()
                paper_link = table_rows[i].find_all('a')[-1]['href']

                # The authors follow it
                i += 1
                authors = table_rows[i].text.strip()

                abstract, _ = get_info_from_semantic_scholar(paper_name)
                papers.append({
                    "title": paper_name,
                    "authors": authors,
                    "abstract": abstract,
                    "link": paper_link,
                })
            
            i += 1

        # Get all papers in the session
        sessions[session_title] = papers
        i += 1

    return sessions