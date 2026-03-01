import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from datetime import datetime, timezone
import email.utils

def fetch_google_news(query):
    # Enclose the query in quotes for an exact phrase match
    # and append terms that filter for business/financial news
    # to avoid generic words like "Elevate" returning random articles.
    advanced_query = f'"{query}" (stock OR earnings OR company OR financial)'
    
    # Google News RSS format
    url = f"https://news.google.com/rss/search?q={quote(advanced_query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        articles = []
        # Google News RSS wraps items inside a <channel>
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            # Convert pubDate to ISO 8601 format
            try:
                dt = email.utils.parsedate_to_datetime(pubDate)
                iso_date = dt.isoformat()
            except:
                iso_date = datetime.now(timezone.utc).isoformat()

            articles.append({
                "title": title,
                "url": link,
                "summary": title, # Description contains HTML, using title is safer for simplicity
                "published_at": iso_date
            })
        return articles
    except Exception as e:
        print(f"Error fetching news for {query}: {e}")
        return []
