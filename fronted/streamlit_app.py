import streamlit as st
from utils import signup, login, me, public_teams, announcements

st.set_page_config(page_title="ML League", page_icon="🏆", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("🏆 ML League Portal")

with st.sidebar:
    st.header("Account")
    if st.session_state.token:
        info = me()
        st.success(f"Logged in: {info['username']}" + (" (Admin)" if info["is_admin"] else ""))
        if st.button("Log out"):
            st.session_state.token = None
            st.session_state.is_admin = False
            st.rerun()
    else:
        mode = st.radio("Auth mode", ["Login", "Sign up"], horizontal=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if mode == "Sign up":
            if st.button("Create account"):
                try:
                    data = signup(username, password)
                    st.session_state.token = data["access_token"]
                    st.session_state.is_admin = data["is_admin"]
                    st.success("Account created & logged in")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        else:
            if st.button("Login"):
                try:
                    data = login(username, password)
                    st.session_state.token = data["access_token"]
                    st.session_state.is_admin = data["is_admin"]
                    st.success("Logged in")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

st.subheader("📣 Weekly Tasks & Announcements")
try:
    anns = announcements()
    if len(anns) == 0:
        st.info("No announcements yet.")
    for a in anns:
        with st.expander(a["title"]):
            st.write(a["body"])
except Exception as e:
    st.error("Could not load announcements. Configure API_BASE_URL.")
    st.caption(str(e))

st.subheader("👥 Public Teams")
try:
    teams = public_teams()
    st.dataframe(
        [{"Team": t["name"], "Member 1": t["member1"], "Member 2": t["member2"], "Member 3": t["member3"]} for t in teams],
        use_container_width=True
    )
except Exception as e:
    st.error("Could not load teams.")
    st.caption(str(e))

st.markdown("Go to the **pages/** (left sidebar) for: Announcements (admin), Team Profile, Public Dashboard, and Leaderboard & Submission.")
