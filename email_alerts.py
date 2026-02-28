import os
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "onboarding@resend.dev")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

def send_email(subject, html_content):
    if not RESEND_API_KEY or not ALERT_EMAIL_TO or RESEND_API_KEY == "your_resend_api_key_for_emails":
        print("Skipping email send: Resend variables not configured in .env.")
        return False
        
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "from": ALERT_EMAIL_FROM,
        "to": [ALERT_EMAIL_TO],
        "subject": subject,
        "html": html_content
    }
    
    try:
        response = requests.post("https://api.resend.com/emails", headers=headers, json=data)
        if response.status_code not in [200, 201]:
            print(f"Failed to send email: {response.text}")
            return False
        else:
            print(f"Successfully sent email to {ALERT_EMAIL_TO}: '{subject}'")
            return True
    except Exception as e:
        print(f"Exception sending email: {e}")
        return False

def send_instant_alert(article):
    subject = f"🚨 High Score Alert: {article.get('title')}"
    html = f"""
    <h2>Important Financial Alert</h2>
    <p>We found an article with a high keyword score!</p>
    <ul>
        <li><strong>Article:</strong> {article.get('title')}</li>
        <li><strong>Score:</strong> {article.get('score')}</li>
        <li><strong>Published:</strong> {article.get('published_at')}</li>
    </ul>
    <p><a href="{article.get('url')}">Read Full Article</a></p>
    """
    send_email(subject, html)

def send_daily_digest(articles):
    if not articles:
        return
        
    subject = f"📈 Daily Morning Digest: {len(articles)} Important Articles"
    
    html = f"<h2>Your Morning Financial Digest</h2><p>Here are {len(articles)} significant articles collected recently.</p><ul>"
    for a in articles:
        html += f"<li><strong>[{a.get('score')} pts]</strong> <a href='{a.get('url')}'>{a.get('title')}</a></li>"
    html += "</ul>"
    
    send_email(subject, html)
