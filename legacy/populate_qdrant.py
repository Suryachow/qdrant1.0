import json
import os
from scraper import index_to_qdrant

DATA_FILE = "data.json"

def populate_all():
    if not os.path.exists(DATA_FILE):
        print(f"❌ {DATA_FILE} not found!")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        colleges = json.load(f)

    print(f"📊 Found {len(colleges)} colleges in {DATA_FILE}. Starting migration...")

    for i, college in enumerate(colleges):
        name = college.get("university_name", "Unknown")
        print(f"\n[{i+1}/{len(colleges)}] Processing {name}...")
        try:
            index_to_qdrant(college)
        except Exception as e:
            print(f"❌ Error indexing {name}: {e}")

    print("\n✅ Migration complete! Your Qdrant server is now populated with categorized data.")

if __name__ == "__main__":
    populate_all()
