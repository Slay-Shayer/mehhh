from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    team = relationship("Team", back_populates="owner", uselist=False)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, index=True, nullable=False)
    member1 = Column(String(80), nullable=False)
    member2 = Column(String(80), nullable=False)
    member3 = Column(String(80), nullable=False)
    banned = Column(Boolean, default=False)
    submission_count = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="team")
    submissions = relationship("Submission", back_populates="team", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    score = Column(Float, nullable=False)
    week = Column(String(32), nullable=True)  # optional label like "2025-W35"
    submitted_at = Column(DateTime, server_default=func.now())

    team = relationship("Team", back_populates="submissions")

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    body = Column(String(2000), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
