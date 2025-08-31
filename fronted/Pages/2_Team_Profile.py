import streamlit as st
from utils import me, get_my_team, create_team, update_my_team

st.set_page_config(page_title="Team Profile", page_icon="👤")

st.title("👤 Team Profile")

if not st.session_state.get("token"):
    st.warning("Please log in from the Home page.")
    st.stop()

info = me()

def form_for_team(existing=None):
    name = st.text_input("Team Name", value=existing["name"] if existing else "")
    m1 = st.text_input("Member 1", value=existing["member1"] if existing else "")
    m2 = st.text_input("Member 2", value=existing["member2"] if existing else "")
    m3 = st.text_input("Member 3", value=existing["member3"] if existing else "")
    return name, m1, m2, m3

try:
    if info.get("team_id"):
        team = get_my_team()
        st.success(f"You own: {team['name']}")
        st.write(f"Members: {team['member1']}, {team['member2']}, {team['member3']}")
        st.caption(f"Submissions: {team['submission_count']} | Total Score: {team['total_score']:.2f} | Banned: {team['banned']}")
        st.divider()
        st.subheader("Update Team")
        name, m1, m2, m3 = form_for_team(existing=team)
        if st.button("Save Changes"):
            update_my_team(name=name, member1=m1, member2=m2, member3=m3)
            st.success("Updated.")
            st.rerun()
    else:
        st.info("You don't have a team yet. Create one below.")
        name, m1, m2, m3 = form_for_team()
        if st.button("Create Team"):
            create_team(name, m1, m2, m3)
            st.success("Team created.")
            st.rerun()
except Exception as e:
    st.error("Problem loading or saving team.")
    st.caption(str(e))
