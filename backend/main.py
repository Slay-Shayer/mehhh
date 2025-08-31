import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import Base, engine, get_db
from . import models, schemas
from .auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_admin
)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "240"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="ML League API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed admin on first boot (optional)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if ADMIN_USERNAME and ADMIN_PASSWORD:
    with next(get_db()) as db:
        maybe = db.query(models.User).filter(models.User.username == ADMIN_USERNAME).first()
        if not maybe:
            admin = models.User(
                username=ADMIN_USERNAME,
                password_hash=hash_password(ADMIN_PASSWORD),
                is_admin=True
            )
            db.add(admin)
            db.commit()

# Dependency to pass settings to deps
def settings_dep():
    return {"SECRET_KEY": SECRET_KEY, "ALGORITHM": ALGORITHM, "ACCESS_TOKEN_EXPIRE_MINUTES": ACCESS_TOKEN_EXPIRE_MINUTES}

@app.get("/")
def root():
    return {"ok": True, "service": "ml-league-api"}

# ---------- Auth ----------
@app.post("/auth/signup", response_model=schemas.TokenOut)
def signup(payload: schemas.SignUpIn, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = models.User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    access = create_access_token({"sub": user.username, "is_admin": user.is_admin}, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
    return schemas.TokenOut(access_token=access, is_admin=user.is_admin)

@app.post("/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token({"sub": user.username, "is_admin": user.is_admin}, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
    return schemas.TokenOut(access_token=access, is_admin=user.is_admin)

@app.get("/auth/me")
def me(user: models.User = Depends(get_current_user), settings: dict = Depends(settings_dep)):
    return {"username": user.username, "is_admin": user.is_admin, "team_id": user.team_id}

# ---------- Teams ----------
@app.post("/teams/create", response_model=schemas.TeamOut)
def create_team(data: schemas.TeamCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db), settings: dict = Depends(settings_dep)):
    if user.team_id:
        raise HTTPException(status_code=400, detail="You already own a team")
    exists = db.query(models.Team).filter(models.Team.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Team name already in use")
    team = models.Team(
        name=data.name.strip(),
        member1=data.member1.strip(),
        member2=data.member2.strip(),
        member3=data.member3.strip(),
        owner_user_id=user.id
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    user.team_id = team.id
    db.add(user)
    db.commit()
    return team

@app.get("/teams/me", response_model=schemas.TeamOut)
def get_my_team(user: models.User = Depends(get_current_user), db: Session = Depends(get_db), settings: dict = Depends(settings_dep)):
    if not user.team_id:
        raise HTTPException(status_code=404, detail="No team yet")
    team = db.query(models.Team).get(user.team_id)
    return team

@app.put("/teams/me", response_model=schemas.TeamOut)
def update_my_team(data: schemas.TeamUpdate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db), settings: dict = Depends(settings_dep)):
    if not user.team_id:
        raise HTTPException(status_code=404, detail="No team yet")
    team = db.query(models.Team).get(user.team_id)
    if team.banned:
        raise HTTPException(status_code=403, detail="Team is banned")
    for field in ["name", "member1", "member2", "member3"]:
        val = getattr(data, field)
        if val is not None:
            setattr(team, field, val.strip())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

@app.get("/teams/public", response_model=list[schemas.TeamOut])
def list_public(db: Session = Depends(get_db)):
    teams = db.query(models.Team).filter(models.Team.banned == False).order_by(models.Team.created_at.desc()).all()
    return teams

# ---------- Submissions & Leaderboard ----------
@app.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    teams = db.query(models.Team).filter(models.Team.banned == False).order_by(models.Team.total_score.desc()).all()
    return [
        {
            "team_id": t.id,
            "team_name": t.name,
            "submission_count": t.submission_count,
            "total_score": t.total_score
        } for t in teams
    ]

@app.post("/submissions", response_model=schemas.SubmissionOut)
def submit_score(data: schemas.SubmissionIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.team_id:
        raise HTTPException(status_code=400, detail="Create a team first")
    team = db.query(models.Team).get(user.team_id)
    if team.banned:
        raise HTTPException(status_code=403, detail="Team is banned")
    sub = models.Submission(team_id=team.id, score=float(data.score), week=data.week)
    team.submission_count += 1
    team.total_score += float(data.score)
    db.add(sub)
    db.add(team)
    db.commit()
    db.refresh(sub)
    return sub

# ---------- Announcements ----------
@app.get("/announcements", response_model=list[schemas.AnnouncementOut])
def get_announcements(db: Session = Depends(get_db)):
    rows = db.query(models.Announcement).order_by(models.Announcement.created_at.desc()).all()
    return rows

@app.post("/announcements", response_model=schemas.AnnouncementOut)
def post_announcement(
    data: schemas.AnnouncementIn,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    row = models.Announcement(title=data.title.strip(), body=data.body.strip(), created_by=admin.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.delete("/announcements/{ann_id}")
def delete_announcement(ann_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    row = db.query(models.Announcement).get(ann_id)
    if not row:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(row)
    db.commit()
    return {"ok": True}

# ---------- Admin: Ban/Delete Teams ----------
@app.post("/admin/teams/{team_id}/ban")
def ban_team(team_id: int, _: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    team = db.query(models.Team).get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.banned = True
    db.add(team)
    db.commit()
    return {"ok": True, "status": "banned"}

@app.post("/admin/teams/{team_id}/unban")
def unban_team(team_id: int, _: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    team = db.query(models.Team).get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.banned = False
    db.add(team)
    db.commit()
    return {"ok": True, "status": "unbanned"}

@app.delete("/admin/teams/{team_id}")
def delete_team(team_id: int, _: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    team = db.query(models.Team).get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    return {"ok": True, "status": "deleted"}
