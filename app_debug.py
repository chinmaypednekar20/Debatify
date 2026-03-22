import sys
print("DEBUG: Starting app_debug.py")

from fastapi import FastAPI, Depends, HTTPException, status
print("DEBUG: FastAPI imported")

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import date as date_type
from collections import defaultdict
import re

print("DEBUG: Standard imports done")

from backend.database import engine, get_db, Base
print("DEBUG: database imported")

from backend.models import User, Debate, Question
print("DEBUG: models imported")

from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
print("DEBUG: auth imported")

from backend.chatbot_api import router as chatbot_router
print("DEBUG: chatbot_api imported")

# ─── Create tables ────────────────────────────────────────
print("DEBUG: Creating tables...")
Base.metadata.create_all(bind=engine)
print("DEBUG: Tables created")

# ─── App ──────────────────────────────────────────────────
app = FastAPI(title="Debatify API", version="1.0.0")
print("DEBUG: FastAPI app instance created")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────
app.include_router(chatbot_router)
print("DEBUG: Routers included")

@app.get("/api/health")
def health():
    return {"status": "ok"}

# ... (omitting other routes for brevity in this test)

if __name__ == "__main__":
    import uvicorn
    print("DEBUG: Running uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
