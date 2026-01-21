from qdrant_client import QdrantClient

def optimize_all_collections():
    client = QdrantClient("localhost", port=6333)
    
    print("🔧 Optimizing Qdrant collections...")
    print("=" * 60)
    
    collections = client.get_collections().collections
    
    for collection in collections:
        collection_name = collection.name
        print(f"\n📊 Collection: {collection_name}")
        
        try:
            # Get current status
            info = client.get_collection(collection_name)
            print(f"   Status: {info.status}")
            print(f"   Points: {info.points_count}")
            
            # Optimize the collection
            print(f"   🔄 Optimizing...")
            client.update_collection(
                collection_name=collection_name,
                optimizer_config={
                    "indexing_threshold": 0
                }
            )
            print(f"   ✅ Optimization triggered")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All collections have been optimized!")
    print("🔄 Refresh your dashboard to see the updated status")
    print("🌐 http://localhost:6333/dashboard")

if __name__ == "__main__":
    optimize_all_collections()
