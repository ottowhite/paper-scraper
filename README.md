# Conference Web Scraper

A Python-based web scraper designed to extract and organize academic conference papers and sessions from various computer science conferences, including OSDI, NSDI, ATC, and SOSP.

## Overview

This tool automatically scrapes conference websites to collect information about:
- Conference sessions
- Paper titles
- Authors
- Abstracts
- Paper links

The scraped data is saved in two formats:
1. JSON format for easy programmatic access
2. Notion-compatible format for easy import into Notion

## Features

- **Conference Support**: Currently supports scraping from:
  - OSDI (Operating Systems Design and Implementation)
  - NSDI (Networked Systems Design and Implementation)
  - ATC (USENIX Annual Technical Conference)
  - SOSP (Symposium on Operating Systems Principles)

- **Paper Information Enhancement**: Automatically fetches additional paper information from Google Scholar, including:
  - Abstracts
  - Direct paper links

- **Caching System**: Implements a caching mechanism to avoid repeated requests to conference websites and Google Scholar

- **Multiple Output Formats**:
  - JSON format for data processing
  - Notion-compatible format for easy import into Notion

## Requirements

- Python 3.x
- Required Python packages:
  - requests
  - beautifulsoup4
  - urllib3

## Usage

1. Clone the repository:
```bash
git clone https://github.com/yourusername/conference-web-scraper.git
cd conference-web-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scraper:
```bash
python main.py
```

The script will automatically scrape the supported conferences and save the results in both JSON and Notion formats.

## Output

The scraper generates two types of files for each conference:
- `{conference_name}_sessions.json`: Contains the structured data in JSON format
- `{conference_name}_sessions.notion.txt`: Contains the data formatted for Notion import

## Project Structure

- `main.py`: Main script containing the scraping logic
- `retrieve_webpage.py`: Handles webpage retrieval and caching
- `retrieve_paper_info.py`: Fetches additional paper information from Google Scholar
- `saving.py`: Handles saving data in different formats
- `notion_format/`: Directory for Notion-formatted output
- `json_format/`: Directory for JSON-formatted output
- `.cache/`: Directory for storing cached webpage content to avoid repeated requests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
