import streamlit as st
import os
from database import get_supabase

# Streamlit config
st.set_page_config(page_title="Financial Dashboard", layout="wide")

try:
    supabase = get_supabase()
except Exception as e:
    st.error(f"Could not connect to Supabase: {e}")
    st.stop()

# check if we are actually connected
if not os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL") == "your_supabase_project_url":
    st.warning("⚠️ Please configure your `.env` file with Supabase and Resend credentials to continue.")
    st.stop()

st.title("📈 Financial News & Earnings Monitor")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["News Feed", "Settings: Entities", "Settings: Keywords"])

if page == "News Feed":
    st.header("Latest News")
    
    # Fetch top 50 un-discarded articles sorted by published date
    response = supabase.table("articles").select("*").eq("discarded", False).order("published_at", desc=True).limit(50).execute()
    articles = response.data or []
    
    if not articles:
        st.info("No articles found or all have been discarded.")
    else:
        for article in articles:
            with st.container():
                st.subheader(article['title'])
                st.caption(f"Score: **{article['score']}** | Published: {article['published_at']}")
                col1, col2 = st.columns([1, 10])
                with col1:
                    if st.button("Discard", key=f"discard_{article['id']}"):
                        supabase.table("articles").update({"discarded": True}).eq("id", article['id']).execute()
                        st.rerun()
                with col2:
                    st.markdown(f"**[Read Full Article]({article['url']})**")
                st.divider()

elif page == "Settings: Entities":
    st.header("Tracked Companies")
    
    c_response = supabase.table("companies").select("*").execute()
    companies = c_response.data or []
    
    with st.expander("Add Company", expanded=True):
        with st.form("add_company"):
            new_c = st.text_input("Company Name")
            if st.form_submit_button("Add"):
                if new_c:
                    try:
                        supabase.table("companies").insert({"name": new_c}).execute()
                        st.success(f"Added {new_c}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                    
    st.subheader("Current Companies")
    for c in companies:
        col1, col2 = st.columns([4, 1])
        col1.write(c['name'])
        if col2.button("Delete", key=f"del_c_{c['id']}"):
            supabase.table("companies").delete().eq("id", c['id']).execute()
            st.rerun()
            
    st.divider()
    st.header("Tracked Competitors")
    
    comp_resp = supabase.table("competitors").select("*").execute()
    competitors = comp_resp.data or []
    
    with st.expander("Add Competitor", expanded=True):
        with st.form("add_competitor"):
            new_comp = st.text_input("Competitor Name")
            if st.form_submit_button("Add"):
                if new_comp:
                    try:
                        supabase.table("competitors").insert({"name": new_comp}).execute()
                        st.success(f"Added {new_comp}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                    
    st.subheader("Current Competitors")
    for comp in competitors:
        col1, col2 = st.columns([4, 1])
        col1.write(comp['name'])
        if col2.button("Delete", key=f"del_comp_{comp['id']}"):
            supabase.table("competitors").delete().eq("id", comp['id']).execute()
            st.rerun()

elif page == "Settings: Keywords":
    st.header("Keyword Scoring Configurations")
    st.markdown("Assign scores to keywords. Articles matching these keywords will accumulate weight. Articles reaching high thresholds trigger instant alerts.")
    
    k_response = supabase.table("keywords").select("*").execute()
    keywords = k_response.data or []
    
    with st.expander("Add Keyword", expanded=True):
        with st.form("add_kw"):
            new_kw = st.text_input("Keyword")
            new_weight = st.number_input("Weight (Points)", value=1, step=1)
            if st.form_submit_button("Add"):
                if new_kw:
                    try:
                        supabase.table("keywords").insert({"keyword": new_kw, "weight": new_weight}).execute()
                        st.success(f"Added '{new_kw}' (Weight {new_weight})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                    
    st.subheader("Current Keywords")
    for kw in keywords:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{kw['keyword']}** (Weight: {kw['weight']})")
        if col2.button("Delete", key=f"del_kw_{kw['id']}"):
            supabase.table("keywords").delete().eq("id", kw['id']).execute()
            st.rerun()
