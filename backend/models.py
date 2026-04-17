from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Debate(Base):
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    date = Column(Date, nullable=False, index=True)
    source_file = Column(String(500), unique=True, nullable=False)
    overall_summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="debate", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    original_id = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True)
    has_table = Column(Boolean, default=False)
    word_count = Column(Integer, nullable=True)

    asked_by = Column(String(500), nullable=True)
    ministry = Column(String(500), nullable=True)
    question_summary = Column(Text, nullable=True)
    answered_by = Column(String(500), nullable=True)
    answer_summary = Column(Text, nullable=True)
    overall_summary = Column(Text, nullable=True)
    category = Column(String(200), nullable=True, index=True)
    question_about = Column(String(500), nullable=True)
    key_answer = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)

    debate = relationship("Debate", back_populates="questions")
