import json
from qdrant_client import QdrantClient

def backup_qdrant_to_json():
    print("💾 Backing up Qdrant data to data.json...")
    
    client = QdrantClient("localhost", port=6333)
    collection_name = "colleges_master"
    
    try:
        # Fetch all points (using scroll)
        all_colleges = []
        offset = None
        
        while True:
            points, offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                with_payload=True,
                offset=offset
            )
            
            for p in points:
                if p.payload:
                    all_colleges.append(p.payload)
            
            if offset is None:
                break
                
        print(f"📦 Extracted {len(all_colleges)} colleges from Qdrant.")
        
        # Save to file
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(all_colleges, f, indent=2, ensure_ascii=False)
            
        print("✅ Successfully updated data.json! Now you can push to GitHub.")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    backup_qdrant_to_json()
