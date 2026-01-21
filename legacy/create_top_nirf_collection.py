import json
import re
from qdrant_client import QdrantClient
from qdrant_client.http import models
import hashlib
from sentence_transformers import SentenceTransformer

# Initialize
client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_nirf_rank(college):
    """Try to extract integer rank from rankings list"""
    rankings = college.get("rankings", [])
    overview = college.get("overview", {}).get("description", "")
    
    # Check rankings list strings
    for r in rankings:
        if "NIRF" in r and "Engineering" in r:
            # Look for numbers
            nums = re.findall(r'\d+', r)
            if nums:
                return int(nums[0])
    
    # Fallback to overview text
    if "NIRF" in overview:
        # Heuristic search
        return 999 
        
    return 9999 # Not ranked/unknown

def create_top_nirf_collection():
    print("🏆 Creating Top NIRF Colleges Collection...")
    
    COLLECTION_NAME = "top_nirf_colleges"
    
    # 1. Load Data
    with open("data.json", "r", encoding="utf-8") as f:
        colleges = json.load(f)
        
    # 2. Sort by NIRF Rank (Manual ordered list of known top colleges if parsing is flaky)
    # Based on standard India rankings: IIT Madras, Delhi, Bombay, Kanpur, Kharagpur, Roorkee, Guwahati, etc.
    # Let's see what we have and try to match them to a known top list to be safe.
    
    known_top_colleges = [
        "Madras", "Delhi", "Bombay", "Kanpur", "Kharagpur", 
        "Roorkee", "Guwahati", "Hyderabad", "Tiruchirappalli", "Vellore" # VIT is high, NIT Trichy high
    ]
    
    selected_colleges = []
    
    # Heuristic matching 
    for college in colleges:
        name = college.get("university_name", "")
        for key in known_top_colleges:
            if key in name:
                selected_colleges.append(college)
                break
                
    # Limit to 10 if we have more, or just take what we found
    selected_colleges = selected_colleges[:10]
    
    print(f"Found {len(selected_colleges)} top colleges to index.")
    
    # 3. Re-create Collection
    try:
        client.delete_collection(COLLECTION_NAME)
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Collection '{COLLECTION_NAME}' created.")
    except Exception as e:
        print(f"⚠️ Error creating collection: {e}")

    # 4. Index Data
    for college in selected_colleges:
        name = college.get("university_name", "Unknown")
        print(f"   Indexing: {name}")
        
        # We index the 'Overview' as the main vector content for the top list
        overview_text = str(college.get("overview", ""))
        
        vector = model.encode(overview_text).tolist()
        point_id = int(hashlib.md5(name.encode()).hexdigest(), 16) % (10**15)
        
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=college # Store full college data in payload
                )
            ]
        )
    
    print("\n✅ Top 10 NIRF Collection Ready!")

if __name__ == "__main__":
    create_top_nirf_collection()
