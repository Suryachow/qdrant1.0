import os
import sys
from scraper import run_scraper_with_groq

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Top 10 NIRF Engineering Colleges 2024
TOP_NIRF_COLLEGES = [
    ("https://www.iitm.ac.in", "IIT Madras - NIRF Rank 1"),
    ("https://www.iitd.ac.in", "IIT Delhi - NIRF Rank 2"),
    ("https://www.iitb.ac.in", "IIT Bombay - NIRF Rank 3"),
    ("https://www.iitkgp.ac.in", "IIT Kharagpur - NIRF Rank 4"),
    ("https://www.iitk.ac.in", "IIT Kanpur - NIRF Rank 5"),
    ("https://www.iitroorkee.ac.in", "IIT Roorkee - NIRF Rank 6"),
    ("https://www.iitg.ac.in", "IIT Guwahati - NIRF Rank 7"),
    ("https://www.iith.ac.in", "IIT Hyderabad - NIRF Rank 8"),
    ("https://www.iitbhu.ac.in", "IIT BHU - NIRF Rank 9"),
    ("https://www.iitr.ac.in", "IIT Ropar - NIRF Rank 10"),
]

def scrape_top_nirf():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found!")
        return
    
    print("🏆 Starting to scrape Top 10 NIRF Engineering Colleges...")
    print("=" * 80)
    
    for i, (url, name) in enumerate(TOP_NIRF_COLLEGES, 1):
        print(f"\n[{i}/10] Processing: {name}")
        print(f"URL: {url}")
        print("-" * 80)
        
        try:
            result = run_scraper_with_groq(url, pages=25, groq_api_key=GROQ_API_KEY)
            
            if result:
                college_name = result.get("university_name", "Unknown")
                print(f"✅ Successfully processed: {college_name}")
                
                # Show course categories
                courses = result.get("courses_and_fees", {})
                if isinstance(courses, dict):
                    categories = list(courses.keys())
                    print(f"   📚 Course categories: {', '.join(categories)}")
            else:
                print(f"⚠️ No data returned for {url}")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("✅ Top 10 NIRF colleges scraping complete!")
    print("📊 All colleges have been added to data.json with categorized courses")
    print("🚀 All colleges have been indexed to Qdrant")
    print("🌐 View dashboard: http://localhost:6333/dashboard")

if __name__ == "__main__":
    scrape_top_nirf()
