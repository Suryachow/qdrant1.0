"""
Verify Qdrant Collections and Course Categorization
This script checks:
1. Which Qdrant collections exist
2. How many colleges are indexed in each collection
3. Sample data from courses_and_fees to verify categorization
"""

from qdrant_client import QdrantClient
import json

def verify_qdrant_collections():
    try:
        client = QdrantClient("localhost", port=6333)
        print("✅ Connected to Qdrant\n")
        
        # Get all collections
        collections = client.get_collections().collections
        print(f"📊 Found {len(collections)} collections:\n")
        
        for collection in collections:
            name = collection.name
            
            # Get collection info
            info = client.get_collection(collection_name=name)
            point_count = info.points_count
            
            print(f"  📁 {name}")
            print(f"     └─ Points: {point_count}")
            
            # If it's the courses collection, show sample data
            if name == "college_courses_and_fees" and point_count > 0:
                print(f"     └─ Checking categorization...")
                
                # Get a few sample points
                samples = client.scroll(
                    collection_name=name,
                    limit=3,
                    with_payload=True,
                    with_vectors=False
                )
                
                for point in samples[0]:
                    payload = point.payload
                    college_name = payload.get("university_name", "Unknown")
                    content = payload.get("content", {})
                    
                    print(f"\n     🎓 {college_name}")
                    
                    if isinstance(content, dict):
                        categories = list(content.keys())
                        print(f"        Categories: {', '.join(categories)}")
                        
                        # Show count of courses in each category
                        for cat, courses in content.items():
                            if isinstance(courses, list):
                                print(f"        └─ {cat}: {len(courses)} programs")
                    else:
                        print(f"        ⚠️ Content is not categorized (type: {type(content)})")
            
            print()
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        # Check if key collections exist
        expected_collections = [
            "college_overview",
            "college_rankings", 
            "college_courses_and_fees",
            "college_placements",
            "college_facilities"
        ]
        
        existing_names = [c.name for c in collections]
        
        for expected in expected_collections:
            if expected in existing_names:
                print(f"✅ {expected}")
            else:
                print(f"❌ {expected} - NOT FOUND")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        print("\nMake sure Qdrant is running:")
        print("  docker start qdrant")
        print("  OR")
        print("  ./qdrant")

def verify_data_json_categorization():
    """Check how many colleges in data.json have categorized courses"""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            colleges = json.load(f)
        
        print(f"\n📄 Checking data.json categorization...")
        print(f"Total colleges: {len(colleges)}\n")
        
        categorized = 0
        uncategorized = 0
        
        for college in colleges:
            name = college.get("university_name", "Unknown")
            courses = college.get("courses_and_fees")
            
            if isinstance(courses, dict) and any(k in courses for k in ["B.Tech", "M.Tech", "MBA", "Other Programs"]):
                categorized += 1
            else:
                uncategorized += 1
                print(f"  ⚠️ {name} - courses not categorized")
        
        print(f"\n✅ Categorized: {categorized}")
        print(f"❌ Not categorized: {uncategorized}")
        
        if uncategorized > 0:
            print("\n💡 Run 'python migrate_courses.py' to categorize remaining colleges")
        
    except FileNotFoundError:
        print("❌ data.json not found")
    except Exception as e:
        print(f"❌ Error reading data.json: {e}")

if __name__ == "__main__":
    print("="*60)
    print("QDRANT CATEGORIZATION VERIFICATION")
    print("="*60 + "\n")
    
    verify_qdrant_collections()
    verify_data_json_categorization()
    
    print("\n" + "="*60)
    print("✅ Verification complete!")
    print("="*60)
    print("\n💡 View Qdrant dashboard: http://localhost:6333/dashboard")
