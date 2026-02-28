import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

from database import get_supabase
from email_alerts import send_daily_digest

load_dotenv()

def run_daily_digest():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting daily digest...")
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url or supabase_url == "your_supabase_project_url":
        print("Skipping execution: SUPABASE_URL is not configured in .env.")
        sys.exit(1)
        
    try:
        supabase = get_supabase()
        
        # Get articles from last 24 hours that are not discarded and have score >= 1
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        response = supabase.table("articles").select("*") \
            .eq("discarded", False) \
            .gte("published_at", yesterday) \
            .gt("score", 0) \
            .order("score", desc=True) \
            .execute()
            
        articles = response.data or []
        
        if not articles:
            print("No new relevant articles to send for digest.")
            return

        print(f"Found {len(articles)} articles for digest.")
        send_daily_digest(articles)
        
    except Exception as e:
        print(f"Error during daily digest: {e}")

if __name__ == "__main__":
    run_daily_digest()
