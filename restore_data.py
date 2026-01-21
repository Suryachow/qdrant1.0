import json
import os
import sys
from qdrant_db.storage import CollegeDB

def restore():
    print("🔄 Checking for local data backup (data.json)...")
    
    if not os.path.exists("data.json"):
        print("⚠️ No data.json found. Starting with empty database.")
        return

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"📦 Found {len(data)} colleges in backup. Restoring to Qdrant...")
        
        db = CollegeDB()
        count = 0
        for college in data:
            if db.save_college(college):
                count += 1
                if count % 10 == 0:
                    print(f"   Indexed {count}...")
                    
        print(f"✅ Successfully restored {count} colleges to Qdrant!")
        
    except Exception as e:
        print(f"❌ Restoration failed: {e}")

if __name__ == "__main__":
    restore()
