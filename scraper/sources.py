import requests
from bs4 import BeautifulSoup
import re

def find_college_url(college_name):
    """
    Finds the official website of a college using DuckDuckGo.
    Returns the URL or None.
    """
    print(f"🔎 Searching for official website: {college_name}")
    
    try:
        # Use DuckDuckGo HTML (no API key needed)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        query = f"{college_name} official website"
        url = f"https://html.duckduckgo.com/html/?q={query}"
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract results
        results = soup.find_all('a', class_='result__a')
        
        for link in results:
            href = link['href']
            # Basic validation: looks like a main educational domain
            if 'wikipedia' in href or 'shiksha' in href or 'careers360' in href:
                continue
            
            # Prefer .ac.in, .edu, .org, or the college name in domain
            if '.ac.in' in href or '.edu' in href or 'university' in href or college_name.split()[0].lower() in href:
                print(f"🎯 Found URL: {href}")
                return href
                
        # Fallback: take the first non-ad result if strict logic fails
        if results:
            return results[0]['href']

    except Exception as e:
        print(f"⚠️ Search failed: {e}")
    
    return None
