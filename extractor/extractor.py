import re
import json
from docling.document_converter import DocumentConverter


# ================= CONFIG =================

PDF_PATH = r"C:/semV/parliament-debate-summarizer/input/lsd_18_V_04-08-2025.pdf"

OUTPUT_TEXT = "extracted_text_v7.txt"
OUTPUT_QA = "questions_v7.txt"


# ================= EXTRACTION =================

def extract_text():

    print("📄 Extracting PDF using Docling...")

    converter = DocumentConverter()
    result = converter.convert(PDF_PATH)

    doc = result.document
    text = doc.export_to_text()

    with open(OUTPUT_TEXT, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ Extraction done")
    print(f"📁 Saved: {OUTPUT_TEXT}")
    print(f"📊 Characters: {len(text):,}")

    return text


# ================= VALIDATOR =================

def is_valid_question(block):

    good_signs = [
        "Will the Minister",
        "be pleased to state",
        "³ya",
        "क्या",
        "बताने क",
        "बताने की",
        "QUESTION"
    ]

    if not any(g.lower() in block.lower() for g in good_signs):
        return False

    bad_signs = [
        "STATEMENT State",
        "State/UT-wise",
        "STATEMENT:",
        "STATEMENT ",
        "STATEMENT-",
        "STATEMENT\n",
        "STATEMENT\n\n"
    ]

    if any(b in block for b in bad_signs):
        return False

    if len(block) < 250:
        return False

    return True


# ================= SPLITTER =================

def split_questions(text):

    print("✂ Detecting questions (FINAL + CONTEXT)...")

    markers = []

    # 1️⃣ Number + name (main pattern)
    START1 = re.compile(
        r'(?m)^(?:##\s*)?\*?\s*\d+\s*\.\s+.*'
    )

    # 2️⃣ QUESTION block
    START2 = re.compile(
        r'(?m)^=+\s*QUESTION\s+\d+',
        re.IGNORECASE
    )

    # 3️⃣ Hindi question start
    START3 = re.compile(
        r'(?m)^(?:##\s*)?\s*(³या|क्या).*',
        re.IGNORECASE
    )

    # 4️⃣ Inline number + name
    START4 = re.compile(
        r'(?m)^.*\b\d+\.\s*(?:SHRI|DR\.|PROF\.|SMT\.|®ी|डॉ\.|श्रीमती).*'
    )

    patterns = [START1, START2, START3, START4]

    for rx in patterns:
        for m in rx.finditer(text):
            markers.append(m.start())

    markers = sorted(set(markers))

    # Split text into lines
    lines = text.splitlines(keepends=True)

    # Map char pos → line number
    pos_map = []
    pos = 0
    for i, line in enumerate(lines):
        pos_map.append((pos, i))
        pos += len(line)

    def get_line_index(char_pos):
        for p, i in reversed(pos_map):
            if char_pos >= p:
                return i
        return 0


    questions = []


    for i in range(len(markers)):

        start_pos = markers[i]
        end_pos = markers[i+1] if i+1 < len(markers) else len(text)

        start_line = get_line_index(start_pos)
        end_line = get_line_index(end_pos)

        # ⬆️ Expand upward to capture names/headings
        while start_line > 0:

            prev = lines[start_line - 1].strip()

            # Stop at empty line
            if prev == "":
                break

            # Stop at previous question
            if re.match(r'(?:##\s*)?\*?\s*\d+\s*\.', prev):
                break

            start_line -= 1


        block = "".join(lines[start_line:end_line]).strip()


        if is_valid_question(block) and len(block) > 120:
            questions.append(block)


    print(f"📊 Total Questions Found → {len(questions)}")

    return questions


# ================= SAVE =================

def save_questions(questions):

    print("💾 Saving questions...")

    with open(OUTPUT_QA, "w", encoding="utf-8") as f:

        for i, q in enumerate(questions, 1):

            f.write("=" * 80 + "\n")
            f.write(f"QUESTION {i}\n")
            f.write("=" * 80 + "\n\n")

            f.write(q.strip())
            f.write("\n\n")

    print(f"✅ Saved: {OUTPUT_QA}")


# ================= JSON EXPORT =================

def save_questions_json(questions):

    print("💾 Saving questions as JSON...")

    data = []

    for i, q in enumerate(questions, 1):

        # Simple language detection
        if re.search(r"[अ-ह]", q):
            lang = "Hindi"
        elif re.search(r"[a-zA-Z]", q):
            lang = "English"
        else:
            lang = "Mixed"

        item = {
            "id": i,
            "language": lang,
            "length": len(q),
            "text": q.strip()
        }

        data.append(item)

    with open("questions_v6.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Saved: questions_v6.json")


# ================= MAIN =================

def main():

    print("\n🚀 Parliament Extractor v6 Starting...\n")

    text = extract_text()

    questions = split_questions(text)

    save_questions(questions)
    save_questions_json(questions)

    print("\n🎉 DONE!")
    print("👉 Ready for summarization / JSON export / AI processing")


# ================= RUN =================

if __name__ == "__main__":
    main()