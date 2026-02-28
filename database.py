import os
import socket
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# --- ISP DNS Bypass Patch ---
# Some ISPs block *.supabase.co. This monkeypatch forces Python to
# resolve the domain using Google's DNS-over-HTTPS.
_old_getaddrinfo = socket.getaddrinfo

def _custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if "supabase.co" in host.lower():
        try:
            resp = requests.get(f"https://dns.google/resolve?name={host}&type=A", timeout=5).json()
            ips = [ans['data'] for ans in resp.get('Answer', []) if 'data' in ans]
            if ips:
                # Return the resolved IPv4 address with the proper socket tuple format
                return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', (ips[0], port))]
        except Exception as e:
            print(f"Warning: DNS bypass failed for {host} - {e}")
    return _old_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = _custom_getaddrinfo
# ----------------------------

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        print("Warning: Supabase credentials not found. Ensure .env is set. App may fail to connect.")
    return create_client(url, key)

def get_companies(supabase: Client):
    response = supabase.table("companies").select("*").execute()
    return response.data

def get_competitors(supabase: Client):
    response = supabase.table("competitors").select("*").execute()
    return response.data

def get_keywords(supabase: Client):
    response = supabase.table("keywords").select("*").execute()
    return response.data

def insert_article(supabase: Client, article_data: dict):
    try:
        response = supabase.table("articles").insert(article_data).execute()
        return response.data
    except Exception as e:
        # Ignore duplicate unique constraints if the article is already in DB
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            return None
        print(f"Error inserting article: {e}")
        return None

def get_recent_articles(supabase: Client, limit=50):
    response = supabase.table("articles").select("*").eq("discarded", False).order("created_at", desc=True).limit(limit).execute()
    return response.data
