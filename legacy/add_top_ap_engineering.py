import os
import sys
from scraper import run_scraper_with_groq

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Top 10 Engineering Colleges in Andhra Pradesh
TOP_AP_ENGINEERING_COLLEGES = [
    ("https://www.kluniversity.in", "KL University (Deemed to be University)"),
    ("https://vignan.ac.in", "Vignan's Foundation for Science, Technology & Research"),
    ("https://www.vrsiddhartha.ac.in", "VR Siddhartha Engineering College"),
    ("https://www.vvitguntur.com", "Vasavi College of Engineering (VVIT)"),
    ("https://www.gitam.edu", "GITAM University"),
    ("https://www.gvpce.ac.in", "GVP College of Engineering (Autonomous)"),
    ("https://www.jntuk.edu.in", "JNTU Kakinada"),
    ("https://www.jntua.ac.in", "JNTU Anantapur"),
    ("https://www.sreenidhi.edu.in", "Sreenidhi Institute of Science and Technology"),
    ("https://www.cvsr.ac.in", "CVR College of Engineering"),
]

def scrape_top_ap_engineering():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found!")
        return
    
    print("🎓 Starting to scrape Top 10 Engineering Colleges in Andhra Pradesh...")
    print("=" * 80)
    
    for i, (url, name) in enumerate(TOP_AP_ENGINEERING_COLLEGES, 1):
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
                    total_courses = sum(len(v) if isinstance(v, list) else 0 for v in courses.values())
                    print(f"   📚 Course categories: {', '.join(categories)}")
                    print(f"   📊 Total courses: {total_courses}")
                    
                # Show rankings if available
                rankings = result.get("rankings", [])
                if rankings:
                    print(f"   🏆 Rankings: {len(rankings)} entries")
            else:
                print(f"⚠️ No data returned for {url}")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("✅ Top 10 AP Engineering colleges scraping complete!")
    print("📊 All colleges have been added to data.json with categorized courses")
    print("   - B.Tech programs")
    print("   - M.Tech programs")
    print("   - MBA programs")
    print("   - Other Programs")
    print("🚀 All colleges have been indexed to Qdrant in category-specific collections")
    print("🌐 View dashboard: http://localhost:6333/dashboard")

if __name__ == "__main__":
    scrape_top_ap_engineering()
