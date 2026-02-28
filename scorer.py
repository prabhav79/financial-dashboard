import re

def score_article(article_title, article_summary, keywords_list):
    """
    keywords_list is a list of dictionaries, e.g., [{"keyword": "earnings", "weight": 5}]
    returns an integer score
    """
    score = 0
    text_to_search = f"{article_title} {article_summary}".lower()
    
    for kw in keywords_list:
        word = kw.get("keyword", "").lower()
        weight = int(kw.get("weight", 0))
        
        if not word:
            continue
            
        # Use simple boundary regex to match whole words 
        # (e.g., 'ear' won't accidentally match 'earnings')
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, text_to_search):
            score += weight
            
    return score
