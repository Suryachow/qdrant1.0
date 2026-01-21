# Qdrant College Data Categorization Guide

## Overview
Your Qdrant database now stores college data in **category-specific collections** with courses organized by program type (B.Tech, M.Tech, MBA, etc.).

## Collection Structure

### 1. **Collection Names**
Each category of college information is stored in a separate Qdrant collection:

- `college_overview` - University overview, establishment year, location, type, description
- `college_rankings` - NIRF, QS, THE rankings and recognitions
- `college_courses_and_fees` - **Categorized courses** (B.Tech, M.Tech, MBA, Other Programs)
- `college_placements` - Placement statistics, packages, recruiters
- `college_facilities` - Campus facilities, infrastructure, amenities
- `college_scholarships` - Scholarship information (if available)

### 2. **Course Categorization**

The `courses_and_fees` field in your `data.json` is structured as:

```json
{
  "courses_and_fees": {
    "B.Tech": [
      {
        "course_name": "B.Tech in Computer Science and Engineering",
        "duration": "4 Years",
        "total_tuition_fee": "Fee details",
        "eligibility": "JEE Advanced criteria"
      }
    ],
    "M.Tech": [
      {
        "course_name": "M.Tech in Computer Science",
        "duration": "2 Years",
        "total_tuition_fee": "Fee details",
        "eligibility": "GATE requirements"
      }
    ],
    "MBA": [
      {
        "course_name": "MBA",
        "duration": "2 Years",
        "total_tuition_fee": "Fee details",
        "eligibility": "CAT requirements"
      }
    ],
    "Other Programs": [
      {
        "course_name": "M.Sc, Ph.D., etc.",
        "duration": "Varies",
        "total_tuition_fee": "Fee details",
        "eligibility": "Program-specific"
      }
    ]
  }
}
```

### 3. **How Data is Indexed**

When a college is indexed to Qdrant:

1. **Each category** (overview, rankings, courses_and_fees, etc.) is indexed separately
2. **For courses_and_fees**: The categorized structure (B.Tech, M.Tech, MBA, Other Programs) is preserved
3. **Vector embeddings** are created from the full text representation of each category
4. **Metadata** includes:
   - `university_name`: Name of the college
   - `college_url`: Website URL
   - `category`: Which category this data belongs to
   - `content`: The actual structured data (preserves the categorization)

### 4. **Example Query Flow**

When searching for "B.Tech courses at IIT Bombay":

1. Query the `college_courses_and_fees` collection
2. The vector search finds relevant colleges
3. The returned `content` field contains the full categorized structure
4. You can then filter/display only the B.Tech category

## Current Status

✅ **38 colleges** are being indexed with categorized course structure
✅ **Category-specific collections** are created automatically
✅ **Course categories** (B.Tech, M.Tech, MBA, Other Programs) are preserved in Qdrant

## Scripts Available

### 1. `populate_qdrant.py`
- Indexes all colleges from `data.json` to Qdrant
- Creates category-specific collections
- Preserves course categorization

### 2. `migrate_courses.py`
- Migrates old flat course lists to categorized structure
- Re-indexes to Qdrant after migration
- (Already completed for your data)

### 3. `check_categories.py`
- Verify which colleges have categorized courses
- Check Qdrant collection status

## Querying Categorized Data

### Python Example:
```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

# Search for B.Tech courses
results = client.search(
    collection_name="college_courses_and_fees",
    query_vector=embedding_model.encode("B.Tech Computer Science"),
    limit=5
)

for result in results:
    college_name = result.payload["university_name"]
    courses = result.payload["content"]
    
    # Access B.Tech courses specifically
    if "B.Tech" in courses:
        btech_courses = courses["B.Tech"]
        print(f"{college_name} offers {len(btech_courses)} B.Tech programs")
```

## Benefits of This Structure

1. **Organized Search**: Query specific course types (B.Tech, M.Tech, etc.)
2. **Efficient Filtering**: Filter by program category without post-processing
3. **Scalable**: Easy to add new categories or course types
4. **Semantic Search**: Vector embeddings capture meaning across all course details
5. **Structured Data**: Maintains JSON structure for easy frontend integration

## Next Steps

1. ✅ Ensure Qdrant is running (`docker start qdrant`)
2. ✅ Run `populate_qdrant.py` to index all colleges (currently running)
3. 🔄 Verify collections using Qdrant dashboard at http://localhost:6333/dashboard
4. 🔄 Test queries to retrieve categorized course data
