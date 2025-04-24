from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage, get_cached_webpage_via_selenium
from retrieve_paper_info import get_info_from_semantic_scholar
import json
import os
from copy import deepcopy
from utils import pretty_print_diff
from ScrapingStrategies import AbstractScrapingStrategy1

class ConferenceScraper():
    def __init__(
        self,
        conference_name,
        top_level_url,
        scraping_strategy1: AbstractScrapingStrategy1 = None
    ):
        self.conference_name = conference_name
        self.top_level_soup = BeautifulSoup(get_cached_webpage(top_level_url), 'html.parser')
        self.sessions = {}
        self.sessions_and_links = []
        self.scraping_strategy1 = scraping_strategy1

    def extract(self):
        if self.scraping_strategy1 is not None:
            self.sessions_and_links = self.scraping_strategy1.extract_session_titles_and_links(
                self.top_level_soup
            )
            for session_title, session_link in self.sessions_and_links:
                papers = self.scraping_strategy1.link_to_papers(session_link)
                self.sessions[session_title] = papers

            self.populate_missing_abstracts_and_links()
            self.print_stats()
        else:
            raise ValueError("Scraping strategy 1 is not set")

    def populate_missing_abstracts_and_links(self):
        for _, papers in self.sessions.items():
            for paper in papers:
                self.try_populate_abstract_and_link_from_semantic_scholar(paper)
                self.try_populate_missing_abstracts_from_doi(paper)

    def try_populate_abstract_and_link_from_semantic_scholar(self, paper):
        if paper["abstract"] == "":
            abstract, link = get_info_from_semantic_scholar(paper["title"])
            if abstract != "":
                paper["abstract"] = abstract
            if paper["link"] == "" and link != "":
                paper["link"] = link

    def try_populate_missing_abstracts_from_doi(self, paper):
        if paper["abstract"] == "":
            if paper["link"] != "" and "doi.org" in paper["link"]:
                # If link in this format
                # https://doi.org/10.1145/3676641.3716268
                # Convert to this format
                # https://dl.acm.org/doi/10.1145/3676641.3716268
                if "doi.org" in paper["link"]:
                    dl_link = paper["link"].replace("doi.org", "dl.acm.org/doi")
                elif "dl.acm.org" in paper["link"]:
                    dl_link = paper["link"]
                else:
                    print(f"No doi found in link: {paper['link']}")
                    return

                soup = BeautifulSoup(get_cached_webpage_via_selenium(dl_link), 'html.parser')

                abstract = soup.find('section', id='abstract')
                abstract_paragraphs = abstract.find_all('div', role='paragraph')
                abstract_text = "\n".join([paragraph.text.strip() for paragraph in abstract_paragraphs])
                paper["abstract"] = abstract_text
    
    def print_stats(self):
        total_papers = 0
        for _, papers in self.sessions.items():
            total_papers += len(papers)
        total_sessions = len(self.sessions)
        missing_abstracts = 0
        missing_links = 0
        for _, papers in self.sessions.items():
            for paper in papers:
                if paper["abstract"] == "":
                    missing_abstracts += 1
                if paper["link"] == "":
                    missing_links += 1

        print(f"Conference: {self.conference_name} -----------------------------------------")
        print(f"Sessions: {total_sessions}")
        print(f"Papers: {total_papers}")
        print(f"Missing abstracts: {missing_abstracts}")
        print(f"Missing links: {missing_links}")
    
    def save_sessions(self, force_overwrite):
        self.save_to_json(force_overwrite)
        self.save_to_notion()

    def save_to_json(self, force_overwrite=False):
        """Save the scraped data to a JSON file"""
        filename = f"{self.conference_name}.json"

        if not os.path.exists("json_format"):
            os.makedirs("json_format")

        # Create JSON content in memory
        json_content = json.dumps(self.sessions, indent=2, ensure_ascii=False)

        # Read the existing JSON file if it exists
        output_file_exists = os.path.exists(f"json_format/{filename}")
        existing_content = ""
        if output_file_exists:
            with open(f"json_format/{filename}", 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        if output_file_exists and not force_overwrite:
            if existing_content != json_content:
                # Print the diff
                pretty_print_diff(existing_content, json_content)
                exit()
        
        # Write the content to file
        with open(f"json_format/{filename}", 'w', encoding='utf-8') as f:
            f.write(json_content)

        print(f"Data saved to json_format/{filename}")
    
    def save_to_notion(self):
        """Save the scraped data to a Notion format"""
        filename = f"{self.conference_name}.notion.txt"

        if not os.path.exists("notion_format"):
            os.makedirs("notion_format")

        with open(f"notion_format/{filename}", 'w', encoding='utf-8') as f:
            for session_title, papers in self.sessions.items():
                f.write(f" - {session_title}\n")
                for paper in papers:
                    temp_paper = deepcopy(paper)
                    f.write(f"   - {paper['title']}\n")
                    temp_paper.pop("title")
                    for key, value in temp_paper.items():
                        f.write(f"     - {value}\n")
        
        print(f"Data saved to notion_format/{filename}")