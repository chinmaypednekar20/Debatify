from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import date as date_type
from collections import defaultdict
import re

from .database import engine, get_db, Base
from .models import User, Debate, Question
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from .chatbot_api import router as chatbot_router

# ─── Create tables ────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── App ──────────────────────────────────────────────────
app = FastAPI(title="Debatify API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────
app.include_router(chatbot_router)


# ═══════════════════════════════════════════════════════════
#  SCHEMAS
# ═══════════════════════════════════════════════════════════

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class QuestionOut(BaseModel):
    id: int
    original_id: Optional[int]
    language: Optional[str]
    has_table: bool
    word_count: Optional[int]
    asked_by: Optional[str]
    ministry: Optional[str]
    question_summary: Optional[str]
    answered_by: Optional[str]
    answer_summary: Optional[str]
    overall_summary: Optional[str]
    category: Optional[str]
    question_about: Optional[str]
    key_answer: Optional[str]

    class Config:
        from_attributes = True

class DebateListItem(BaseModel):
    id: int
    title: str
    date: date_type
    overall_summary: Optional[str]
    question_count: int

class DebateDetail(BaseModel):
    id: int
    title: str
    date: date_type
    overall_summary: Optional[str]
    questions: List[QuestionOut]

    class Config:
        from_attributes = True

class CategoryStat(BaseModel):
    category: str
    count: int

class CategorySummary(BaseModel):
    category: str
    count: int
    questions: List[dict]
    combined_summary: str


# ═══════════════════════════════════════════════════════════
#  CATEGORY NORMALIZATION
# ═══════════════════════════════════════════════════════════

# Canonical mapping — merges synonyms into broad 1-2 word categories
_CATEGORY_MAP = {
    # Education
    "education": "Education",
    "literacy": "Education",
    "schooling": "Education",
    "education and employment": "Education",
    "higher education": "Education",
    "primary education": "Education",
    "school education": "Education",
    "university": "Education",
    "colleges": "Education",
    "educational institutions": "Education",
    "teachers": "Education",
    "students": "Education",
    "mid day meal": "Education",

    # Employment
    "employment": "Employment",
    "jobs": "Employment",
    "unemployment": "Employment",
    "labour": "Employment",
    "labour and employment": "Employment",
    "workforce": "Employment",
    "job creation": "Employment",
    "workers": "Employment",
    "migrant workers": "Employment",
    "wage": "Employment",
    "pension": "Employment",
    "provident fund": "Employment",
    "epfo": "Employment",
    "esic": "Employment",

    # Skill Development
    "skill development": "Skill Development",
    "skills": "Skill Development",
    "entrepreneurship": "Skill Development",
    "skill development and entrepreneurship": "Skill Development",
    "vocational training": "Skill Development",
    "startup": "Skill Development",
    "msme": "Skill Development",

    # Environment
    "environment": "Environment",
    "environmental conservation": "Environment",
    "environmental protection": "Environment",
    "climate change": "Environment",
    "pollution": "Environment",
    "culture and environment": "Environment",
    "ecology": "Environment",
    "forest": "Environment",
    "wildlife": "Environment",
    "biodiversity": "Environment",
    "air pollution": "Environment",
    "water pollution": "Environment",
    "waste management": "Environment",
    "plastic waste": "Environment",
    "wetlands": "Environment",
    "coastal regulation zone": "Environment",

    # Finance
    "finance": "Finance",
    "economy": "Finance",
    "economy and finance": "Finance",
    "economic development": "Finance",
    "taxation": "Finance",
    "budget": "Finance",
    "fiscal policy": "Finance",
    "banking": "Finance",
    "gst": "Finance",
    "demonetisation": "Finance",
    "inflation": "Finance",
    "foreign direct investment": "Finance",
    "fdi": "Finance",
    "public sector banks": "Finance",
    "loan": "Finance",
    "debt": "Finance",
    "insurance": "Finance",
    "stock market": "Finance",
    "revenue": "Finance",
    "expenditure": "Finance",
    "financial inclusion": "Finance",
    "digital payments": "Finance",
    "currency": "Finance",
    "reserve bank of india": "Finance",
    "rbi": "Finance",

    # Health
    "health": "Health",
    "healthcare": "Health",
    "public health": "Health",
    "medicine": "Health",
    "medical": "Health",
    "sanitation": "Health",
    "nutrition": "Health",
    "health and family welfare": "Health",
    "ayushman bharat": "Health",
    "hospitals": "Health",
    "doctors": "Health",
    "nurses": "Health",
    "vaccination": "Health",
    "disease": "Health",
    "covid-19": "Health",
    "malaria": "Health",
    "tuberculosis": "Health",
    "cancer": "Health",
    "mental health": "Health",
    "drugs": "Health",
    "pharmaceuticals": "Health",
    "medical devices": "Health",
    "food safety": "Health",
    "drinking water": "Health",
    "swachh bharat": "Health",

    # Agriculture
    "agriculture": "Agriculture",
    "farming": "Agriculture",
    "rural development": "Agriculture",
    "crop": "Agriculture",
    "irrigation": "Agriculture",
    "food security": "Agriculture",
    "farmers": "Agriculture",
    "agri": "Agriculture",
    "horticulture": "Agriculture",
    "fisheries": "Agriculture",
    "animal husbandry": "Agriculture",
    "fertilizers": "Agriculture",
    "seeds": "Agriculture",
    "minimum support price": "Agriculture",
    "msp": "Agriculture",
    "farm loans": "Agriculture",
    "agricultural credit": "Agriculture",
    "crop insurance": "Agriculture",
    "pradhan mantri fasal bima yojana": "Agriculture",
    "pmfby": "Agriculture",
    "mandis": "Agriculture",
    "agricultural markets": "Agriculture",
    "food processing": "Agriculture",
    "storage": "Agriculture",
    "cold chain": "Agriculture",

    # Infrastructure
    "infrastructure": "Infrastructure",
    "roads": "Infrastructure",
    "transport": "Infrastructure",
    "transportation": "Infrastructure",
    "railways": "Infrastructure",
    "urban development": "Infrastructure",
    "housing": "Infrastructure",
    "construction": "Infrastructure",
    "ports": "Infrastructure",
    "airports": "Infrastructure",
    "highways": "Infrastructure",
    "metro": "Infrastructure",
    "smart cities": "Infrastructure",
    "jawaharlal nehru national urban renewal mission": "Infrastructure",
    "jnnurm": "Infrastructure",
    "amrut": "Infrastructure",
    "pradhan mantri awas yojana": "Infrastructure",
    "pmay": "Infrastructure",
    "water supply": "Infrastructure",
    "sewerage": "Infrastructure",
    "bridges": "Infrastructure",
    "dams": "Infrastructure",
    "logistics": "Infrastructure",

    # Defence
    "defence": "Defence",
    "defense": "Defence",
    "armed forces": "Defence",
    "military": "Defence",
    "national security": "Defence",
    "border security": "Defence",
    "army": "Defence",
    "navy": "Defence",
    "air force": "Defence",
    "paramilitary": "Defence",
    "coast guard": "Defence",
    "weapons": "Defence",
    "ammunition": "Defence",
    "defence production": "Defence",
    "defence procurement": "Defence",
    "ex-servicemen": "Defence",
    "veterans": "Defence",
    "pensioners": "Defence",
    "one rank one pension": "Defence",
    "orop": "Defence",

    # Technology
    "technology": "Technology",
    "information technology": "Technology",
    "it": "Technology",
    "digital india": "Technology",
    "science": "Technology",
    "science and technology": "Technology",
    "innovation": "Technology",
    "research": "Technology",
    "electronics": "Technology",
    "space": "Technology",
    "biotechnology": "Technology",
    "nanotechnology": "Technology",
    "artificial intelligence": "Technology",
    "ai": "Technology",
    "cyber security": "Technology",
    "internet": "Technology",
    "software": "Technology",
    "hardware": "Technology",
    "e-governance": "Technology",
    "data": "Technology",
    "gis": "Technology",

    # Culture
    "culture": "Culture",
    "cultural affairs": "Culture",
    "cultural heritage": "Culture",
    "cultural diversity": "Culture",
    "arts": "Culture",
    "heritage": "Culture",
    "museums": "Culture",
    "monuments": "Culture",
    "festivals": "Culture",
    "languages": "Culture",
    "books": "Culture",
    "libraries": "Culture",
    "archives": "Culture",
    "performing arts": "Culture",
    "visual arts": "Culture",

    # Sports
    "sports": "Sports",
    "sports infrastructure": "Sports",
    "youth affairs": "Sports",
    "games": "Sports",
    "olympics": "Sports",
    "commonwealth games": "Sports",
    "asian games": "Sports",
    "fit india": "Sports",
    " Khelo India": "Sports",

    # Tourism
    "tourism": "Tourism",
    "travel": "Tourism",
    "hospitality": "Tourism",
    "pilgrimage": "Tourism",
    "ecotourism": "Tourism",
    "adventure tourism": "Tourism",
    "medical tourism": "Tourism",

    # Communications
    "communications": "Communications",
    "telecom": "Communications",
    "telecommunications": "Communications",
    "broadcasting": "Communications",
    "media": "Communications",
    "post office": "Communications",
    "postal services": "Communications",
    "internet connectivity": "Communications",
    "mobile services": "Communications",
    "spectrum": "Communications",

    # Corporate Affairs
    "corporate affairs": "Corporate Affairs",
    "companies": "Corporate Affairs",
    "business": "Corporate Affairs",
    "corporate social responsibility": "Corporate Affairs",
    "csr": "Corporate Affairs",
    "company law": "Corporate Affairs",
    "insolvency": "Corporate Affairs",
    "bankruptcy": "Corporate Affairs",

    # Water Resources
    "water": "Water Resources",
    "water resources": "Water Resources",
    "drinking water": "Water Resources",
    "rivers": "Water Resources",
    "jal shakti": "Water Resources",
    "groundwater": "Water Resources",
    "inter-linking of rivers": "Water Resources",
    "water conservation": "Water Resources",
    "irrigation projects": "Water Resources",

    # Energy
    "energy": "Energy",
    "power": "Energy",
    "electricity": "Energy",
    "renewable energy": "Energy",
    "solar": "Energy",
    "coal": "Energy",
    "petroleum": "Energy",
    "oil and gas": "Energy",
    "nuclear energy": "Energy",
    "hydro power": "Energy",
    "wind energy": "Energy",
    "power generation": "Energy",
    "power distribution": "Energy",
    "power transmission": "Energy",
    "energy efficiency": "Energy",
    "lpg": "Energy",
    "natural gas": "Energy",

    # Social Welfare
    "social welfare": "Social Welfare",
    "welfare": "Social Welfare",
    "poverty": "Social Welfare",
    "women and child development": "Social Welfare",
    "women empowerment": "Social Welfare",
    "child welfare": "Social Welfare",
    "minorities": "Social Welfare",
    "scheduled castes": "Social Welfare",
    "scheduled tribes": "Social Welfare",
    "tribals": "Social Welfare",
    "persons with disabilities": "Social Welfare",
    "legal": "Law & Justice",
    "police": "Law & Justice",
    "crime": "Law & Justice",
    "law and order": "Law & Justice",

    # Foreign Affairs
    "foreign affairs": "Foreign Affairs",
    "external affairs": "Foreign Affairs",
    "diplomacy": "Foreign Affairs",
    "international relations": "Foreign Affairs",
}

# Keyword fallback — used when the raw category is not in the exact-match map.
# Ordered by priority: earlier patterns win.
_FALLBACK_KEYWORDS = [
    ("education", "Education"),
    ("skill", "Skill Development"),
    ("employ", "Employment"),
    ("labour", "Employment"),
    ("environ", "Environment"),
    ("forest", "Environment"),
    ("climate", "Environment"),
    ("wildlife", "Environment"),
    ("conservation", "Environment"),
    ("sport", "Sports"),
    ("youth", "Sports"),
    ("tour", "Tourism"),
    ("culture", "Culture"),
    ("heritage", "Culture"),
    ("financ", "Finance"),
    ("econom", "Finance"),
    ("health", "Health"),
    ("agri", "Agriculture"),
    ("farm", "Agriculture"),
    ("infra", "Infrastructure"),
    ("urban", "Infrastructure"),
    ("transport", "Infrastructure"),
    ("rail", "Infrastructure"),
    ("ship", "Infrastructure"),
    ("port", "Infrastructure"),
    ("road", "Infrastructure"),
    ("housing", "Infrastructure"),
    ("defence", "Defence"),
    ("defense", "Defence"),
    ("military", "Defence"),
    ("security", "Defence"),
    ("technol", "Technology"),
    ("digital", "Technology"),
    ("science", "Technology"),
    ("communic", "Communications"),
    ("telecom", "Communications"),
    ("corporate", "Corporate Affairs"),
    ("water", "Water Resources"),
    ("energy", "Energy"),
    ("power", "Energy"),
    ("solar", "Energy"),
    ("welfare", "Social Welfare"),
    ("women", "Social Welfare"),
    ("tribal", "Social Welfare"),
    ("panchayat", "Social Welfare"),
    ("gig worker", "Social Welfare"),
    ("law", "Law & Justice"),
    ("justice", "Law & Justice"),
    ("foreign", "Foreign Affairs"),
    ("international", "Foreign Affairs"),
    ("cooperat", "Foreign Affairs"),
]


def normalize_category(raw: str) -> str:
    """Normalize a category string — lowercase, deduplicate, merge synonyms."""
    if not raw or not raw.strip():
        return "Uncategorized"

    # If the string is predominantly non-ASCII (e.g. Hindi/Devanagari), try to
    # extract any recognisable English keyword first; otherwise bin it.
    non_ascii = sum(1 for c in raw if ord(c) > 127)
    if non_ascii > len(raw) * 0.4:
        lower = raw.lower()
        # Check for known English words hidden inside mixed strings
        if "tour" in lower or "paryatan" in lower:
            return "Tourism"
        if "sanrakshan" in lower or "conservation" in lower or "wildlife" in lower:
            return "Environment"
        if "shiksha" in lower or "education" in lower:
            return "Education"
        # Unrecognisable Hindi category — skip it
        return "Uncategorized"

    key = raw.strip().lower()

    # 1. Exact map lookup
    if key in _CATEGORY_MAP:
        return _CATEGORY_MAP[key]

    # 2. Keyword substring fallback (handles verbose/compound AI-generated strings)
    for kw, canonical in _FALLBACK_KEYWORDS:
        if kw in key:
            return canonical

    # 3. Last resort: clean title case
    return raw.strip().title()


# ═══════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════

@app.post("/api/auth/signup", response_model=TokenResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, username=user.username)


@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, username=user.username)


# ═══════════════════════════════════════════════════════════
#  DEBATE ROUTES
# ═══════════════════════════════════════════════════════════

@app.get("/api/debates", response_model=List[DebateListItem])
def list_debates(date: Optional[date_type] = None, db: Session = Depends(get_db)):
    query = db.query(Debate)
    if date:
        query = query.filter(Debate.date == date)
    query = query.order_by(Debate.date.desc())
    debates = query.all()

    result = []
    for d in debates:
        result.append(DebateListItem(
            id=d.id,
            title=d.title,
            date=d.date,
            overall_summary=d.overall_summary,
            question_count=len(d.questions),
        ))
    return result


@app.get("/api/debates/{debate_id}", response_model=DebateDetail)
def get_debate(debate_id: int, db: Session = Depends(get_db)):
    debate = db.query(Debate).filter(Debate.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return debate


@app.get("/api/dates")
def get_dates(db: Session = Depends(get_db)):
    """Return all unique dates that have debates — for calendar dots."""
    rows = db.query(Debate.date).distinct().all()
    return [r[0].isoformat() for r in rows]


# ═══════════════════════════════════════════════════════════
#  CATEGORY ROUTES
# ═══════════════════════════════════════════════════════════

def _build_normalized_categories(db: Session):
    """Query all questions and group by normalized category."""
    all_qs = (
        db.query(Question)
        .filter(Question.category != "", Question.category.isnot(None))
        .all()
    )
    grouped: Dict[str, list] = defaultdict(list)
    for q in all_qs:
        norm = normalize_category(q.category)
        grouped[norm].append(q)
    return grouped


@app.get("/api/categories", response_model=List[CategoryStat])
def list_categories(db: Session = Depends(get_db)):
    grouped = _build_normalized_categories(db)
    result = [
        CategoryStat(category=cat, count=len(qs))
        for cat, qs in grouped.items()
    ]
    result.sort(key=lambda x: -x.count)
    return result


@app.get("/api/categories/{name}/summary", response_model=CategorySummary)
def get_category_summary(name: str, db: Session = Depends(get_db)):
    grouped = _build_normalized_categories(db)
    questions = grouped.get(name, [])
    if not questions:
        raise HTTPException(status_code=404, detail="Category not found")

    # Build per-question detail list
    question_details = []
    for q in questions:
        question_details.append({
            "id": q.id,
            "asked_by": q.asked_by,
            "ministry": q.ministry,
            "question_summary": q.question_summary,
            "answer_summary": q.answer_summary,
            "overall_summary": q.overall_summary,
            "question_about": q.question_about,
        })

    # Build a proper combined summary
    ministries = list({q.ministry for q in questions if q.ministry})
    topics = [q.question_about or q.question_summary or "" for q in questions]
    topics = [t for t in topics if t]

    parts = []
    parts.append(f"This category covers {len(questions)} question(s) raised in Parliament.")
    if ministries:
        parts.append(f"Ministries addressed: {', '.join(ministries[:5])}.")
    if len(topics) <= 5:
        parts.append("Key topics: " + "; ".join(topics) + ".")
    else:
        parts.append("Key topics include: " + "; ".join(topics[:5]) + f"; and {len(topics)-5} more.")

    return CategorySummary(
        category=name,
        count=len(questions),
        questions=question_details,
        combined_summary=" ".join(parts),
    )


# ═══════════════════════════════════════════════════════════
#  OVERALL SUMMARY
# ═══════════════════════════════════════════════════════════

@app.get("/api/overall-summary")
def overall_summary(db: Session = Depends(get_db)):
    questions = db.query(Question).all()
    grouped = _build_normalized_categories(db)

    # Top ministries
    ministry_counts: Dict[str, int] = defaultdict(int)
    for q in questions:
        if q.ministry:
            ministry_counts[q.ministry] += 1
    top_ministries = sorted(ministry_counts.items(), key=lambda x: -x[1])[:8]

    # Category breakdown with proper 1-line summaries
    category_breakdown = []
    for cat, qs in sorted(grouped.items(), key=lambda x: -len(x[1])):
        topics = [q.question_about or q.question_summary or "" for q in qs]
        topics = [t for t in topics if t][:3]
        if topics:
            cat_summary = "Key topics: " + "; ".join(topics)
            if len(qs) > 3:
                cat_summary += f" (and {len(qs)-3} more)"
        else:
            cat_summary = f"{len(qs)} question(s) in this category."
        category_breakdown.append({
            "category": cat,
            "count": len(qs),
            "summary": cat_summary,
        })

    # Build proper overall summary
    total_q = len(questions)
    total_cats = len(grouped)
    total_ministries = len(ministry_counts)

    top_cat = category_breakdown[0] if category_breakdown else None
    top_min = top_ministries[0] if top_ministries else None

    try:
        from .chatbot.llm import generate_answer
        
        # Build a concise context to send to LLM (using top categories to avoid massive context)
        context_lines = []
        for cat in category_breakdown[:10]:
            context_lines.append(f"Category: {cat['category']} ({cat['count']} questions)")
            context_lines.append(cat['summary'])
        
        context_str = "\n".join(context_lines)
        
        prompt = (
            f"Write a concise, high-quality analytical summary (3-4 sentences) of this parliamentary session. "
            f"There were {total_q} questions across {total_cats} categories, involving {total_ministries} ministries. "
            f"Focus on the major themes and issues discussed, integrating the facts smoothly rather than just listing numbers. "
            f"Do not use templates like 'This session saw X questions...'. Make it sound professional and insightful."
        )
        
        ai_summary = generate_answer(prompt, context_str)
        final_summary_text = ai_summary
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        final_summary_text = f"AI Error: {e}"

    return {
        "total_questions": total_q,
        "total_categories": total_cats,
        "total_ministries": total_ministries,
        "combined_summary": final_summary_text,
        "top_ministries": [
            {"name": m[0], "count": m[1]} for m in top_ministries
        ],
        "category_breakdown": category_breakdown,
    }
