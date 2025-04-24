from utils import flat_map
from retrieve_webpage import get_cached_webpage
from bs4 import BeautifulSoup
from ScrapingStrategies import AbstractScrapingStrategy1
from typing import List, Tuple, Dict
from ConferenceScraper import ConferenceScraper

class MLSysScraper(AbstractScrapingStrategy1):
	def __init__(self, conference_name: str):
		self.ignore_session_titles = [
			"Poster",
			"Overflow",
			"Creative AI Session"
		]
		self.conference_name = conference_name

	def extract_session_titles_and_links(self, top_level_soup: BeautifulSoup) -> List[Tuple[str, str]]:
		timebox_divs = top_level_soup.find_all('div', class_='timebox')
		session_title_divs = flat_map(lambda timebox_div: timebox_div.find_all('div', class_='sessiontitle'), timebox_divs)

		sessions_and_links = []
		for session_title_div in session_title_divs:
			session_title = session_title_div.text.strip()
			session_title = session_title.split("\n")[0]

			if any(ignore_title in session_title for ignore_title in self.ignore_session_titles):
				continue

			if self.conference_name == "neurips24":
				# Drop first two words of session title
				session_title = " ".join(session_title.split(" ")[2:])

			if self.conference_name == "mlsys24":
				session_link = f"https://mlsys.org{session_title_div.find('a')['href']}"
			elif self.conference_name == "neurips24":
				session_link = f"https://neurips.cc{session_title_div.find('a')['href']}"
			else:
				raise ValueError(f"Unknown conference: {self.conference_name}")

			sessions_and_links.append((session_title, session_link))

		return sessions_and_links

	def link_to_papers(self, session_link: str) -> List[Dict[str, str]]:
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

		return papers


if __name__ == "__main__":
	mlsys24_scraper = ConferenceScraper(
		"mlsys24",
		"https://mlsys.org/virtual/2024/calendar",
		MLSysScraper("mlsys24")
	)
	mlsys24_scraper.extract()
	mlsys24_scraper.save_sessions(force_overwrite=False)

	# neurips24_scraper = ConferenceScraper(
	# 	"neurips24",
	# 	"https://neurips.cc/virtual/2024/calendar",
	# 	MLSysScraper("neurips24")
	# )
	# neurips24_scraper.extract()
	# neurips24_scraper.save_sessions(force_overwrite=False)
