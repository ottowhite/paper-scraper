from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage, get_cached_webpage_via_selenium
from retrieve_paper_info import get_info_from_semantic_scholar

class ConferenceScraper:
	def __init__(self, conference_name, top_level_url):
		self.conference_name = conference_name
		self.top_level_soup = BeautifulSoup(get_cached_webpage(top_level_url), 'html.parser')
		self.sessions = {}
		self.sessions_and_links = []
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

	def extract(self):
		self.extract_session_titles_and_links()
		self.extract_sessions()
		self.populate_missing_abstracts_and_links()
		self.print_stats()

		return self.sessions

	def extract_session_titles_and_links(self):
		bucket_divs = self.top_level_soup.find_all('div', class_=lambda x: x and 'pretalx-tab-content' in x)

		links = []
		for bucket_div in bucket_divs:
			links.extend(bucket_div.find_all('a'))

		for link in links:
			if not "talk" in link['href']:
				continue

			session_title = link.find('div', class_='title').text.strip()
			if any(ignore_session in session_title for ignore_session in self.ignore_sessions):
				continue

			full_url = "https://download.vusec.net" + link['href']
			self.sessions_and_links.append((session_title, full_url))
	
	def extract_sessions(self):
		assert len(self.sessions_and_links) != 0

		for session_title, full_url in self.sessions_and_links:
			soup = BeautifulSoup(get_cached_webpage(full_url), 'html.parser')

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

			self.sessions[session_title] = papers
	
	def populate_missing_abstracts_and_links(self):
		self.populate_missing_abstracts_and_links_from_semantic_scholar()
		self.populate_missing_abstracts_from_paper_links()

	def populate_missing_abstracts_and_links_from_semantic_scholar(self):
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
				print(abstract_text)
	
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

	def get_sessions(self):
		return self.sessions
