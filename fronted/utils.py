import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL") or st.secrets.get("API_BASE_URL") or "http://localhost:8000"

def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def signup(username, password):
    r = requests.post(f"{API_BASE}/auth/signup", json={"username": username, "password": password})
    r.raise_for_status()
    return r.json()

def login(username, password):
    r = requests.post(f"{API_BASE}/auth/login", json={"username": username, "password": password})
    r.raise_for_status()
    return r.json()

def me():
    r = requests.get(f"{API_BASE}/auth/me", headers=_headers())
    r.raise_for_status()
    return r.json()

def create_team(name, m1, m2, m3):
    r = requests.post(f"{API_BASE}/teams/create", json={"name": name, "member1": m1, "member2": m2, "member3": m3}, headers=_headers())
    r.raise_for_status()
    return r.json()

def get_my_team():
    r = requests.get(f"{API_BASE}/teams/me", headers=_headers())
    r.raise_for_status()
    return r.json()

def update_my_team(**kwargs):
    r = requests.put(f"{API_BASE}/teams/me", json=kwargs, headers=_headers())
    r.raise_for_status()
    return r.json()

def public_teams():
    r = requests.get(f"{API_BASE}/teams/public")
    r.raise_for_status()
    return r.json()

def leaderboard():
    r = requests.get(f"{API_BASE}/leaderboard")
    r.raise_for_status()
    return r.json()

def submit_score(score, week=None):
    payload = {"score": float(score)}
    if week:
        payload["week"] = week
    r = requests.post(f"{API_BASE}/submissions", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()

def announcements():
    r = requests.get(f"{API_BASE}/announcements")
    r.raise_for_status()
    return r.json()

def post_announcement(title, body):
    r = requests.post(f"{API_BASE}/announcements", json={"title": title, "body": body}, headers=_headers())
    r.raise_for_status()
    return r.json()

def delete_announcement(ann_id):
    r = requests.delete(f"{API_BASE}/announcements/{ann_id}", headers=_headers())
    r.raise_for_status()
    return r.json()

def admin_ban(team_id, unban=False):
    path = "unban" if unban else "ban"
    r = requests.post(f"{API_BASE}/admin/teams/{team_id}/{path}", headers=_headers())
    r.raise_for_status()
    return r.json()

def admin_delete_team(team_id):
    r = requests.delete(f"{API_BASE}/admin/teams/{team_id}", headers=_headers())
    r.raise_for_status()
    return r.json()
