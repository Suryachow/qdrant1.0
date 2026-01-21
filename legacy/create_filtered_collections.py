import json
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# Initialize
client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- MAPPINGS ---

STREAMS = {
    "Engineering": ["B.Tech", "M.Tech", "B.E", "M.E", "B.Arch", "M.Arch", "Polytechnic"],
    "Management": ["MBA", "BBA", "PGDM", "BMS", "MMS"],
    "Medical": ["MBBS", "BDS", "MD", "MS", "B.Pharma", "M.Pharma", "BPT", "MPT"],
    "Science": ["B.Sc", "M.Sc", "BCA", "MCA"], # BCA/MCA often grouped with Science or Eng, putting here or sep? Let's keep Science for now or "Computer Applications"
    "Commerce": ["B.Com", "M.Com"],
    "Arts": ["B.A", "M.A", "B.Ed", "M.Ed", "LLB", "LLM", "B.Des", "M.Des"],
    "Ph.D": ["Ph.D"] # Ph.D is often treated as a level, but sometimes a separate stream bucket in UI
}

# Explicit Level Mapping
LEVELS = {
    "Undergraduate": ["B.Tech", "B.E", "B.Arch", "BBA", "BMS", "MBBS", "BDS", "B.Pharma", "BPT", "B.Sc", "BCA", "B.Com", "B.A", "B.Ed", "LLB", "B.Des"],
    "Postgraduate": ["M.Tech", "M.E", "M.Arch", "MBA", "PGDM", "MMS", "MD", "MS", "M.Pharma", "MPT", "M.Sc", "MCA", "M.Com", "M.A", "M.Ed", "LLM", "M.Des"],
    "Diploma": ["Polytechnic", "Diploma"],
    "Ph.D": ["Ph.D"]
}

# Default Study Mode (since data might not have it, we default to Full Time)
DEFAULT_MODE = "Full Time"

def determine_metadata(course_name_key):
    """
    Determine Stream and Level based on the course key (e.g., 'B.Tech', 'MBA').
    Returns (Stream, Level)
    """
    # Normalize
    key_norm = course_name_key.strip()
    
    # Find Stream
    assigned_stream = "Other"
    for stream, keywords in STREAMS.items():
        if any(k.lower() == key_norm.lower() or k.lower() in key_norm.lower() for k in keywords):
            assigned_stream = stream
            break
            
    # Find Level
    assigned_level = "Other"
    for level, keywords in LEVELS.items():
        if any(k.lower() == key_norm.lower() or k.lower() in key_norm.lower() for k in keywords):
            assigned_level = level
            break
            
    # Fallbacks/Heuristics
    if assigned_level == "Other":
        if key_norm.startswith("B."): assigned_level = "Undergraduate"
        elif key_norm.startswith("M."): assigned_level = "Postgraduate"
        elif "Diploma" in key_norm: assigned_level = "Diploma"
        elif "Ph.D" in key_norm: assigned_level = "Ph.D"

    return assigned_stream, assigned_level

def init_stream_collections():
    """Create collections for each stream"""
    print("🔧 Creating stream-based collections...")
    
    # We create a collection for each distinct Stream defined in STREAMS + 'Other'
    target_streams = list(STREAMS.keys()) + ["Other"]
    
    for stream in target_streams:
        # Collection name format: stream_engineering, stream_management
        safe_name = stream.lower().replace(" & ", "_").replace(" ", "_").replace(".", "")
        collection_name = f"stream_{safe_name}"
        
        try:
            client.delete_collection(collection_name) # Reset for clean state
            
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
            
            # Create Payload Indexes for filtering
            # We want to filter by: course_level, study_mode, state/city (location)
            client.create_payload_index(
                collection_name=collection_name,
                field_name="course_level",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            client.create_payload_index(
                collection_name=collection_name,
                field_name="study_mode",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            client.create_payload_index(
                collection_name=collection_name,
                field_name="state",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            
            print(f"   ✅ Created: {collection_name} (with filters)")
            
        except Exception as e:
            print(f"   ❌ Error {collection_name}: {e}")

def index_data():
    print("\n🚀 Indexing data with filters...")
    
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            colleges = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found.")
        return

    count = 0
    for college in colleges:
        name = college.get("university_name", "Unknown")
        url = college.get("college_url", "Unknown")
        location = college.get("overview", {}).get("location", "Unknown")
        state = location.split(",")[-2].strip() if "," in location else location # Rough state extraction
        
        courses_data = college.get("courses_and_fees", {})
        
        # We assume courses_and_fees keys are the course types 'B.Tech', 'MBA', etc.
        # But sometimes they are nested under 'Other Programs'.
        # We need to flatten the structure slightly for processing.
        
        # 1. Top level keys
        toplevel_keys = list(courses_data.keys())
        
        all_course_items = []
        
        for key in toplevel_keys:
            val = courses_data[key]
            
            if key == "Other Programs" and isinstance(val, list):
                 # Iterate through the list of dicts in 'Other Programs'
                 for item in val:
                     c_name = item.get("course_name", "Unknown")
                     # Try to deduce type from name
                     s_type, s_level = determine_metadata(c_name.split()[0]) # simplistic
                     # Actually, usually better to pass the whole name or the key if it was distinct
                     # In data.json, "Other Programs" is a list.
                     # "course_name": "B.Arch ..."
                     
                     # Refined meta extraction for list items
                     meta_name = c_name
                     if "Ph.D" in c_name: meta_name = "Ph.D"
                     elif "B.Sc" in c_name: meta_name = "B.Sc"
                     elif "M.Sc" in c_name: meta_name = "M.Sc"
                     
                     all_course_items.append({
                         "raw_key": meta_name,
                         "details": item,
                         "is_from_other": True
                     })
            elif isinstance(val, list):
                # e.g. "B.Tech": [ ... ]
                for item in val:
                    all_course_items.append({
                        "raw_key": key,
                        "details": item,
                        "is_from_other": False
                    })
        
        # Now index each item
        for item in all_course_items:
            raw_key = item["raw_key"]
            details = item["details"]
            
            stream, level = determine_metadata(raw_key)
            
            # Text for embedding
            course_name = details.get("course_name", raw_key)
            fee = details.get("total_tuition_fee", "")
            eligibility = details.get("eligibility", "")
            
            text_chunk = f"{name} - {course_name}. Fee: {fee}. Eligibility: {eligibility}. Location: {location}"
            
            # Vector
            vector = model.encode(text_chunk).tolist()
            
            # Target Collection
            safe_stream_name = stream.lower().replace(" & ", "_").replace(" ", "_").replace(".", "")
            collection_name = f"stream_{safe_stream_name}"
            
            # Unique ID
            payload_str = f"{name}_{course_name}_{stream}_{level}"
            point_id = int(hashlib.md5(payload_str.encode()).hexdigest(), 16) % (10**15)
            
            try:
                client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=point_id,
                            vector=vector,
                            payload={
                                "university_name": name,
                                "course_name": course_name,
                                "stream": stream,            # For filtering
                                "course_level": level,       # For filtering
                                "study_mode": DEFAULT_MODE,  # For filtering
                                "state": state,              # For filtering
                                "fee": fee,
                                "eligibility": eligibility,
                                "college_url": url,
                                "full_details": details
                            }
                        )
                    ]
                )
                        
            except Exception as e:
                # pass if collection doesn't exist or other error (some streams might calculate to 'other' index, ensure 'stream_other' exists)
                pass
                
    print("✅ Indexing Complete.")

if __name__ == "__main__":
    init_stream_collections()
    index_data()
