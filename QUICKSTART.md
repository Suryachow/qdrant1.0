# Quick Start Guide - Qdrant College Categorization

## Step 1: Start Qdrant

First, make sure Qdrant is running:

```bash
# Option 1: Using the batch file
.\start_qdrant.bat

# Option 2: If container already exists, just start it
docker start local_qdrant

# Option 3: Check if it's already running
docker ps
```

Verify Qdrant is running by visiting: http://localhost:6333/dashboard

## Step 2: Index All Colleges with Categorized Courses

Run the population script to index all 38 colleges:

```bash
python populate_qdrant.py
```

This will:
- ✅ Load all colleges from `data.json`
- ✅ Create category-specific collections (college_overview, college_courses_and_fees, etc.)
- ✅ Index each college with **categorized courses** (B.Tech, M.Tech, MBA, Other Programs)
- ✅ Generate vector embeddings for semantic search

## Step 3: Verify Categorization

Check that everything is indexed correctly:

```bash
python verify_categorization.py
```

This will show:
- ✅ All Qdrant collections and their point counts
- ✅ Sample categorized course data
- ✅ Which colleges have categorized vs uncategorized courses

## Step 4: Access Qdrant Dashboard

Open your browser and go to:
```
http://localhost:6333/dashboard
```

You can:
- View all collections
- See indexed points
- Run test queries
- Inspect the categorized structure

## Collections Created

Your data will be organized into these collections:

1. **college_overview** - University details, location, establishment year
2. **college_rankings** - NIRF, QS, THE rankings
3. **college_courses_and_fees** - ⭐ **Categorized courses** (B.Tech, M.Tech, MBA, etc.)
4. **college_placements** - Placement stats, packages, recruiters
5. **college_facilities** - Campus facilities and infrastructure
6. **college_scholarships** - Scholarship information

## Course Categories

Each college's courses are organized as:

```
B.Tech
├── B.Tech in Computer Science and Engineering
├── B.Tech in Electrical Engineering
├── B.Tech in Mechanical Engineering
└── ...

M.Tech
├── M.Tech in Computer Science
├── M.Tech in VLSI Design
└── ...

MBA
└── MBA (Master of Business Administration)

Other Programs
├── M.Sc in Physics
├── Ph.D. Programs
└── ...
```

## Troubleshooting

### Qdrant not running?
```bash
docker start local_qdrant
# OR
.\start_qdrant.bat
```

### Need to re-index?
```bash
# Re-index all colleges
python populate_qdrant.py

# OR migrate and re-index
python migrate_courses.py
```

### Check Docker status
```bash
docker ps                    # See running containers
docker ps -a                 # See all containers
docker logs local_qdrant     # View Qdrant logs
```

## What's Next?

After indexing, you can:

1. **Query by course type**: Search for "B.Tech Computer Science" and get relevant colleges
2. **Filter by category**: Get only M.Tech programs or MBA programs
3. **Semantic search**: Search "AI and Machine Learning courses" to find related programs
4. **Build applications**: Use the categorized data in your web app or API

## Example Query (Python)

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Search for B.Tech courses
query = "B.Tech Computer Science Engineering"
vector = model.encode(query).tolist()

results = client.search(
    collection_name="college_courses_and_fees",
    query_vector=vector,
    limit=5
)

for result in results:
    college = result.payload["university_name"]
    courses = result.payload["content"]
    
    # Access categorized courses
    if "B.Tech" in courses:
        print(f"\n{college}:")
        for course in courses["B.Tech"]:
            print(f"  - {course['course_name']}")
```

## Files Reference

- `data.json` - Source data with categorized courses
- `populate_qdrant.py` - Index all colleges to Qdrant
- `migrate_courses.py` - Migrate old format to categorized format
- `verify_categorization.py` - Verify indexing and categorization
- `scraper.py` - Core indexing logic
- `README_CATEGORIZATION.md` - Detailed documentation

---

**Ready to start?** Run these commands:

```bash
# 1. Start Qdrant
docker start local_qdrant

# 2. Index colleges
python populate_qdrant.py

# 3. Verify
python verify_categorization.py
```
