import os
import sys
from scraper import run_scraper_with_groq

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Use environment variable!
if not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY not found in environment.")

# List of prominent colleges in Andhra Pradesh
AP_COLLEGES = [
    "https://www.jntua.ac.in",  # JNTU Anantapur
    "https://www.jntuk.edu.in",  # JNTU Kakinada
    "https://www.kluniversity.in",  # KL University
    "https://www.gitam.edu",  # GITAM University
    "https://www.andhrauniversity.edu.in",  # Andhra University
    "https://www.svuniversity.edu.in",  # Sri Venkateswara University
    "https://www.svu.edu.in",  # SV University Tirupati
    "https://www.vrsiddhartha.ac.in",  # VR Siddhartha Engineering College
    "https://www.gvpce.ac.in",  # GVP College of Engineering
    "https://www.raghuenggcollege.com",  # Raghu Engineering College
]

def scrape_ap_colleges():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found!")
        print("Make sure your .env file or environment variables are set.")
        return
    
    print(f"🎓 Starting to scrape {len(AP_COLLEGES)} Andhra Pradesh colleges...")
    print("=" * 70)
    
    for i, url in enumerate(AP_COLLEGES, 1):
        print(f"\n[{i}/{len(AP_COLLEGES)}] Processing: {url}")
        print("-" * 70)
        
        try:
            result = run_scraper_with_groq(url, pages=20, groq_api_key=GROQ_API_KEY)
            
            if result:
                college_name = result.get("university_name", "Unknown")
                print(f"✅ Successfully processed: {college_name}")
            else:
                print(f"⚠️ No data returned for {url}")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
            continue
    
    print("\n" + "=" * 70)
    print("✅ Scraping complete! All colleges have been added to data.json and Qdrant.")
    print("🌐 Open Qdrant dashboard to view: http://localhost:6333/dashboard")

if __name__ == "__main__":
    scrape_ap_colleges()
