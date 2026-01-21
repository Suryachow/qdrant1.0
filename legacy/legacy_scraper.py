# scraper.py
import json
import os
import re
import time
import requests
import numpy as np
from groq import Groq
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from html import unescape
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# ================= CONFIG =================
BASE_URL = "https://vignan.ac.in/newvignan/"
MAX_PAGES = 50
MIN_SENTENCE_LEN = 30
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
DATA_FILE = "data.json"
COLLECTION_NAME = "universities"
INDEX_CATEGORIES = ["overview", "rankings", "courses_and_fees", "placements", "facilities", "scholarships"]

FIELDS = {
    "University Overview": ["about", "overview", "history", "vision", "mission", "founded", "established", "since", "accreditation", "naac", "nirf", "ranking", "institute", "university", "college"],
    "Courses Offered": ["b.tech", "m.tech", "mba", "bba", "program", "department", "branch", "specialization", "undergraduate", "postgraduate", "diploma", "course", "engineering", "degree"],
    "Admissions": ["admission", "apply", "entrance", "application", "selection", "counseling", "eligibility", "cutoff", "jee", "gate"],
    "Eligibility": ["eligibility", "qualification", "required", "minimum", "marks", "entrance exam", "cutoff score"],
    "Fees": ["fee structure", "tuition", "fees", "annual", "semester", "cost", "payment", "refund"],
    "Scholarships": ["scholarship", "financial aid", "assistance", "fee waiver", "merit", "grant"],
    "Placements": ["placement", "package", "salary", "company", "recruit", "career", "opportunity", "intern"],
    "Faculty": ["faculty", "professor", "instructor", "teacher", "phd", "expert", "experienced", "qualified"],
    "Facilities": ["hostel", "library", "laboratory", "lab", "sports", "cafeteria", "medical", "transport", "infrastructure", "amenities"],
    "Campus Life": ["club", "event", "activity", "fest", "cultural", "sports", "student life", "community"],
    "Contact": ["contact", "phone", "email", "address", "location", "reach us"],
    "Research": ["research", "paper", "publication", "project", "innovation", "development"],
}

session = requests.Session()
session.headers.update(HEADERS)

# Initialize models lazily
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        print("🔧 Loading embedding model (all-MiniLM-L6-v2)...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model

# =============== QDRANT HELPERS =============
def get_qdrant_client():
    try:
        return QdrantClient("localhost", port=6333)
    except Exception as e:
        print(f"⚠️ Qdrant connection error: {e}")
        return None

def init_qdrant_collection(collection_name):
    client = get_qdrant_client()
    if not client: return False
    
    try:
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            print(f"📡 Creating Qdrant collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
        return True
    except Exception as e:
        print(f"❌ Qdrant init error for {collection_name}: {e}")
        return False

def index_to_qdrant(college_data):
    client = get_qdrant_client()
    if not client: return
    
    name = college_data.get("university_name", "Unknown")
    url = college_data.get("college_url", "Unknown")
    model = get_embedding_model()
    import hashlib

    print(f"🚀 Indexing {name} to category-specific collections...")

    for category in INDEX_CATEGORIES:
        data = college_data.get(category)
        if not data: continue

        # Format text based on data type
        if isinstance(data, dict):
            # Special handling for categorized list of dicts (like courses_and_fees)
            formatted_parts = []
            for subcat, items in data.items():
                if isinstance(items, list) and all(isinstance(i, dict) for i in items):
                    subcat_text = f"[{subcat}]: " + ". ".join([", ".join([f"{k}: {v}" for k, v in item.items()]) for item in items])
                    formatted_parts.append(subcat_text)
                else:
                    formatted_parts.append(f"{subcat}: {items}")
            text_to_embed = ". ".join(formatted_parts)
        elif isinstance(data, list):
            if all(isinstance(i, dict) for i in data):
                # Handle list of dicts (like courses)
                text_to_embed = ". ".join([", ".join([f"{k}: {v}" for k, v in item.items()]) for item in data])
            else:
                text_to_embed = ". ".join([str(i) for i in data])
        else:
            text_to_embed = str(data)

        if len(text_to_embed) < 10: continue

        # Add university name for context in the vector
        rich_text = f"{name} ({category}): {text_to_embed}"
        
        try:
            collection_name = f"college_{category}"
            if not init_qdrant_collection(collection_name): continue

            vector = model.encode(rich_text).tolist()
            
            # ID: hash(name + category)
            point_id = int(hashlib.md5(f"{name}_{category}".encode()).hexdigest(), 16) % (10**15)
            
            client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "university_name": name,
                            "college_url": url,
                            "category": category,
                            "content": data
                        }
                    )
                ]
            )
        except Exception as e:
            print(f"❌ Error indexing {category}: {e}")

# =============== DATA OPS ====================
def lookup_college(query):
    """Search for existing college in data.json by URL or name"""
    if not os.path.exists(DATA_FILE):
        return None
        
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            colleges = json.load(f)
            
        query_clean = query.lower().replace("https://", "").replace("http://", "").strip("/").replace("www.", "")
        
        for college in colleges:
            # Check top-level URL
            url = str(college.get("college_url", "")).lower().replace("https://", "").replace("http://", "").strip("/").replace("www.", "")
            if url and (query_clean in url or url in query_clean):
                return college
            
            # Check contact_info website
            contact_url = str(college.get("contact_info", {}).get("website", "")).lower().replace("https://", "").replace("http://", "").strip("/").replace("www.", "")
            if contact_url and (query_clean in contact_url or contact_url in query_clean):
                return college
            
            # Check Name
            name = str(college.get("university_name", "")).lower()
            if query.lower() in name or name in query.lower():
                return college
                
    except Exception as e:
        print(f"⚠️ Lookup error: {e}")
        
    return None

def save_to_data_json(new_college):
    """Save/Update college in data.json"""
    colleges = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                colleges = json.load(f)
        except:
            colleges = []

    name = new_college.get("university_name")
    url = new_college.get("college_url")
    
    # Ensure college_url is at top level
    if not url and new_college.get("contact_info", {}).get("website"):
        url = new_college["contact_info"]["website"]
        new_college["college_url"] = url

    updated = False
    for i, college in enumerate(colleges):
        # Match by URL or Name
        existing_url = college.get("college_url") or college.get("contact_info", {}).get("website")
        if (url and existing_url == url) or (name and college.get("university_name") == name):
            colleges[i] = new_college
            updated = True
            break
            
    if not updated:
        colleges.append(new_college)
        
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(colleges, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved/Updated {name} in {DATA_FILE}")
    
    # Also index to Qdrant (category-specific)
    index_to_qdrant(new_college)

# =============== UTILS ====================
def clean_text(text):
    text = unescape(text)
    text = "".join(char for char in text if char.isprintable() or char in "\n\r\t")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    clean_sentences = []
    for s in sentences:
        s = clean_text(s)
        if len(s) < MIN_SENTENCE_LEN or len(s.split()) < 5:
            continue
        clean_sentences.append(s)
    return clean_sentences

# =============== CRAWLER ==================
def crawl_site(url, max_pages):
    visited, queue = set(), [url]
    pages = []
    SKIP_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz')

    while queue and len(visited) < max_pages:
        current = queue.pop(0)
        if current in visited: continue
        if any(current.lower().endswith(ext) for ext in SKIP_EXTENSIONS): continue

        try:
            print(f"📄 Crawling: {current[:70]}...")
            res = session.get(current, timeout=10)
            content_type = res.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                visited.add(current)
                continue
            
            if res.status_code != 200: continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            pages.append(soup)
            visited.add(current)

            for a in soup.find_all("a", href=True):
                link = urljoin(current, a["href"])
                if urlparse(link).netloc == urlparse(url).netloc:
                    if link not in visited:
                        queue.append(link)
            time.sleep(0.05)
        except Exception as e:
            print(f"⚠️ Error {current[:30]}: {e}")

    return pages

def extract_data(pages):
    content = defaultdict(list)
    for soup in pages:
        text = clean_text(soup.get_text())
        sentences = split_sentences(text)
        for sent in sentences:
            sent_lower = sent.lower()
            for field, keys in FIELDS.items():
                if any(k in sent_lower for k in keys):
                    content[field].append(sent)
                    break
    
    final_content = {}
    for field, sents in content.items():
        unique_sents = list(set(sents))
        if unique_sents:
            final_content[field] = sorted(unique_sents, key=len, reverse=True)[:15]
            
    if not final_content:
        for soup in pages[:5]:
            text = clean_text(soup.get_text())
            sentences = split_sentences(text)
            if sentences:
                final_content["General Content"] = sentences[:20]
                break
    return final_content

# =============== GROQ AI SYNTHESIS ============
def synthesize_university_data(all_data, url, api_key):
    try:
        client = Groq(api_key=api_key)
        full_context = ""
        for field, sentences in all_data.items():
            full_context += f"--- {field} ---\n" + "\n".join(sentences) + "\n\n"
        
        full_context = full_context[:15000]
        
        schema = {
            "university_name": "Name",
            "overview": {"established_year": "YYYY", "location": "City", "type": "Public/Private", "campus_size": "Size", "description": "200-word prose"},
            "rankings": ["Rank 1"],
            "courses_and_fees": {
                "B.Tech": [{"course_name": "Name", "duration": "Years", "total_tuition_fee": "Fee", "eligibility": "Criteria"}],
                "M.Tech": [{"course_name": "Name", "duration": "Years", "total_tuition_fee": "Fee", "eligibility": "Criteria"}],
                "MBA": [{"course_name": "Name", "duration": "Years", "total_tuition_fee": "Fee", "eligibility": "Criteria"}],
                "Other Programs": [{"course_name": "Name", "duration": "Years", "total_tuition_fee": "Fee", "eligibility": "Criteria"}]
            },
            "placements": {"description": "Summary", "highest_package": "Value", "average_package": "Value", "major_recruiters": ["Co 1"]},
            "facilities": ["Facility 1"],
            "contact_info": {"website": url, "address": "Address"}
        }

        print("🧠 Synthesizing structured profile...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=3000,
            temperature=0.1,
            messages=[{
                "role": "user",
                "content": f"Create a professional university profile JSON for {url} based on this text:\n\n{full_context}\n\nSTRICT SCHEMA:\n{json.dumps(schema, indent=2)}\n\nIMPORTANT: Group all programs into their respective categories (B.Tech, M.Tech, MBA, Ph.D, etc.) under 'courses_and_fees'. Return raw JSON only."
            }]
        )
        
        resp = completion.choices[0].message.content.strip()
        start, end = resp.find('{'), resp.rfind('}') + 1
        data = json.loads(resp[start:end])
        data["college_url"] = url # Ensure URL is saved
        return data
    except Exception as e:
        print(f"❌ Synthesis error: {e}")
        return all_data

def run_scraper_with_groq(url=BASE_URL, pages=MAX_PAGES, groq_api_key=None):
    if url and not url.startswith("http"): url = "https://" + url
    
    # 1. Check if exists in data.json
    existing = lookup_college(url)
    if existing:
        print(f"✔️ {url} found in local database. Returning cached data.")
        # Ensure it's in Qdrant too (proactive)
        index_to_qdrant(existing)
        return existing
    
    # 2. Scrape and synthesize
    pages_data = crawl_site(url, pages)
    raw_data = extract_data(pages_data)
    
    if groq_api_key:
        final_data = synthesize_university_data(raw_data, url, groq_api_key)
        save_to_data_json(final_data)
        return final_data
    
    # If no Groq, just return raw (but we usually want Groq)
    return raw_data

def run_scraper(url=BASE_URL, pages=MAX_PAGES):
    # Basic scraper doesn't do synthesis or Qdrant for now to keep it simple,
    # but we can redirect to enhanced if GROW_API_KEY is present if needed.
    if url and not url.startswith("http"): url = "https://" + url
    pages_data = crawl_site(url, pages)
    data = extract_data(pages_data)
    return data

if __name__ == '__main__':
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://vignan.ac.in/newvignan/'
    # Check for Groq API Key
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        run_scraper_with_groq(url, groq_api_key=api_key)
    else:
        run_scraper(url)
