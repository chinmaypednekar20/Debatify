import json
import requests
import time
import re
import os


# ================= CONFIG =================

INPUT_FILE = "../questions_v6.txt"
OUTPUT_FILE = "final_summary.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"   # High-quality model for summaries

TIMEOUT = 600
RETRIES = 3
DELAY = 2

MAX_WORDS = 3500   # Safe for Mistral 7B


# ================= JSON CLEANER =================

def clean_json(text):

    if not text:
        return None

    text = text.strip()

    # Remove markdown
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"```json|```", "", text, flags=re.I)

    # Try direct parse
    try:
        return json.loads(text)
    except:
        pass

    # Extract balanced JSON
    start = -1
    stack = 0

    for i, ch in enumerate(text):

        if ch == "{":
            if stack == 0:
                start = i
            stack += 1

        elif ch == "}":
            stack -= 1

            if stack == 0 and start != -1:

                candidate = text[start:i+1]

                try:
                    return json.loads(candidate)
                except:
                    pass

    return None


# ================= SCHEMA VALIDATION =================

def validate_schema(data):

    keys = [
        "asked_by",
        "ministry",
        "question_about",
        "answered_by",
        "key_answer",
        "category"
    ]

    if not isinstance(data, dict):
        return None

    for k in keys:
        if k not in data or data[k] is None:
            data[k] = ""

    return data


# ================= OLLAMA =================

def run_ollama(prompt, primed=False):

    payload = {
    "model": MODEL,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.1,        # Slight flexibility (better wording)
        "top_p": 0.9,              # Balanced sampling
        "num_ctx": 8192,           # Large context
        "num_predict": 999,        # Limit output size
        "repeat_penalty": 1.15,    # Reduce loops
        "stop": ["Text:", "###"]   # Prevent extra output
    }
}

    for _ in range(RETRIES):

        try:

            r = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=TIMEOUT
            )

            if r.status_code == 200:
                resp = r.json().get("response", "")
                if primed:
                    return "Debate Overview:\n" + resp
                return resp

            print("⚠ Bad status:", r.status_code)

        except Exception as e:
            print("⚠ Ollama error:", e)

        time.sleep(DELAY)

    return None


# ================= LOAD QUESTIONS =================

def load_questions():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = f.read()

    blocks = re.split(r"\n={20,}\n", data)

    questions = []

    for b in blocks:

        b = b.strip()

        if len(b) > 400:
            questions.append(b)

    print(f"📊 Loaded {len(questions)} questions")

    return questions


# ================= SMART TRIM =================

def smart_trim(text, max_words=3000, head_ratio=0.6):
    """
    Keeps important beginning and ending parts of long text.
    Trims middle if too long.
    """

    if not text:
        return ""

    words = text.split()
    total = len(words)

    # If already within limit
    if total <= max_words:
        return text.strip()

    # Calculate split
    head_words = int(max_words * head_ratio)
    tail_words = max_words - head_words

    head = words[:head_words]
    tail = words[-tail_words:]

    return " ".join(head + ["[TRUNCATED]"] + tail)


# ================= PREPROCESS =================

def preprocess_text(text):

    # Remove tables
    text = re.sub(r"\|.*?\|", " ", text, flags=re.S)

    # Remove debate noise
    text = re.sub(r"माननीय अÅय±.*?\n", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    # Trim safely
    text = smart_trim(text)

    return text


# ================= PROMPTS =================

def build_summary_prompt(text):

    cleaned = preprocess_text(text)

    return f"""
You are reading an official Indian Parliament Question & Answer record.

Task:
Extract ONLY factual information from the text and summarize clearly.

Write in simple, neutral English.

Return in EXACTLY this format:

Asked By:
Ministry:
Answered By:
Question Summary:
Answer Summary:
Overall Summary:
Category:

Instructions:

1. Question Summary:
   - Summarize what the MP is asking.
   - Length: 40 to 150 words.
   - Include purpose, background, and key demands.

2. Answer Summary:
   - Summarize the Minister’s response.
   - Length: 40 to 150 words.
   - Include data, actions taken, policies, and promises.

3. Overall Summary:
   - Combine the main points of both question and answer.
   - Length: 60 to 300 words.
   - Should give a complete understanding to a general reader.

4. Use "" (double quotes) if any field is missing.
5. Do NOT invent facts.
6. Do NOT use markdown.
7. Do NOT add explanations.

Text:
{cleaned}
"""


def build_json_prompt(summary_text):

    return f"""
Convert the following structured text into VALID JSON.

Rules:
- Output JSON only.
- Use double quotes.
- No comments.
- No extra text.

Schema:

{{
  "asked_by": "",
  "ministry": "",
  "question_summary": "",
  "answered_by": "",
  "answer_summary": "",
  "overall_summary": "",
  "category": ""
}}

Text:
{summary_text}
"""


def build_global_summary_prompt(question_summaries):
    return f"""
You are given multiple parliamentary questions.

Generate a concise summary based ONLY on these questions.

RULES:
- Do NOT mention numbers or statistics
- Do NOT write like a report
- Do NOT use generic phrases like "the government has taken steps"
- Focus only on key issues discussed
- Do NOT start with introductory/first-person phrases like "As I analyzed the parliamentary debate session", "it became clear that", "my analysis shows", or "it is clear that". Start directly with the summary of key issues (insights, not personal opinions).

STYLE:
- 1 paragraph
- Clear and compact
- No fluff
- Completely objective and impersonal tone

OUTPUT:
Only the summary text.~

Questions:
{question_summaries}
"""


# ================= SAVE =================

def save(results):

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("💾 Saved:", OUTPUT_FILE)


# ================= MAIN =================

def main():

    print("\n🚀 Parliament Summarizer v11 Starting...\n")

    questions = load_questions()

    results = []


    # Resume support
    if os.path.exists(OUTPUT_FILE):

        try:

            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                results = json.load(f)

            print(f"📂 Resuming from {len(results)} items")

        except:
            print("⚠ Corrupt JSON — starting fresh")
            results = []


    for i in range(len(results), len(questions)):

        print(f"\n⚡ Processing {i+1}/{len(questions)}")

        q = questions[i]


        # ---------- STAGE 1: SUMMARY ----------

        summary_prompt = build_summary_prompt(q)

        summary_text = run_ollama(summary_prompt)

        if not summary_text:
            print("❌ Summary failed — skipped")
            continue


        # ---------- STAGE 2: JSON ----------

        json_prompt = build_json_prompt(summary_text)

        json_output = run_ollama(json_prompt)

        data = clean_json(json_output)


        # Retry formatter
        if not data:

            print("⚠ JSON format failed — retrying...")

            retry = json_prompt + "\nREMEMBER: OUTPUT JSON ONLY."

            json_output = run_ollama(retry)

            data = clean_json(json_output)


        if not data:
            print("❌ JSON failed twice — skipped")
            continue


        data = validate_schema(data)

        wc = len(preprocess_text(q).split())


        item = {
            "id": i + 1,
            "language": "mixed",
            "has_table": "|" in q,
            "word_count": wc,
            "summary": data
        }


        results.append(item)

        save(results)

        time.sleep(DELAY)

    # ---------- STAGE 3: GLOBAL SUMMARY ----------
    print("\n🌍 Generating Global Debate Summary...")
    
    all_summaries = [r["summary"]["overall_summary"] for r in results if r["summary"].get("overall_summary")]
    if all_summaries:
        combined_text = "\n\n".join(all_summaries)
        # Trim if too long for the context window
        combined_text = smart_trim(combined_text, max_words=6000)
        
        global_prompt = build_global_summary_prompt(combined_text)
        global_summary = run_ollama(global_prompt, primed=True)
        
        if global_summary:
            # We'll save it as a special metadata item or in a separate file
            # For now, let's wrap results in a dict if we want to store global summary
            output_data = {
                "debate_summary": global_summary,
                "questions": results
            }
            with open("debate_with_summary.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print("✅ Global summary generated and saved to debate_with_summary.json")
        else:
            print("❌ Global summary generation failed")


    print("\n🎉 ALL DONE!")
    print(f"📦 Total Summarized: {len(results)}")
    print("👉 Ready for DB / API / Dashboard")



# ================= RUN =================

if __name__ == "__main__":
    main()