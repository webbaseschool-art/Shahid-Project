# Nexlas AI — Complete Project Documentation

**Last updated:** September 2026
**Event:** Alibaba Cloud AI Hackathon Pakistan 2026
**Team:** 4-person team (Backend/API + DB + AI, Frontend HTML/CSS/JS, Deployment + Pitch)

---

## 1. Project Overview

Nexlas AI is a career-guidance layer on an online learning platform. It takes a learner through a structured diagnostic, recommends a career path, analyzes skill gaps, matches courses and mentors, and generates a 30/60/90-day roadmap.

**Core loop:** Diagnose > Understand > Recommend > Roadmap > Action

### Key Design Decisions

- **AI provider:** Gemini (`gemini-3.6-flash`) via `google-genai` — Qwen (original plan) was not used.
- **Diagnostic is fully hardcoded** — 8 fixed questions, not an open AI conversation.
- **Gemini's role (narrow and validated):**
  1. Picks the best-fit career from 5 real careers (deterministic fallback if it fails)
  2. Sequences already-matched real courses into month1/month2/month3 (output validated against exact course list)
  3. Writes the plain-language roadmap explanation
- **Everything else stays deterministic:** skill-gap calculation, fit-score math, course matching by skill, mentor matching by specialization.
- **Every Gemini call has a deterministic fallback** so the demo cannot break if Gemini is down.

### Data Flow

```
User > Hardcoded diagnostic (8 questions) > Gemini picks career (validated)
     > Deterministic skill-gap/course/mentor matching > Gemini sequences roadmap + explains
     > Persisted to DB
```

---

## 2. Architecture

**Single-origin serving:** FastAPI serves both the REST API and the static Frontend files from one server. No CORS needed.

- `Backend/main.py` mounts `StaticFiles` at `/` with `html=True` after all API routers.
- Frontend JS uses `window.location.origin` as the API base URL.
- `FRONTEND_DIR` env var can override the default `../Frontend` path for deployments.

```
Browser > http://localhost:8000
          |-- /auth/*, /chat/*, /recommendations/*, /roadmap/*  > FastAPI API
          |-- /*                                                > Static Frontend files
```

---

## 3. Tech Stack

| Layer | Choice | Status |
|---|---|---|
| Backend | Python, FastAPI | Running |
| Database | PostgreSQL (18) | 7 tables, seeded |
| AI | Gemini (`gemini-3.6-flash`) via `google-genai` | Working |
| Frontend | HTML/CSS/JS (vanilla, no framework) | Integrated |
| Static serving | FastAPI `StaticFiles` | Single-origin |
| Test harness | Streamlit | Built, all 4 stages tested |
| Deployment | Alibaba Cloud | Pending |

---

## 4. Complete Folder Structure

```
D:\Nexlas Project\
|-- Backend\
|   |-- main.py                    # FastAPI app + static file serving
|   |-- config.py                  # Environment config (.env loader)
|   |-- database.py                # SQLAlchemy engine + session
|   |-- create_table.py            # DDL: creates all tables
|   |-- gemini.py                  # Quick Gemini API connectivity test
|   |-- streamlitui.py             # Streamlit test console (4 tabs)
|   |-- reseed_mentors.py          # One-off mentor reseeding script
|   |-- requirements.txt
|   |-- .env
|   |
|   |-- models\
|   |   |-- __init__.py            # (empty)
|   |   |-- user.py
|   |   |-- career.py
|   |   |-- course.py
|   |   |-- mentor.py
|   |   |-- learner_profile.py
|   |   |-- chat_message.py
|   |   |-- roadmap.py
|   |
|   |-- schemas\
|   |   |-- auth_schema.py
|   |   |-- chat_schema.py
|   |   |-- profile_schema.py
|   |   |-- recommendation_schema.py
|   |   |-- roadmap_schema.py
|   |
|   |-- routers\
|   |   |-- auth.py                # POST /auth/register, /auth/login
|   |   |-- chat.py                # GET /chat/next/{id}, POST /chat/answer
|   |   |-- recommendations.py     # GET /recommendations/{id}, /catalog/*
|   |   |-- roadmap.py             # GET /roadmap/{id}
|   |
|   |-- services\
|   |   |-- __init__.py            # (empty)
|   |   |-- ai_client.py           # Gemini wrapper
|   |   |-- conversation_manager.py # Hardcoded 8-question diagnostic
|   |   |-- matching_engine.py     # Career/course/mentor matching
|   |   |-- roadmap_generator.py   # Roadmap sequencing + explanation
|   |
|   |-- seed\
|       |-- seed_data.json          # 5 careers, 20 courses, 5 mentors
|       |-- seed_db.py             # Database seeder
|
|-- Frontend\
|   |-- index.html                 # Main onboarding wizard (NexlasGPT)
|   |-- login.html                 # Login page
|   |-- register.html              # Registration page
|   |
|   |-- pages\
|   |   |-- dashboard.html         # Career diagnosis dashboard
|   |   |-- roadmap.html           # 30/60/90-day roadmap
|   |   |-- learning.html          # Course catalog
|   |   |-- mentors.html           # Mentor directory
|   |
|   |-- css\
|   |   |-- index.css, auth.css, dashboard.css, roadmap.css, learning.css, mentors.css
|   |
|   |-- js\
|   |   |-- api.js                 # Centralized API client
|   |   |-- shared.js              # Shared state, toast, chat widget
|   |   |-- auth.js                # Login/register handlers
|   |   |-- index.js               # Onboarding wizard logic (466 lines)
|   |   |-- dashboard.js           # Dashboard page logic
|   |   |-- roadmap.js             # Roadmap page logic
|   |   |-- learning.js            # Learning catalog logic
|   |   |-- mentors.js             # Mentors page logic
|   |
|   |-- assets\images\download.png  # Nexlas AI logo
|
|-- Nexlas_AI_Project_Documentation.md  # This file
```

---

## 5. Environment Setup

### PostgreSQL (Windows)
```sql
CREATE DATABASE nexlas_db;
CREATE USER nexlas_user WITH PASSWORD '62922';
GRANT ALL PRIVILEGES ON DATABASE nexlas_db TO nexlas_user;
-- Postgres 15+ schema permission fix:
\c nexlas_db
GRANT ALL ON SCHEMA public TO nexlas_user;
GRANT CREATE ON SCHEMA public TO nexlas_user;
```

### Python Packages
```bash
pip install fastapi uvicorn python-dotenv sqlalchemy psycopg2-binary pydantic
pip install passlib[bcrypt] email-validator bcrypt==4.0.1
pip install google-genai streamlit requests
```

### `.env`
```
DATABASE_URL=postgresql://nexlas_user:62922@localhost:5432/nexlas_db
GEMINI_API_KEY=<your_gemini_key>
GEMINI_MODEL=gemini-3.6-flash
DEBUG=True
FRONTEND_DIR=
```

### Running the App
```bash
cd Backend && uvicorn main:app --reload
# App at http://localhost:8000

# Optional test console (separate terminal):
cd Backend && streamlit run streamlitui.py
```

---

## 6. Backend Code

### `requirements.txt`
```
fastapi
uvicorn
python-dotenv
sqlalchemy
psycopg2-binary
pydantic
passlib[bcrypt]
email-validator
bcrypt==4.0.1
google-genai
```

### `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nexlas.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
APP_NAME = "Nexlas AI Backend"
DEBUG = os.getenv("DEBUG", "True") == "True"
FRONTEND_DIR = os.getenv("FRONTEND_DIR")
```

### `database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `main.py`
```python
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import APP_NAME, FRONTEND_DIR
from routers import auth, chat, recommendations, roadmap

app = FastAPI(title=APP_NAME)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(recommendations.router)
app.include_router(roadmap.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

frontend_path = Path(FRONTEND_DIR) if FRONTEND_DIR else Path(__file__).resolve().parent.parent / "Frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
```

### `create_table.py`
```python
from database import Base, engine
from models.user import User
from models.career import Career
from models.course import Course
from models.mentor import Mentor
from models.learner_profile import LearnerProfile
from models.chat_message import ChatMessage
from models.roadmap import Roadmap

Base.metadata.create_all(bind=engine)
print("All tables created successfully.")
```

---

### Models (`models/`)

**`user.py`**
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**`career.py`**
```python
from sqlalchemy import Column, Integer, String, JSON
from database import Base

class Career(Base):
    __tablename__ = "careers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    required_skills = Column(JSON, nullable=False)
```

**`course.py`**
```python
from sqlalchemy import Column, Integer, String
from database import Base

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    skill_covered = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    description = Column(String, nullable=False)
```

**`mentor.py`**
```python
from sqlalchemy import Column, Integer, String
from database import Base

class Mentor(Base):
    __tablename__ = "mentors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    bio = Column(String, nullable=False)
    email = Column(String, nullable=False)
```

**`learner_profile.py`**
```python
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    education = Column(JSON)
    experience = Column(JSON)
    skills = Column(JSON)
    interests = Column(JSON)
    career_goal = Column(String)
    constraints = Column(JSON)
    diagnostic_status = Column(String, default="in_progress")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
```

**`chat_message.py`** — Not currently used by any router. Optional debug/replay log.
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**`roadmap.py`**
```python
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_recommendation = Column(String, nullable=False)
    fit_score = Column(Float, nullable=False)
    skill_gaps = Column(JSON)
    recommended_courses = Column(JSON)
    recommended_mentor = Column(Integer, ForeignKey("mentors.id"))
    roadmap_steps = Column(JSON)
    next_action = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

### Schemas (`schemas/`)

**`auth_schema.py`**
```python
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True
```

**`chat_schema.py`**
```python
from pydantic import BaseModel
from typing import List, Optional, Any

class DiagnosticQuestion(BaseModel):
    id: str
    question: str
    type: str
    options: Optional[List[str]] = None

class DiagnosticAnswer(BaseModel):
    question_id: str
    answer: Any

class ChatRequest(BaseModel):
    user_id: int
    answers: List[DiagnosticAnswer]

class ChatResponse(BaseModel):
    next_question: Optional[DiagnosticQuestion] = None
    diagnostic_status: str
```

**`profile_schema.py`**
```python
from pydantic import BaseModel
from typing import List, Optional

class Education(BaseModel):
    level: str
    field: Optional[str] = None

class Experience(BaseModel):
    years: str
    field: Optional[str] = None

class SkillItem(BaseModel):
    skill: str
    level: str

class Constraints(BaseModel):
    time_available: str
    learning_style: str

class LearnerProfileInput(BaseModel):
    education: Education
    experience: Experience
    skills: List[SkillItem]
    interests: List[str]
    career_goal: str
    constraints: Constraints

class LearnerProfileResponse(LearnerProfileInput):
    id: int
    user_id: int
    diagnostic_status: str
    class Config:
        from_attributes = True
```

**`recommendation_schema.py`**
```python
from pydantic import BaseModel
from typing import List

class SkillGap(BaseModel):
    skill: str
    required_level: float
    current_level: float
    gap: float

class RecommendedCourse(BaseModel):
    id: int
    title: str
    skill_covered: str
    difficulty: str

class RecommendedMentor(BaseModel):
    id: int
    name: str
    specialization: str
    bio: str
    email: str

class RecommendationResponse(BaseModel):
    career_title: str
    fit_score: float
    skill_gaps: List[SkillGap]
    recommended_courses: List[RecommendedCourse]
    recommended_mentor: RecommendedMentor
```

**`roadmap_schema.py`**
```python
from pydantic import BaseModel
from typing import List, Dict

class RoadmapSteps(BaseModel):
    month1: List[str]
    month2: List[str]
    month3: List[str]

class RoadmapResponse(BaseModel):
    id: int
    user_id: int
    career_recommendation: str
    fit_score: float
    skill_gaps: List[Dict]
    recommended_courses: List[int]
    recommended_mentor: int
    roadmap_steps: RoadmapSteps
    next_action: str
    class Config:
        from_attributes = True
```

---

### Services (`services/`)

**`ai_client.py`** — Gemini wrapper
```python
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_text(prompt: str, system_instruction: str = None) -> str:
    try:
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt,
            config=config if config else None)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None
```

**`conversation_manager.py`** — Hardcoded 8-question diagnostic
```python
from sqlalchemy.orm import Session
from models.learner_profile import LearnerProfile

QUESTIONS = [
    {"id":"education_level","question":"What's your current education level?",
     "type":"single_select","options":["High school","Bachelor's in progress","Bachelor's completed","Master's or higher"]},
    {"id":"education_field","question":"What field is/was your education in?","type":"text","options":None},
    {"id":"experience_years","question":"Do you have any work experience related to a career field?",
     "type":"single_select","options":["None","Less than 1 year","1-3 years","3+ years"]},
    {"id":"skills","question":"Which of these skills do you already have?",
     "type":"multi_select","options":["SQL","Excel","Python","Data Visualization","Statistics","JavaScript","React","CSS","HTML","Git","Figma","Wireframing","User Research","Design Systems","SEO","Content Strategy","Google Analytics","Social Media Ads","Copywriting","Machine Learning"]},
    {"id":"interests","question":"Which of these areas interest you most?",
     "type":"multi_select","options":["Data","Web Development","Design","Marketing","Machine Learning"]},
    {"id":"career_goal","question":"What's your career goal?","type":"text","options":None},
    {"id":"time_available","question":"How much time can you commit weekly to learning?",
     "type":"single_select","options":["Less than 5hrs","5-10hrs","10+hrs"]},
    {"id":"learning_style","question":"How do you prefer to learn?",
     "type":"single_select","options":["Video","Hands-on","Reading"]},
]

def get_or_create_profile(db: Session, user_id: int) -> LearnerProfile:
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        profile = LearnerProfile(user_id=user_id, education={}, experience={}, skills=[],
                                 interests=[], career_goal="", constraints={}, diagnostic_status="in_progress")
        db.add(profile); db.commit(); db.refresh(profile)
    return profile

def get_next_question(profile: LearnerProfile):
    answered_ids = _get_answered_ids(profile)
    for q in QUESTIONS:
        if q["id"] not in answered_ids: return q
    return None

def _get_answered_ids(profile):
    answered = []
    if profile.education and profile.education.get("level"): answered.append("education_level")
    if profile.education and profile.education.get("field"): answered.append("education_field")
    if profile.experience and profile.experience.get("years"): answered.append("experience_years")
    if profile.skills: answered.append("skills")
    if profile.interests: answered.append("interests")
    if profile.career_goal: answered.append("career_goal")
    if profile.constraints and profile.constraints.get("time_available"): answered.append("time_available")
    if profile.constraints and profile.constraints.get("learning_style"): answered.append("learning_style")
    return answered

def save_answer(db, profile, question_id, answer):
    if question_id == "education_level":
        profile.education = {**(profile.education or {}), "level": answer}
    elif question_id == "education_field":
        profile.education = {**(profile.education or {}), "field": answer}
    elif question_id == "experience_years":
        profile.experience = {**(profile.experience or {}), "years": answer}
    elif question_id == "skills":
        profile.skills = [{"skill": s, "level": "intermediate"} for s in answer]
    elif question_id == "interests": profile.interests = answer
    elif question_id == "career_goal": profile.career_goal = answer
    elif question_id == "time_available":
        profile.constraints = {**(profile.constraints or {}), "time_available": answer}
    elif question_id == "learning_style":
        profile.constraints = {**(profile.constraints or {}), "learning_style": answer}
    else: raise ValueError(f"Unknown question_id: {question_id}")
    if get_next_question(profile) is None: profile.diagnostic_status = "completed"
    db.commit(); db.refresh(profile)
    return profile
```

**`matching_engine.py`** — Career/course/mentor matching
```python
from sqlalchemy.orm import Session
from models.career import Career
from models.course import Course
from models.mentor import Mentor
from models.learner_profile import LearnerProfile
from services.ai_client import generate_text

def pick_career_with_gemini(profile, careers):
    career_titles = [c.title for c in careers]
    skills_list = ", ".join([s["skill"] for s in (profile.skills or [])]) or "none"
    interests_list = ", ".join(profile.interests or []) or "none"
    prompt = f"""Match this learner to ONE career from: {career_titles}.
Skills: {skills_list}. Interests: {interests_list}. Goal: {profile.career_goal or "not specified"}.
Education: {profile.education}. Experience: {profile.experience}.
Respond with ONLY the exact career title. No explanation."""
    result = generate_text(prompt)
    if result:
        cleaned = result.strip()
        for career in careers:
            if career.title.lower() == cleaned.lower(): return career
    return _fallback_pick_career(profile, careers)

def _fallback_pick_career(profile, careers):
    user_skills = {s["skill"] for s in (profile.skills or [])}
    best_career, best_score = None, -1
    for career in careers:
        score = sum(r["weight"] for r in (career.required_skills or []) if r["skill"] in user_skills)
        if score > best_score: best_score = score; best_career = career
    return best_career or careers[0]

def calculate_skill_gaps(profile, career):
    level_map = {"beginner": 0.3, "intermediate": 0.6, "advanced": 1.0}
    user_skills = {s["skill"]: level_map.get(s["level"], 0.5) for s in (profile.skills or [])}
    gaps = []
    for req in (career.required_skills or []):
        current = user_skills.get(req["skill"], 0.0)
        gaps.append({"skill": req["skill"], "required_level": req["weight"],
                      "current_level": current, "gap": max(round(req["weight"] - current, 2), 0.0)})
    gaps.sort(key=lambda g: g["gap"], reverse=True)
    return gaps

def calculate_fit_score(profile, career):
    user_skills = {s["skill"] for s in (profile.skills or [])}
    required = career.required_skills or []
    if not required: return 0.0
    total = sum(r["weight"] for r in required)
    matched = sum(r["weight"] for r in required if r["skill"] in user_skills)
    return round((matched / total) * 100, 1) if total else 0.0

def match_courses(db, skill_gaps, limit=5):
    matched = []
    for g in [g for g in skill_gaps if g["gap"] > 0]:
        course = db.query(Course).filter(Course.skill_covered == g["skill"]).first()
        if course and course not in matched: matched.append(course)
        if len(matched) >= limit: break
    return matched

def match_mentor(db, career):
    mentor = db.query(Mentor).filter(Mentor.specialization == career.title).first()
    return mentor or db.query(Mentor).first()

def run_matching(db, profile):
    careers = db.query(Career).all()
    career = pick_career_with_gemini(profile, careers)
    return {"career": career, "fit_score": calculate_fit_score(profile, career),
            "skill_gaps": calculate_skill_gaps(profile, career),
            "courses": match_courses(db, calculate_skill_gaps(profile, career)),
            "mentor": match_mentor(db, career)}
```

**`roadmap_generator.py`** — Roadmap sequencing + explanation
```python
import json
from services.ai_client import generate_text

def _fallback_roadmap_steps(course_ids, courses_by_id):
    titles = [courses_by_id[cid].title for cid in course_ids if cid in courses_by_id]
    third = max(1, len(titles) // 3) or 1
    return {"month1": titles[:third] or ["Review fundamentals"],
            "month2": titles[third:third*2] or ["Continue building core skills"],
            "month3": titles[third*2:] or ["Apply skills to a project"]}

def generate_roadmap_steps(career_title, skill_gaps, courses, career_goal):
    course_titles = [c.title for c in courses]
    courses_by_id = {c.id: c for c in courses}
    if not course_titles: return _fallback_roadmap_steps([c.id for c in courses], courses_by_id)
    gap_summary = ", ".join([f"{g['skill']} (gap: {g['gap']})" for g in skill_gaps[:5]])
    prompt = f"""Organize these courses into a 30/60/90 day plan for a {career_title}.
Goal: "{career_goal}". Gaps: {gap_summary}.
Courses (use exact titles, do not add/remove): {course_titles}
Respond with ONLY JSON: {{"month1":[...],"month2":[...],"month3":[...]}}"""
    result = generate_text(prompt)
    if result:
        try:
            parsed = json.loads(result.strip().strip("`").replace("json\n","").strip())
            all_r = parsed.get("month1",[])+parsed.get("month2",[])+parsed.get("month3",[])
            if set(all_r) <= set(course_titles) and len(all_r) > 0: return parsed
        except: pass
    return _fallback_roadmap_steps([c.id for c in courses], courses_by_id)

def generate_explanation(career_title, fit_score, skill_gaps, career_goal):
    gap_summary = ", ".join([g["skill"] for g in skill_gaps[:3]])
    result = generate_text(f"""Write 3-4 encouraging sentences for a learner matched to "{career_title}"
({fit_score}% fit). Goal: "{career_goal}". Gaps: {gap_summary}. No invented facts.""")
    return result.strip() if result else f"{career_title} is a strong match at {fit_score}%. Focus on {gap_summary}."

def build_and_save_roadmap(db, user_id, matching_result, career_goal):
    from models.roadmap import Roadmap
    c, f, sg, courses, m = [matching_result[k] for k in ["career","fit_score","skill_gaps","courses","mentor"]]
    steps = generate_roadmap_steps(c.title, sg, courses, career_goal)
    explanation = generate_explanation(c.title, f, sg, career_goal)
    next_action = (f"Start with '{courses[0].title}'" if courses else f"Connect with mentor {m.name}")
    roadmap = Roadmap(user_id=user_id, career_recommendation=c.title, fit_score=f, skill_gaps=sg,
                      recommended_courses=[x.id for x in courses], recommended_mentor=m.id,
                      roadmap_steps=steps, next_action=f"{next_action}. {explanation}")
    db.add(roadmap); db.commit(); db.refresh(roadmap)
    return roadmap
```

---

### Routers (`routers/`)

**`auth.py`**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models.user import User
from schemas.auth_schema import RegisterRequest, LoginRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, password_hash=pwd_context.hash(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user
```

**`chat.py`**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.chat_schema import ChatRequest, ChatResponse, DiagnosticQuestion
from services.conversation_manager import get_or_create_profile, get_next_question, save_answer

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/next/{user_id}", response_model=ChatResponse)
def get_next(user_id: int, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, user_id)
    next_q = get_next_question(profile)
    return ChatResponse(next_question=DiagnosticQuestion(**next_q) if next_q else None,
                        diagnostic_status=profile.diagnostic_status)

@router.post("/answer", response_model=ChatResponse)
def submit_answer(payload: ChatRequest, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, payload.user_id)
    for ans in payload.answers:
        try: profile = save_answer(db, profile, ans.question_id, ans.answer)
        except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
    next_q = get_next_question(profile)
    return ChatResponse(next_question=DiagnosticQuestion(**next_q) if next_q else None,
                        diagnostic_status=profile.diagnostic_status)
```

**`recommendations.py`**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.learner_profile import LearnerProfile
from models.course import Course
from models.mentor import Mentor
from schemas.recommendation_schema import RecommendationResponse, SkillGap, RecommendedCourse, RecommendedMentor
from services.matching_engine import run_matching

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendation(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile: raise HTTPException(404, "No profile found")
    if profile.diagnostic_status != "completed": raise HTTPException(400, "Diagnostic not completed")
    r = run_matching(db, profile)
    return RecommendationResponse(
        career_title=r["career"].title, fit_score=r["fit_score"],
        skill_gaps=[SkillGap(**g) for g in r["skill_gaps"]],
        recommended_courses=[RecommendedCourse(id=c.id,title=c.title,skill_covered=c.skill_covered,difficulty=c.difficulty) for c in r["courses"]],
        recommended_mentor=RecommendedMentor(id=r["mentor"].id,name=r["mentor"].name,
            specialization=r["mentor"].specialization,bio=r["mentor"].bio,email=r["mentor"].email))

@router.get("/catalog/courses")
def list_courses(db: Session = Depends(get_db)):
    return [{"id":c.id,"title":c.title,"category":c.category,"skill_covered":c.skill_covered,
             "difficulty":c.difficulty,"description":c.description} for c in db.query(Course).all()]

@router.get("/catalog/mentors")
def list_mentors(db: Session = Depends(get_db)):
    return [{"id":m.id,"name":m.name,"specialization":m.specialization,
             "bio":m.bio,"email":m.email} for m in db.query(Mentor).all()]
```

**`roadmap.py`**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.roadmap import Roadmap
from models.learner_profile import LearnerProfile
from schemas.roadmap_schema import RoadmapResponse
from services.matching_engine import run_matching
from services.roadmap_generator import build_and_save_roadmap

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

@router.get("/{user_id}", response_model=RoadmapResponse)
def get_roadmap(user_id: int, db: Session = Depends(get_db)):
    existing = db.query(Roadmap).filter(Roadmap.user_id == user_id).first()
    if existing: return existing
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile: raise HTTPException(404, "No profile found")
    if profile.diagnostic_status != "completed": raise HTTPException(400, "Diagnostic not completed")
    return build_and_save_roadmap(db, user_id, run_matching(db, profile), profile.career_goal)
```

---

### Seed Data (`seed/`)

**`seed_data.json`** contains 5 careers, 20 courses, and 5 mentors. See `Backend/seed/seed_data.json` for full JSON.

Careers: Data Analyst, Frontend Developer, UI/UX Designer, Digital Marketing Specialist, Data Scientist. Each has weighted `required_skills`.

Courses: 20 courses mapped 1:1 to skills (e.g. "SQL for Beginners" covers "SQL", beginner level).

Mentors: One per career with name, specialization, bio, and email.

**`seed_db.py`** loads `seed_data.json`, inserts all records. Skips if careers already exist.

### Utility Scripts

- **`gemini.py`** -- Quick Gemini API chat test (standalone, not part of app).
- **`reseed_mentors.py`** -- Isolated mentor reseed from seed data.
- **`streamlitui.py`** -- 4-tab Streamlit test console (Auth, Diagnostic, Recommendation, Roadmap).

---

## 7. Frontend Code

### `js/api.js` -- Centralized API Client
```javascript
const API_BASE = window.location.origin;
const API = {
  getSession() { try { return JSON.parse(sessionStorage.getItem('nexlas_session')); } catch(e) { return null; } },
  setSession(user) { sessionStorage.setItem('nexlas_session', JSON.stringify(user)); },
  clearSession() { sessionStorage.removeItem('nexlas_session'); },
  getUserId() { const s = this.getSession(); return s ? s.id : null; },
  async request(method, path, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API_BASE + path, opts);
    if (!res.ok) { const err = await res.json().catch(() => ({ detail: res.statusText })); throw new Error(err.detail || 'Request failed'); }
    return res.json();
  },
  register(name, email, password) { return this.request('POST', '/auth/register', { name, email, password }); },
  login(email, password) { return this.request('POST', '/auth/login', { email, password }); },
  getNextQuestion(userId) { return this.request('GET', '/chat/next/' + userId); },
  submitAnswers(userId, answers) { return this.request('POST', '/chat/answer', { user_id: userId, answers }); },
  getRecommendations(userId) { return this.request('GET', '/recommendations/' + userId); },
  getRoadmap(userId) { return this.request('GET', '/roadmap/' + userId); },
  getCourses() { return this.request('GET', '/recommendations/catalog/courses'); },
  getMentors() { return this.request('GET', '/recommendations/catalog/mentors'); },
};
```

### `js/shared.js` -- State, Toast, Chat Widget, Persistence (140 lines)

Defines global `state` object (story, education, field, experience, skills, interests, goal, timeAvailable, learningStyle), `appData` (roadmapDone, learningDone, filters, sessions), `TOTAL_STEPS=15`, `STEP_LABELS` array, `toast()` function, chat widget functions (`toggleChat`, `pushChat`, `askChat`, `sendChat`), and `saveProjectData()`/`loadProjectData()` for localStorage persistence.

> Full source at `Frontend/js/shared.js`.

### `js/auth.js` -- Login/Register (103 lines)

Handles `handleRegister()` and `handleLogin()` form submissions, calls `API.register()`/`API.login()`, saves session via `API.setSession()`, redirects to dashboard on success.

> Full source at `Frontend/js/auth.js`.

### `js/dashboard.js` -- Dashboard Page (80 lines)

`updateUserDisplay()` updates sidebar chips from session. `renderDashboard()` fetches `API.getRecommendations()`, renders readiness gauge ring, career match icon/title/percentage, and quick stats.

> Full source at `Frontend/js/dashboard.js`.

### `js/roadmap.js` -- Roadmap Page (106 lines)

Fetches `API.getRoadmap()`, renders 3-month milestone grid with MONTH_LABELS, completion toggle via `appData.roadmapDone`, and progress bar.

> Full source at `Frontend/js/roadmap.js`.

### `js/learning.js` -- Learning Catalog (65 lines)

Fetches `API.getCourses()`, renders filterable course grid with category chips, completion toggle via `appData.learningDone`.

> Full source at `Frontend/js/learning.js`.

### `js/mentors.js` -- Mentors Page (64 lines)

Fetches `API.getMentors()`, renders mentor cards with specialization filters, email contact, booking via `appData.sessions`.

> Full source at `Frontend/js/mentors.js`.

### `js/index.js` -- Onboarding Wizard (466 lines)

Key functions:

| Function | Purpose |
|---|---|
| `renderStepper()` | 15-step progress indicator |
| `goStep(n)` | Navigate wizard steps (1-9 interactive, 10+ results) |
| Steps 2-9 | Story, Education, Experience, Skills, Interests, Career Goal, Time, Learning Style |
| `submitToBackend()` | Maps wizard state to 8 diagnostic answers |
| `runAnalysis()` | Animated loading, calls backend, fetches recommendations + roadmap |
| `showResults(recs, roadmap)` | Career match ring, have/need skills, readiness gauge, timeline |
| `restartAll()` | Reset all wizard state |

> Full source at `Frontend/js/index.js`.

### HTML Pages

All pages share: sidebar nav, topbar with profile chips, chat widget, script order (api.js > shared.js > page JS).

| Page | File | Lines | Purpose |
|---|---|---|---|
| Onboarding | `index.html` | 347 | 9-step wizard, AI analysis, diagnosis results |
| Login | `login.html` | 49 | Email/password login |
| Register | `register.html` | 64 | Registration with password confirm |
| Dashboard | `pages/dashboard.html` | 89 | Readiness gauge, match, stats |
| Roadmap | `pages/roadmap.html` | 58 | 30/60/90-day milestones |
| Learning | `pages/learning.html` | 57 | Course catalog |
| Mentors | `pages/mentors.html` | 61 | Mentor directory + sessions |

### CSS Stylesheets

Each page has a self-contained stylesheet: `index.css`, `auth.css`, `dashboard.css`, `roadmap.css`, `learning.css`, `mentors.css`.

---

## 8. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login |
| `GET` | `/chat/next/{user_id}` | Next diagnostic question |
| `POST` | `/chat/answer` | Submit answers |
| `GET` | `/recommendations/{user_id}` | Career recommendation + gaps + courses + mentor |
| `GET` | `/recommendations/catalog/courses` | All courses |
| `GET` | `/recommendations/catalog/mentors` | All mentors |
| `GET` | `/roadmap/{user_id}` | 30/60/90-day roadmap |
| `GET` | `/health` | Health check |

---

## 9. Database Schema

| Table | Key Columns | Purpose |
|---|---|---|
| `users` | id, name, email, password_hash | User accounts |
| `careers` | id, title, description, required_skills (JSON) | 5 career profiles |
| `courses` | id, title, category, skill_covered, difficulty | 20 courses |
| `mentors` | id, name, specialization, bio, email | 5 mentors |
| `learner_profiles` | id, user_id, education, experience, skills, interests, career_goal, constraints, diagnostic_status | Diagnostic data |
| `chat_messages` | id, user_id, role, content | (unused) Future chat |
| `roadmaps` | id, user_id, career_recommendation, fit_score, skill_gaps, recommended_courses, recommended_mentor, roadmap_steps, next_action | Persisted roadmaps |

---

## 10. Known Issues and Fixes

| # | Issue | Fix |
|---|---|---|
| 1 | `psql` not recognized | Add Postgres bin to PATH |
| 2 | `permission denied for schema public` | `GRANT ALL ON SCHEMA public TO nexlas_user` |
| 3 | `bcrypt`/`passlib` conflict | Pin `bcrypt==4.0.1` |
| 4 | FK dependency on DROP | Use `CASCADE` |
| 5 | Seed duplication | Reseed mentors in isolation |
| 6 | 404 on endpoints | Verify `include_router()` in main.py |
| 7 | Empty tables after fix | Verify counts after drop/recreate |
| 8 | `models/__ini__.py` typo | Fixed: renamed to `__init__.py` |

---

## 11. Current Status

### Fully Built and Tested
- All 7 DB models + seed data (5 careers, 20 courses, 5 mentors)
- Auth (register/login with bcrypt)
- Gemini AI client with deterministic fallbacks
- 8-question diagnostic flow
- Matching engine (career + gaps + courses + mentor)
- All API endpoints
- Streamlit test console
- Frontend-backend integration via single-origin serving

### Not Done
1. `chat_messages` table unused
2. Gemini fallback not deliberately tested
3. Deployment to Alibaba Cloud pending
4. "Coming Soon" pages not built
5. No automated tests

---

## 12. Future Plans

### Short-term
- Deploy to Alibaba Cloud (Docker + ECS)
- Test Gemini fallback deliberately
- Polish UI and error handling
- Demo rehearsal

### Medium-term
- Build "Coming Soon" pages (Projects, Portfolio, Opportunities, Analytics, Certificates, Settings)
- Real chat integration with `chat_messages` table
- JWT authentication
- Admin dashboard for content management
- Email notifications

### Long-term
- Multi-language (Urdu + English)
- 20+ career paths
- Real course integration (Coursera/Udemy)
- Mentor marketplace with calendar
- Community features (forums, study groups)
- Mobile app (React Native)
- Advanced AI (conversational follow-ups, interview prep)

---
