from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SignUpIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool

class TeamCreate(BaseModel):
    name: str
    member1: str
    member2: str
    member3: str

class TeamOut(BaseModel):
    id: int
    name: str
    member1: str
    member2: str
    member3: str
    banned: bool
    submission_count: int
    total_score: float
    created_at: datetime
    class Config:
        from_attributes = True

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    member1: Optional[str] = None
    member2: Optional[str] = None
    member3: Optional[str] = None

class SubmissionIn(BaseModel):
    score: float
    week: Optional[str] = None

class SubmissionOut(BaseModel):
    id: int
    team_id: int
    score: float
    week: Optional[str]
    submitted_at: datetime
    class Config:
        from_attributes = True

class AnnouncementIn(BaseModel):
    title: str
    body: str

class AnnouncementOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    class Config:
        from_attributes = True
