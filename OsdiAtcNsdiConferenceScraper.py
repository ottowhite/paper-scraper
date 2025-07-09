from bs4 import BeautifulSoup
from typing import List, Tuple
from ScrapingStrategies import AbstractScrapingStrategy2

class OsdiAtcNsdiConferenceScraper(AbstractScrapingStrategy2):
    def __init__(self, conference_name: str):
        self.conference_name = conference_name

    def extract_sessions(self, top_level_soup: BeautifulSoup) -> List[Tuple[str, str]]:
        session_divs = top_level_soup.find_all('article', class_=lambda c: c and 'node-session' in c)
        return self.parse_sessions(session_divs, self.conference_name)

    def parse_sessions(self, session_divs, conference_name):
        sessions = {}

        for session_div in session_divs:
            session_title, papers = self.parse_session(session_div)
            sessions[session_title] = papers
    
        return sessions

    def parse_session(self, session_div):
        session_title = session_div.find('h2').get_text(strip=True)

        paper_divs = session_div.find_all('article', class_='node-paper')
        papers = []
        for paper_div in paper_divs:
            papers.append(self.parse_paper(paper_div))

        return session_title, papers

    def parse_paper(self, paper_div):
        paper_title = paper_div.find('a').get_text(strip=True)
        paper_link = f"https://www.usenix.org{paper_div.find('a')['href']}"

        authors_div = paper_div.find('div', class_='field-name-field-paper-people-text')
        authors = authors_div.find('p').get_text(strip=True) if authors_div else ""
        # authors = parse_authors_osdi_nsdi_atc(authors)

        abstract_div = paper_div.find('div', class_='field-name-field-paper-description-long')

        if abstract_div is None:
            abstract = ""
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