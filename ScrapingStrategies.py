from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict

class AbstractScrapingStrategy1(ABC):
	
	# Extracts a list of session titles, and links to the session pages
	@abstractmethod
	def extract_session_titles_and_links(
		self,
		top_level_soup: BeautifulSoup
	) -> List[Tuple[str, str]]:
		pass

	# Given a link to a session page, extracts a list of papers in the session
	@abstractmethod
	def link_to_papers(
		self,
		session_link: str
	) -> List[Dict[str, str]]:
		pass

class AbstractScrapingStrategy2(ABC):
	
	# Extracts sessions immediately as all information in the top-level page
	@abstractmethod
	def extract_sessions(
		self,
		top_level_soup: BeautifulSoup
	) -> List[Tuple[str, str]]:
		pass