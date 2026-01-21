from qdrant_client import QdrantClient
from qdrant_client.http import models

def fix_red_collections():
    client = QdrantClient("localhost", port=6333)
    
    print("🔧 Fixing RED collections...")
    print("=" * 60)
    
    # Collections that are RED
    red_collections = ["college_facilities", "college_placements", "college_overview"]
    
    for collection_name in red_collections:
        print(f"\n📊 Fixing: {collection_name}")
        
        try:
            # Delete the collection
            print(f"   🗑️ Deleting old collection...")
            client.delete_collection(collection_name)
            print(f"   ✅ Deleted")
            
            # Recreate with proper config
            print(f"   🔨 Creating new collection...")
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
            print(f"   ✅ Created successfully")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Collections recreated!")
    print("Now re-indexing data...")
    
    # Re-index all colleges
    import json
    with open("data.json", "r", encoding="utf-8") as f:
        colleges = json.load(f)
    
    from scraper import index_to_qdrant
    
    print(f"\n🚀 Re-indexing {len(colleges)} colleges...")
    for i, college in enumerate(colleges, 1):
        name = college.get("university_name", "Unknown")
        print(f"[{i}/{len(colleges)}] Indexing {name}...")
        try:
            index_to_qdrant(college)
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All done! Check your dashboard:")
    print("🌐 http://localhost:6333/dashboard")

if __name__ == "__main__":
    fix_red_collections()
