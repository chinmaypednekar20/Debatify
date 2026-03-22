"""
Convert one or more final_summary.json files into the Debatify SQLite database.

Usage:
    python -m backend.json_to_db summarizer/final_summary.json
    python -m backend.json_to_db path/to/file1.json path/to/file2.json
    python -m backend.json_to_db --dir summarizer/        # imports every .json in a folder
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal, Base
from backend.models import Debate, Question


def import_json_file(db, filepath: str) -> bool:
    """Import a single JSON file into the database. Returns True if imported."""
    abs_path = os.path.abspath(filepath)
    source_name = os.path.basename(abs_path)

    # Check if already imported
    existing = db.query(Debate).filter(Debate.source_file == source_name).first()
    if existing:
        print(f"  ⏭  Already imported: {source_name} (debate id={existing.id})")
        return False

    with open(abs_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        # New format: {"debate_summary": "...", "questions": [...]}
        questions_list = data.get("questions", [])
        global_summary_from_json = data.get("debate_summary")
    else:
        # Old format: [...]
        questions_list = data
        global_summary_from_json = None

    if not isinstance(questions_list, list):
        print(f"  ⚠  Skipping {source_name}: expected a JSON array of questions")
        return False

    # Derive a title & date from the filename or use defaults
    stem = Path(abs_path).stem  # e.g. "final_summary"
    title = stem.replace("_", " ").title()

    # ── Date resolution (3 strategies, in priority order) ──────────────────

    debate_date = None

    # Strategy 1: top-level "date" key in the JSON array wrapper
    # (supports {"date": "2025-07-21", "questions": [...]} format)
    # Here data is a list so we check for a top-level dict first
    # (not applicable since data is a list — skip)

    # Strategy 2: "date" key present in any question item
    for item in questions_list:
        raw_date = item.get("date") or item.get("debate_date")
        if raw_date:
            try:
                debate_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                title = f"Lok Sabha Debate — {debate_date.strftime('%A, %B')} {debate_date.day}, {debate_date.year}"
                break
            except ValueError:
                pass

    # Strategy 3: PDF filename in candidate input/ directories
    if not debate_date:
        candidate_dirs = [
            # Same level as the JSON file
            os.path.join(os.path.dirname(abs_path), "input"),
            # One level up
            os.path.join(os.path.dirname(os.path.dirname(abs_path)), "input"),
            # Project root (two levels up from json)
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(abs_path))),
                "input"
            ),
        ]
        for input_dir in candidate_dirs:
            if not os.path.isdir(input_dir):
                continue
            for pdf_name in sorted(os.listdir(input_dir)):
                if not pdf_name.lower().endswith(".pdf"):
                    continue
                try:
                    # Format: "Monday, July 21, 2025.pdf"
                    name_no_ext = pdf_name.rsplit(".", 1)[0]
                    if "," in name_no_ext:
                        # Drop weekday prefix before the first comma
                        weekday, rest = name_no_ext.split(",", 1)
                        date_str = rest.strip()  # "July 21, 2025"
                        debate_date = datetime.strptime(date_str, "%B %d, %Y").date()
                        title = f"Lok Sabha Debate — {name_no_ext}"
                        break
                except ValueError:
                    pass
            if debate_date:
                break

    # Fallback: today (warn the user)
    if not debate_date:
        debate_date = date.today()
        print(f"  ⚠  Could not extract debate date — using today ({debate_date}) for {source_name}")


    # Build/Use overall summary
    if global_summary_from_json:
        combined_summary = global_summary_from_json
    else:
        try:
            from backend.chatbot.llm import generate_answer
            context_parts = []
            for item in questions_list[:60]:
                s = item.get("summary", {})
                q_about = s.get("question_about", "Unknown")
                q_sum = s.get("question_summary", "")
                a_sum = s.get("answer_summary", "")
                context_parts.append(f"Topic: {q_about}\nQ: {q_sum}\nA: {a_sum}")
            
            context_str = "\n---\n".join(context_parts)
            prompt = (
                "You are an expert political analyst summarizing a parliamentary debate session for a senior panel. "
                "Write a highly professional, engaging, and insightful executive summary (3-4 paragraphs) of the key issues discussed in this session. "
                "Focus on the most significant policy matters, major concerns raised by MPs, and the government's key responses. "
                "Do NOT just list statistics or category counts. Do NOT say 'This debate saw X questions...'. "
                "Instead, weave the topics into a cohesive narrative that highlights the core political and administrative focus of the day. "
            )
            print("  Generating high-quality AI overall summary for Debate... (this may take a moment)")
            ai_sum = generate_answer(prompt, context_str)
            if ai_sum and len(ai_sum) > 50:
                combined_summary = ai_sum
            else:
                combined_summary = "Session summary unavailable."
        except Exception as e:
            print(f"  ⚠ Failed to generate AI summary: {e}")
            combined_summary = f"Summary generation failed: {e}"

    # Create debate
    debate = Debate(
        title=title,
        date=debate_date,
        source_file=source_name,
        overall_summary=combined_summary,
    )
    db.add(debate)
    db.flush()  # get debate.id

    # Insert questions
    for item in questions_list:
        s = item.get("summary", {})
        q = Question(
            debate_id=debate.id,
            original_id=item.get("id"),
            language=item.get("language"),
            has_table=item.get("has_table", False),
            word_count=item.get("word_count"),
            asked_by=s.get("asked_by", ""),
            ministry=s.get("ministry", ""),
            question_summary=s.get("question_summary", ""),
            answered_by=s.get("answered_by", ""),
            answer_summary=s.get("answer_summary", ""),
            overall_summary=s.get("overall_summary", ""),
            category=s.get("category", ""),
            question_about=s.get("question_about", ""),
            key_answer=s.get("key_answer", ""),
        )
        db.add(q)

    db.commit()
    print(f"  ✅ Imported {source_name}: {len(questions_list)} questions → debate id={debate.id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Import JSON summaries into Debatify DB")
    parser.add_argument("files", nargs="*", help="JSON file(s) to import")
    parser.add_argument("--dir", type=str, help="Import all .json files from a directory")
    args = parser.parse_args()

    # Collect file paths
    paths = list(args.files)
    if args.dir:
        for fname in sorted(os.listdir(args.dir)):
            if fname.endswith(".json"):
                paths.append(os.path.join(args.dir, fname))

    if not paths:
        print("No files specified. Use: python -m backend.json_to_db <file.json> [...]")
        sys.exit(1)

    # Create tables
    Base.metadata.create_all(bind=engine)
    print(f"\n📦 Debatify DB Importer — {len(paths)} file(s)\n")

    db = SessionLocal()
    try:
        imported = 0
        for p in paths:
            if not os.path.isfile(p):
                print(f"  ⚠  File not found: {p}")
                continue
            if import_json_file(db, p):
                imported += 1
        print(f"\n🎉 Done! {imported} file(s) imported.\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()
