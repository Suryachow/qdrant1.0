import re

def clean_text(text):
    """Remove extra whitespace and non-printable chars."""
    if not text: return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_course(course_name):
    """Normalize course strings (e.g. 'B. Tech' -> 'B.Tech')"""
    if not course_name: return "Unknown"
    norm = course_name.replace("B. Tech", "B.Tech").replace("Bachelor of Technology", "B.Tech")
    norm = norm.replace("M. Tech", "M.Tech").replace("Master of Technology", "M.Tech")
    return clean_text(norm)
