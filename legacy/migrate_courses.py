import json
import os
from scraper import index_to_qdrant

DATA_FILE = "data.json"

def categorize_courses(courses_list):
    """Categorize courses into B.Tech, M.Tech, MBA, and Other Programs"""
    if not isinstance(courses_list, list):
        return courses_list  # Already categorized or invalid format
    
    categorized = {
        "B.Tech": [],
        "M.Tech": [],
        "MBA": [],
        "Other Programs": []
    }
    
    for course in courses_list:
        if not isinstance(course, dict):
            continue
            
        course_name = course.get("course_name", "").lower()
        
        if "b.tech" in course_name or "bachelor" in course_name and "tech" in course_name:
            categorized["B.Tech"].append(course)
        elif "m.tech" in course_name or "master" in course_name and "tech" in course_name:
            categorized["M.Tech"].append(course)
        elif "mba" in course_name or "master" in course_name and "business" in course_name:
            categorized["MBA"].append(course)
        else:
            categorized["Other Programs"].append(course)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}

def migrate_all_colleges():
    if not os.path.exists(DATA_FILE):
        print(f"❌ {DATA_FILE} not found!")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        colleges = json.load(f)

    print(f"📊 Found {len(colleges)} colleges. Starting categorization migration...")

    updated_count = 0
    for i, college in enumerate(colleges):
        name = college.get("university_name", "Unknown")
        print(f"\n[{i+1}/{len(colleges)}] Processing {name}...")
        
        # Check if courses_and_fees needs migration
        courses = college.get("courses_and_fees")
        if isinstance(courses, list):
            print(f"  ↳ Categorizing {len(courses)} courses...")
            college["courses_and_fees"] = categorize_courses(courses)
            updated_count += 1
        else:
            print(f"  ↳ Already categorized or no courses found")

    # Save updated data
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(colleges, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Migration complete! Updated {updated_count} colleges.")
    print(f"📁 All data saved to {DATA_FILE}")
    
    # Now re-index to Qdrant
    print(f"\n🚀 Re-indexing all colleges to Qdrant with categorized structure...")
    for i, college in enumerate(colleges):
        name = college.get("university_name", "Unknown")
        print(f"[{i+1}/{len(colleges)}] Indexing {name}...")
        try:
            index_to_qdrant(college)
        except Exception as e:
            print(f"❌ Error indexing {name}: {e}")
    
    print("\n✅ All colleges have been categorized and indexed to Qdrant!")

if __name__ == "__main__":
    migrate_all_colleges()
