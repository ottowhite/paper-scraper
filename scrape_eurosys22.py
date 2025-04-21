from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage
from retrieve_paper_info import get_info_from_semantic_scholar

def scrape_sessions_eurosys22(url, conference_name):
    assert conference_name in ["eurosys22", "eurosys21"]

    html_content = get_cached_webpage(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    return parse_document_eurosys22(soup, conference_name)

def parse_document_eurosys22(soup, conference_name):
    if conference_name == "eurosys21":
        entry_content_div = soup.find('div', class_='text-justify')
    else:
        entry_content_div = soup.find('div', class_='entry-content')
    
    sessions = {}

    if conference_name == "eurosys21":
        titles = entry_content_div.find_all('h3', class_='section-subheading')
    else:
        titles = entry_content_div.find_all('h5')

    for title in titles:
        if conference_name == "eurosys22":
            if title.get("id") is None:
                continue

        if title.text == "Workshops":
            continue

        if "Poster" in title.text:
            continue

        if "Cocktail" in title.text:
            continue

        if "General Assembly" in title.text:
            continue

        if "Ask Me Anything" in title.text:
            continue

        if conference_name == "eurosys22":
            if "–" in title.text:
                session_title = title.text.split("–")[1].strip()
            else:
                session_title = title.text.strip()
        elif conference_name == "eurosys21":
            session_title = title.text.split(":")[1].strip().split("(")[0].strip()

        sessions[session_title] = []

        # Get the list after this title
        paper_li_elements = title.find_next('ul').find_all('li')

        if conference_name == "eurosys22":
            for paper in paper_li_elements:
                paper_name = paper.find('a').text.strip()
                paper_link = paper.find('a')['href']
                authors_list = paper.find('i').text.strip()
                abstract, _ = get_info_from_semantic_scholar(paper_name)

                paper = {
                    "title": paper_name,
                    "authors": authors_list,
                    "abstract": abstract,
                    "link": paper_link,
                }
                sessions[session_title].append(paper)
        elif conference_name == "eurosys21":
            for paper_li in paper_li_elements:
                paper_and_authors = paper_li.text
                authors = paper_li.find('em').text.strip()
                paper_title = paper_and_authors.replace(authors, "").strip()
                assert "," in paper_title
                last_comma_index = paper_title.rindex(",")
                paper_title = paper_title[:last_comma_index].strip()

                paper_link = paper_li.find('a')['href']

                abstract, _ = get_info_from_semantic_scholar(paper_title)

                paper = {
                    "title": paper_title,
                    "authors": authors,
                    "abstract": abstract,
                    "link": paper_link,
                }
                sessions[session_title].append(paper)


    return sessions
