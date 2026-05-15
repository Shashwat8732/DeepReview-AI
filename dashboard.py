import streamlit as st
from database import get_token, LITESQL_URL
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Code Review Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00ff88;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Code Review Dashboard")
st.caption("Real-time code review analytics")

def get_reviews():
    token = get_token()
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT * FROM code_reviews"}
    )
    return response.json()


data = get_reviews()

if data["success"] and data["data"]:
    reviews = data["data"]
    df = pd.DataFrame(reviews)

    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Reviews", len(reviews))

    with col2:
        critical = sum(1 for r in reviews 
                      if "CRITICAL" in str(r.get("severity", "")))
        st.metric("🔴 Critical PRs", critical)

    with col3:
        repos = set(r.get("repo_name", "") for r in reviews)
        st.metric("📁 Repos Reviewed", len(repos))

    with col4:
        dates = set(r.get("date", "") for r in reviews)
        st.metric("📅 Active Days", len(dates))

    st.divider()

    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Issues By Severity")
        
        
        severity_data = {
            "Severity": ["🔴 Critical", "🟡 Medium", "🟢 Low"],
            "Count": [
                sum(r.get("review_text", "").count("Critical_") and 
                    int(r.get("review_text", "0").split("Critical_")[1].split("_")[0]) 
                    for r in reviews if "Critical_" in str(r.get("review_text", ""))),
                sum(r.get("review_text", "").count("Medium_") and 
                    int(r.get("review_text", "0").split("Medium_")[1].split("_")[0]) 
                    for r in reviews if "Medium_" in str(r.get("review_text", ""))),
                sum(r.get("review_text", "").count("Low_") and 
                    int(r.get("review_text", "0").split("Low_")[1].split("_")[0]) 
                    for r in reviews if "Low_" in str(r.get("review_text", "")))
            ]
        }
        
        fig1 = px.bar(
            severity_data,
            x="Severity",
            y="Count",
            color="Severity",
            color_discrete_map={
                "🔴 Critical": "#ff4444",
                "🟡 Medium": "#ffaa00",
                "🟢 Low": "#00ff88"
            }
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📁 Reviews Per Repo")
        
        repo_counts = df["repo_name"].value_counts().reset_index()
        repo_counts.columns = ["Repo", "Count"]
        
        fig2 = px.pie(
            repo_counts,
            values="Count",
            names="Repo",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

   
    st.subheader("📅 Reviews Timeline")
    
    date_counts = df["date"].value_counts().reset_index()
    date_counts.columns = ["Date", "Reviews"]
    date_counts = date_counts.sort_values("Date")
    
    fig3 = px.line(
        date_counts,
        x="Date",
        y="Reviews",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#00ff88"]
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

   
    st.subheader("📋 Review History")
    
    columns_order = [
        "id", "repo_name", "pr_number",
        "file_name", "severity",
        "review_text", "date", "time"
    ]
    
   
    available = [c for c in columns_order if c in df.columns]
    df = df[available]
    
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Koi reviews nahi mili abhi tak!")
    st.info("Koi PR karo — automatically review ho jayegi!")