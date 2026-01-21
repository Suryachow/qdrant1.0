from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import json
import hashlib

# Initialize
client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Course types to create collections for
COURSE_TYPES = ["B.Tech", "M.Tech", "MBA", "Other Programs"]

def init_course_collections():
    """Create Qdrant collections for each course type"""
    print("🔧 Creating course-specific collections...")
    print("=" * 60)
    
    for course_type in COURSE_TYPES:
        collection_name = f"colleges_{course_type.lower().replace('.', '').replace(' ', '_')}"
        
        try:
            # Check if collection exists
            collections = client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if exists:
                print(f"✅ Collection '{collection_name}' already exists")
            else:
                print(f"📡 Creating collection: {collection_name}")
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=384,
                        distance=models.Distance.COSINE
                    ),
                    optimizers_config=models.OptimizersConfigDiff(
                        indexing_threshold=20000
                    )
                )
                print(f"✅ Created: {collection_name}")
        except Exception as e:
            print(f"❌ Error creating {collection_name}: {e}")
    
    print("=" * 60)

def index_colleges_by_course():
    """Index colleges into course-specific collections"""
    print("\n🚀 Indexing colleges by course offerings...")
    print("=" * 60)
    
    # Load colleges
    with open("data.json", "r", encoding="utf-8") as f:
        colleges = json.load(f)
    
    stats = {course: 0 for course in COURSE_TYPES}
    
    for i, college in enumerate(colleges, 1):
        name = college.get("university_name", "Unknown")
        url = college.get("college_url", "Unknown")
        courses_and_fees = college.get("courses_and_fees", {})
        
        print(f"\n[{i}/{len(colleges)}] Processing: {name}")
        
        # For each course type the college offers
        for course_type in COURSE_TYPES:
            if course_type not in courses_and_fees:
                continue
            
            course_data = courses_and_fees[course_type]
            if not course_data:
                continue
            
            collection_name = f"colleges_{course_type.lower().replace('.', '').replace(' ', '_')}"
            
            try:
                # Create rich text for embedding
                # Include college name, overview, and course details
                overview_text = ""
                if "overview" in college and isinstance(college["overview"], dict):
                    overview_text = college["overview"].get("description", "")[:500]
                
                # Format course data
                if isinstance(course_data, list):
                    course_text = ". ".join([
                        ", ".join([f"{k}: {v}" for k, v in item.items()])
                        for item in course_data if isinstance(item, dict)
                    ])
                else:
                    course_text = str(course_data)[:500]
                
                # Combine for rich context
                rich_text = f"{name}. {overview_text}. {course_type} Programs: {course_text}"
                
                # Generate embedding
                vector = model.encode(rich_text).tolist()
                
                # Create unique ID
                point_id = int(hashlib.md5(f"{name}_{course_type}".encode()).hexdigest(), 16) % (10**15)
                
                # Upsert to collection
                client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=point_id,
                            vector=vector,
                            payload={
                                "university_name": name,
                                "college_url": url,
                                "course_type": course_type,
                                "courses": course_data,
                                "overview": college.get("overview", {}),
                                "rankings": college.get("rankings", []),
                                "placements": college.get("placements", {}),
                                "facilities": college.get("facilities", []),
                                "contact_info": college.get("contact_info", {})
                            }
                        )
                    ]
                )
                
                stats[course_type] += 1
                print(f"  ✅ Indexed to {collection_name}")
                
            except Exception as e:
                print(f"  ❌ Error indexing {course_type}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Indexing Statistics:")
    for course_type, count in stats.items():
        collection_name = f"colleges_{course_type.lower().replace('.', '').replace(' ', '_')}"
        print(f"  {collection_name}: {count} colleges")
    print("=" * 60)

def verify_collections():
    """Verify all collections and show counts"""
    print("\n🔍 Verifying collections...")
    print("=" * 60)
    
    collections = client.get_collections().collections
    
    for course_type in COURSE_TYPES:
        collection_name = f"colleges_{course_type.lower().replace('.', '').replace(' ', '_')}"
        
        try:
            collection_info = client.get_collection(collection_name)
            count = collection_info.points_count
            print(f"✅ {collection_name}: {count} points")
        except Exception as e:
            print(f"❌ {collection_name}: {e}")
    
    print("=" * 60)
    print("\n🌐 View dashboard: http://localhost:6333/dashboard")

if __name__ == "__main__":
    print("🎓 Creating Course-Specific Collections for Qdrant")
    print("=" * 60)
    
    # Step 1: Create collections
    init_course_collections()
    
    # Step 2: Index colleges
    index_colleges_by_course()
    
    # Step 3: Verify
    verify_collections()
    
    print("\n✅ All done!")
