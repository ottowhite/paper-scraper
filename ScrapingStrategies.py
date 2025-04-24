from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict

class AbstractScrapingStrategy1(ABC):
	@abstractmethod
	def extract_session_titles_and_links(
		self,
		top_level_soup: BeautifulSoup
	) -> List[Tuple[str, str]]:
		pass

	@abstractmethod
	def extract_sessions(
		self,
		session_titles_and_links: List[Tuple[str, str]]
	) -> Dict[str, List[Dict[str, str]]]:
		pass
