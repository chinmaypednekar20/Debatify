import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Debate, Question
from backend.chatbot.llm import generate_answer

def update_summaries():
    db = SessionLocal()
    debates = db.query(Debate).all()
    
    for debate in debates:
        print(f"Processing debate: {debate.title}")
        questions = db.query(Question).filter(Question.debate_id == debate.id).all()
        
        # Prepare context by taking the most detailed question summaries
        context_parts = []
        for q in questions[:60]: # limit to avoid context overflow
            part = f"Topic: {q.question_about or 'Unknown'}\n"
            if q.question_summary:
                part += f"Q: {q.question_summary}\n"
            if q.answer_summary:
                part += f"A: {q.answer_summary}\n"
            context_parts.append(part)
            
        context_str = "\n---\n".join(context_parts)
        
        prompt = (
            "You are an expert political analyst summarizing a parliamentary debate session for a senior panel. "
            "Write a highly professional, engaging, and insightful executive summary (3-4 paragraphs) of the key issues discussed in this session. "
            "Focus on the most significant policy matters, major concerns raised by MPs, and the government's key responses. "
            "Do NOT just list statistics or category counts. Do NOT say 'This debate saw X questions...'. "
            "Instead, weave the topics into a cohesive narrative that highlights the core political and administrative focus of the day. "
            "Structure it with a brief overview, the main thematic highlights, and the government's stance. "
            "Make it read like a premium intelligence briefing."
        )
        
        try:
            print("Generating new AI summary via Ollama. This will take a moment...")
            new_summary = generate_answer(prompt, context_str)
            if new_summary and len(new_summary) > 50:
                debate.overall_summary = new_summary
                db.commit()
                print("✅ Successfully updated database!")
            else:
                print("⚠ LLM returned an empty or extremely short response.")
        except Exception as e:
            print(f"❌ Failed: {e}")
            
    db.close()

if __name__ == "__main__":
    update_summaries()
