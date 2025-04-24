from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage
from ScrapingStrategies import AbstractScrapingStrategy1
from typing import List, Dict, Tuple
from ConferenceScraper import ConferenceScraper
class EuroSys25ConferenceScraper(AbstractScrapingStrategy1):
	def __init__(self):
		self.ignore_sessions = [
			"Martin",
			"Registration",
			"Keynote",
			"Coffee",
			"Lunch",
			"Dinner",
			"Closing",
			"Opening",
			"Award",
			"general assembly",
			"WACI",
			"ASPLOS business meeting"
		]

	def extract_session_titles_and_links(self, top_level_soup: BeautifulSoup) -> List[Tuple[str, str]]:
		bucket_divs = top_level_soup.find_all('div', class_=lambda x: x and 'pretalx-tab-content' in x)

		links = []
		for bucket_div in bucket_divs:
			links.extend(bucket_div.find_all('a'))

		sessions_and_links = []
		for link in links:
			if not "talk" in link['href']:
				continue

			session_title = link.find('div', class_='title').text.strip()
			if any(ignore_session in session_title for ignore_session in self.ignore_sessions):
				continue

			full_url = "https://download.vusec.net" + link['href']
			sessions_and_links.append((session_title, full_url))

		return sessions_and_links
	
	def link_to_papers(self, session_link: str) -> List[Dict[str, str]]:
		soup = BeautifulSoup(get_cached_webpage(session_link), 'html.parser')

		papers = []
		description_section = soup.find('section', class_='description')
		paragraphs = description_section.find_all('p')
		for paragraph in paragraphs:
			if "session chair" in paragraph.text.strip().lower():
				continue

			paragraph_text = paragraph.text.strip()
			paper_title = paragraph.find('strong').text.strip()
			authors = paragraph_text.replace(paper_title, "").replace("Paper", "").strip()
			link = paragraph.find('a')['href']

			papers.append({
				"title": paper_title,
				"authors": authors,
				"abstract": "",
				"link": link
			})

		return papers

if __name__ == "__main__":
	scraper = ConferenceScraper(
		"eurosys25",
		"https://download.vusec.net/asplos-eurosys-2025/schedule/nojs",
		EuroSys25ConferenceScraper()
	)
	scraper.extract()
	scraper.save_sessions(force_overwrite=False)