import os
import sys
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from qdrant_db.storage import CollegeDB
from scraper.sources import find_college_url
from scraper.scraper import CollegeScraper

def main():
    print("=================================================")
    print("🎓 College Data Agent (Qdrant Powered)")
    print("=================================================")
    
    # 1. User Input
    if len(sys.argv) > 1:
        college_name = " ".join(sys.argv[1:])
    else:
        college_name = input("👉 Enter College Name: ").strip()

    if not college_name:
        print("❌ No name entered.")
        return

    # 2. Check Database
    db = CollegeDB()
    existing_data = db.search_college(college_name)
    
    if existing_data:
        print("\n✅ DATA FOUND IN LOCAL STORE:")
        print(json.dumps(existing_data, indent=2, default=str))
        return

    # 3. Not found? Scrape it.
    print(f"\nCreating new entry for '{college_name}'...")
    
    url = find_college_url(college_name)
    if not url:
        print("❌ Could not find an official website.")
        return

    scraper = CollegeScraper()
    # The scraper uses the URL to fetch data. 
    scraped_data = scraper.scrape(college_name, url=url)
    
    # 4. Save to DB
    success = db.save_college(scraped_data)
    
    if success:
        print("\n🎉 Success! Data saved to Knowledge Base.")
        print(json.dumps(scraped_data, indent=2, default=str))
    else:
        print("⚠️ Failed to save data.")

if __name__ == "__main__":
    main()
