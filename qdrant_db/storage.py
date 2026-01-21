from qdrant_client import QdrantClient
from qdrant_client.http import models
import hashlib
import json
from sentence_transformers import SentenceTransformer

class CollegeDB:
    def __init__(self):
        self.client = QdrantClient("localhost", port=6333)
        self._model = None # Lazy load
        self.collection_name = "colleges_master"
        self._ensure_collection()

    @property
    def model(self):
        if self._model is None:
            print("⏳ Loading AI Model (Lazy)...")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def _ensure_collection(self):
        """Ensure the master collection exists and has proper indexes."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            print(f"🔧 Creating master collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
        
        # Ensure Full Text Index on Name (Idempotent operation)
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="university_name",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                lowercase=True
            )
        )

    def search_college(self, college_name):
        """
        Check if college exists using Full Text Search first (Fast & Accurate).
        """
        # 1. Try Full Text Search (Fastest for names)
        # This handles 'IIT Bombay' matching 'Indian Institute of Technology Bombay'
        text_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="university_name",
                    match=models.MatchText(text=college_name)
                )
            ]
        )
        
        try:
            res = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=text_filter,
                limit=1,
                with_payload=True
            )[0]
            
            if res:
                print(f"✅ Found in Qdrant (Text Match): {res[0].payload['university_name']}")
                return res[0].payload
        except Exception as e:
            print(f"⚠️ Text search error: {e}")

        # 2. Fallback to Vector Search (Slower but catches semantic meanings)
        print("⚡ Text match failed, trying vector search...")
        # Only load model here!
        vector = self.model.encode(college_name).tolist()
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=1,
            with_payload=True,
            score_threshold=0.75
        ).points
        
        if results:
            print(f"✅ Found in Qdrant (Vector): {results[0].payload['university_name']}")
            return results[0].payload
            
        return None

    def save_college(self, college_data):
        """
        Save/Upsert college data.
        """
        name = college_data.get("university_name")
        if not name:
            return False
            
        print(f"💾 Saving to Qdrant: {name}")
        
        # Create a rich text representation for the vector
        # This helps in future semantic search
        courses_txt = str(college_data.get("courses", {}))
        text_for_vector = f"{name}. {college_data.get('location', '')}. {college_data.get('description', '')}. Courses: {courses_txt}"
        
        vector = self.model.encode(text_for_vector).tolist()
        
        # Deterministic ID based on name to prevent duplicates
        point_id = int(hashlib.md5(name.encode()).hexdigest(), 16) % (10**15)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=college_data
                )
            ]
        )
        return True
