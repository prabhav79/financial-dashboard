import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

from database import get_supabase, get_companies, get_competitors, get_keywords, insert_article
from rss_aggregator import fetch_google_news
from scorer import score_article
from email_alerts import send_instant_alert, send_daily_digest

load_dotenv()
try:
    INSTANT_ALERT_THRESHOLD = int(os.getenv("INSTANT_ALERT_SCORE_THRESHOLD", "10"))
except ValueError:
    INSTANT_ALERT_THRESHOLD = 10

def run_aggregator():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting news aggregation worker...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url or supabase_url == "your_supabase_project_url":
        print("Skipping execution: SUPABASE_URL is not configured in .env.")
        sys.exit(1)
        
    try:
        supabase = get_supabase()
        
        companies = get_companies(supabase) or []
        competitors = get_competitors(supabase) or []
        keywords = get_keywords(supabase) or []
        
        entities_to_track = [c['name'] for c in companies] + [comp['name'] for comp in competitors]
        
        if not entities_to_track:
            print("No companies or competitors found in the database.")
            return
            
        new_high_score_articles = []
            
        for entity in entities_to_track:
            print(f"Fetching news for: {entity}")
            articles = fetch_google_news(entity)
            
            for article in articles:
                score = score_article(article['title'], article['summary'], keywords)
                article['score'] = score
                
                # We only want to insert/care about articles that have SOME significance,
                # but for comprehensive tracking, we can insert all. We'll insert all but only alert on high scores.
                
                result = insert_article(supabase, article)
                
                # result is somewhat truthy if inserted successfully
                if result:
                    if score >= INSTANT_ALERT_THRESHOLD:
                        print(f" -> Instant alert triggered for: {article['title'][:30]}... (Score: {score})")
                        send_instant_alert(article)
                        
        print(f"[{datetime.now(timezone.utc).isoformat()}] Aggregation run complete.")
        
    except Exception as e:
        print(f"Fatal error during aggregation: {e}")

if __name__ == "__main__":
    run_aggregator()
