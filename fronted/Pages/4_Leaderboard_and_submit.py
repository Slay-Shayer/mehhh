import streamlit as st
from utils import leaderboard, submit_score, get_my_team, me

st.set_page_config(page_title="Leaderboard & Submit", page_icon="🏅")
st.title("🏅 Leaderboard")

# Table
try:
    data = leaderboard()
    if data:
        st.dataframe(
            [
                {
                    "Team": row["team_name"],
                    "Submissions": row["submission_count"],
                    "Total Score": row["total_score"],
                }
                for row in data
            ],
            use_container_width=True
        )
    else:
        st.info("No teams yet.")
except Exception as e:
    st.error("Failed to load leaderboard.")
    st.caption(str(e))

st.divider()
st.subheader("Submit Weekly Score")

if not st.session_state.get("token"):
    st.info("Log in to submit your team's score.")
    st.stop()

try:
    info = me()
    if not info.get("team_id"):
        st.warning("Create a team first (Team Profile page).")
        st.stop()
    team = get_my_team()
    if team["banned"]:
        st.error("Your team is banned; submissions disabled.")
        st.stop()
except Exception as e:
    st.error("Could not verify team.")
    st.caption(str(e))
    st.stop()

score = st.number_input("Score for this week", min_value=0.0, value=0.0, step=0.1)
week = st.text_input("Week Label (optional, e.g., 2025-W35)", value="")

if st.button("Submit Score"):
    try:
        submit_score(score, week or None)
        st.success("Submitted. Leaderboard updated.")
        st.rerun()
    except Exception as e:
        st.error("Submission failed.")
        st.caption(str(e))
