import requests
from bs4 import BeautifulSoup
import json
import time
from .cleaner import clean_text

class CollegeScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape(self, college_name, url=None):
        """
        Main entry point. If URL is provided, scrapes it.
        """
        data = {
           "university_name": college_name,
           "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "location": "India", # Default
           "courses": {"Other": []},
           "overview": ""
        }

        if url:
            print(f"🌍 Scraping content from: {url}")
            try:
                # 1. Fetch Page
                res = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(res.text, "html.parser")
                
                # 2. Extract Title / Meta Description
                title = soup.title.string if soup.title else college_name
                desc = ""
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    desc = meta_desc.get("content", "")
                
                # 3. Extract Text Content (Basic)
                # In a real agent, we'd go deeper, but this is 'Shape Up' step 1.
                paragraphs = [p.get_text() for p in soup.find_all('p')]
                full_text = " ".join(paragraphs[:10]) # First 10 paragraphs for overview
                
                data["overview"] = clean_text(desc + " " + full_text)[:1000] # Limit size
                data["college_url"] = url
                
                # 4. Attempt to find Courses (Heuristic)
                # Look for 'B.Tech', 'M.Tech' in links
                courses = set()
                for link in soup.find_all('a', href=True):
                    txt = link.get_text().lower()
                    if 'b.tech' in txt or 'engineering' in txt:
                        courses.add(clean_text(link.get_text()))
                
                if courses:
                    data["courses"]["BTech"] = list(courses)[:5]
                
            except Exception as e:
                print(f"⚠️ Scraping error: {e}")
        
        return data
