import json
import os

def save_to_notion_format(data, filename="osdi24_sessions.notion.txt"):
    """Save the scraped data to a Notion format file"""
    if not os.path.exists("notion_format"):
        os.makedirs("notion_format")
    with open(f"notion_format/{filename}", 'w', encoding='utf-8') as f:
        for session_title, papers in data.items():
            f.write(f" - {session_title}\n")
            for paper in papers:
                
                f.write(f"   - {paper['title']}\n")
                if isinstance(paper['authors'], list):
                    for author in paper['authors']:
                        f.write(f"     - {author['name']} ({author['institution']})\n")
                else:
                    f.write(f"     - {paper['authors']}\n")
                f.write(f"     - {paper['abstract']}\n")
                f.write(f"     - {paper['link']}\n")

def save_to_json(data, filename="osdi24_sessions.json"):
    """Save the scraped data to a JSON file"""
    if not os.path.exists("json_format"):
        os.makedirs("json_format")
    with open(f"json_format/{filename}", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")
