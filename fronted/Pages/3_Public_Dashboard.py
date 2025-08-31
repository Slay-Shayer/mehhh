import streamlit as st
from utils import public_teams

st.set_page_config(page_title="Public Dashboard", page_icon="🌐")

st.title("🌐 Public Dashboard")

try:
    data = public_teams()
    st.caption("All visible (not banned) teams.")
    st.dataframe(
        [
            {
                "Team": t["name"],
                "Member 1": t["member1"],
                "Member 2": t["member2"],
                "Member 3": t["member3"],
                "Submissions": t["submission_count"],
                "Total Score": t["total_score"],
            }
            for t in data
        ],
        use_container_width=True
    )
except Exception as e:
    st.error("Could not load public teams.")
    st.caption(str(e))
