from utils import flat_map
from retrieve_webpage import get_cached_webpage
from bs4 import BeautifulSoup
from ScrapingStrategies import AbstractScrapingStrategy1
from typing import List, Tuple, Dict
from ConferenceScraper import ConferenceScraper

class MLSysScraper(AbstractScrapingStrategy1):
	def extract_session_titles_and_links(self, top_level_soup: BeautifulSoup) -> List[Tuple[str, str]]:
		timebox_divs = top_level_soup.find_all('div', class_='timebox')
		session_title_divs = flat_map(lambda timebox_div: timebox_div.find_all('div', class_='sessiontitle'), timebox_divs)

		sessions_and_links = []
		for session_title_div in session_title_divs:
			session_title = session_title_div.text.strip()
			session_title = session_title.split("\n")[0]

			if "Poster" in session_title:
				continue

			session_link = f"https://mlsys.org{session_title_div.find('a')['href']}"
			sessions_and_links.append((session_title, session_link))

		return sessions_and_links

	def extract_sessions(self, sessions_and_links: List[Tuple[str, str]]) -> Dict[str, List[Dict[str, str]]]:
		sessions = {}
		for session_title, session_link in sessions_and_links:
			session_soup = BeautifulSoup(get_cached_webpage(session_link), 'html.parser')

			paper_divs = session_soup.find_all('div', class_='track-schedule-card')
			papers = []
			for paper_div in paper_divs:
				paper_title = paper_div.find('a').text.strip()

				paper_link = f"https://mlsys.org{paper_div.find('a')['href']}"
				authors = paper_div.find('p', class_='text-muted').text.strip()
				abstract = paper_div.find('div', class_='abstract').text.strip()

				papers.append({
					"title": paper_title,
					"authors": authors,
					"abstract": abstract,
					"link": paper_link,
				})

			sessions[session_title] = papers

		return sessions


if __name__ == "__main__":
	scraper = ConferenceScraper(
		"mlsys24",
		"https://mlsys.org/virtual/2024/calendar",
		MLSysScraper()
	)
	scraper.extract()
	scraper.save_sessions(force_overwrite=False)