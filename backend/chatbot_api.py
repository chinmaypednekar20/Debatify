"""
chatbot_api.py — FastAPI router for the summary-specific debate chatbot.

Endpoint:
    POST /api/summaries/{summary_id}/chat
    Body: { "question": "..." }
    Response: { "answer": "..." }
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_db
from .models import Debate, Question
from .chatbot.retriever import retrieve_chunks
from .chatbot.llm import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


def _build_summary_text(debate: Debate) -> str:
    """
    Build a rich summary text from a Debate and its Questions.
    This is the corpus the retriever will search within.
    """
    parts = []

    # Per-question summaries - treat each as a separate searchable block
    for i, q in enumerate(debate.questions, 1):
        block = [f"### Question {i} ###"]
        if q.asked_by:
            block.append(f"Member of Parliament: {q.asked_by}")
        if q.ministry:
            block.append(f"Ministry Involved: {q.ministry}")
        if q.category:
            block.append(f"Category: {q.category}")
        if q.question_about:
            block.append(f"Topic/Subject: {q.question_about}")
        if q.question_summary:
            block.append(f"Question Summary: {q.question_summary}")
        if q.answer_summary:
            block.append(f"Minister's Answer Summary: {q.answer_summary}")
        if q.overall_summary:
            block.append(f"Combined Q&A Summary: {q.overall_summary}")
        if q.key_answer:
            block.append(f"Key Takeaway/Answer: {q.key_answer}")
        
        if len(block) > 1:
            parts.append("\n".join(block))

    return "\n\n".join(parts)


@router.post("/api/summaries/{summary_id}/chat", response_model=ChatResponse)
def chat_with_summary(
    summary_id: int,
    req: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Accept a question and return an AI answer grounded only in the
    specified debate's summary content.
    """
    # 1. Fetch the debate
    debate = db.query(Debate).filter(Debate.id == summary_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    # 2. Build the full text corpus from this debate
    summary_text = _build_summary_text(debate)
    if not summary_text.strip():
        raise HTTPException(
            status_code=422,
            detail="This debate has no summary content to search.",
        )

    # 3. Retrieve relevant chunks from the detailed Q&A content
    chunks = retrieve_chunks(summary_text, req.question)
    
    # 4. Construct context. ALWAYS include the overall debate overview for high-level questions.
    context_parts = []
    if debate.overall_summary:
        context_parts.append(f"MAIN DEBATE OVERVIEW:\n{debate.overall_summary}")
    
    if chunks:
        context_parts.append("RELEVANT DETAILS FROM DEBATE TRANSACTIONS:")
        context_parts.extend(chunks)
    
    if not context_parts:
        return ChatResponse(
            answer="I'm sorry, I don't see any summary content for this debate to answer your question."
        )

    context = "\n\n---\n\n".join(context_parts)

    # 5. Generate the answer via Ollama
    answer = generate_answer(req.question, context)

    return ChatResponse(answer=answer)
