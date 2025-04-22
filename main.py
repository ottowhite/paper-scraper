import requests
from bs4 import BeautifulSoup
import json
import re
import os
import hashlib
from datetime import datetime, timedelta
from retrieve_webpage import get_cached_webpage
from saving import save_to_notion_format, save_to_json
from retrieve_paper_info import get_info_from_semantic_scholar, get_abstract_from_osdi_nsdi_atc_link
from dotenv import load_dotenv
from scrape_osdi_atc_nsdi import scrape_sessions
from scrape_sosp24 import scrape_sessions_sosp24
from scrape_sosp_old import scrape_sessions_sosp_old
from scrape_eurosys import scrape_sessions_eurosys
from scrape_eurosys22 import scrape_sessions_eurosys22
from ConferenceScraper import ConferenceScraper

def scrape_and_save(url, conference_name, filename_prefix):
    if conference_name == "atc" or conference_name == "nsdi" or conference_name == "osdi":
        data = scrape_sessions(url, conference_name)
    elif conference_name == "sosp24":
        data = scrape_sessions_sosp24(url)
    elif conference_name in ["sosp23", "sosp21", "sosp19"]:
        data = scrape_sessions_sosp_old(url, conference_name)
    elif conference_name in ["eurosys24", "eurosys23"]:
        data = scrape_sessions_eurosys(url, conference_name)
    elif conference_name in ["eurosys22", "eurosys21"]:
        data = scrape_sessions_eurosys22(url, conference_name)
    elif conference_name == "eurosys25":
        assert url is None
        scraper = ConferenceScraper("eurosys25", "https://download.vusec.net/asplos-eurosys-2025/schedule/nojs")
        data = scraper.extract()
    else:
        raise ValueError(f"Invalid conference name: {conference_name}")

    save_to_json(data, f"{filename_prefix}.json")
    save_to_notion_format(data, f"{filename_prefix}.notion.txt")
    print(f"Scraping completed successfully! ({filename_prefix})")


if __name__ == "__main__":
    load_dotenv()
    assert os.getenv("SEMANTIC_SCHOLAR_API_KEY") is not None

    # for year in range(20, 25):
    #     scrape_and_save(f"https://www.usenix.org/conference/osdi{year}/technical-sessions", "osdi", f"osdi{year}_sessions")
    #     scrape_and_save(f"https://www.usenix.org/conference/atc{year}/technical-sessions", "atc", f"atc{year}_sessions")
    
    # scrape_and_save("https://sigops.org/s/conferences/sosp/2024/schedule.html", "sosp24", "sosp24_sessions")


    # for year in range(20, 26):
    #     scrape_and_save(f"https://www.usenix.org/conference/nsdi{year}/technical-sessions", "nsdi", f"nsdi{year}_sessions")

    # scrape_and_save("https://sosp2023.mpi-sws.org/program.html", "sosp23", "sosp23_sessions")
    # scrape_and_save("https://sosp2021.mpi-sws.org/program.html", "sosp21", "sosp21_sessions")
    # scrape_and_save("https://www.sigops.org/s/conferences/sosp/2019/program.html", "sosp19", "sosp19_sessions")

    # scrape_and_save("https://2024.eurosys.org/program.html", "eurosys24", "eurosys24_sessions")
    # scrape_and_save("https://2023.eurosys.org/program.html", "eurosys23", "eurosys23_sessions")
    # scrape_and_save("https://2022.eurosys.org/index.html@p=494.html", "eurosys22", "eurosys22_sessions")
    # scrape_and_save("https://2021.eurosys.org/papers.html#papers", "eurosys21", "eurosys21_sessions")
    scrape_and_save(None, "eurosys25", "eurosys25_sessions")
