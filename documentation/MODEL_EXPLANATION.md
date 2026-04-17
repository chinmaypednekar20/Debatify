# Debatify — Model Explanation & Accuracy

## Overview

Debatify uses **two AI models** that work together to power its summarization and chatbot features. Both run **locally** via [Ollama](https://ollama.com/) and [SentenceTransformers](https://www.sbert.net/) — no external API keys are required.

---

## 1. Summarization Model — `llama3:8b`

### What it is
**LLaMA 3 (8 Billion Parameters)** is Meta's open-source large language model. It is served locally through [Ollama](https://ollama.com/), which provides a simple REST API at `http://localhost:11434`.

### Where it is used
The model is used in **three places**:

| Task | Where | Description |
|---|---|---|
| **Per-question summaries** | `summarizer/summarizer.py` | Reads raw parliamentary Q&A text and generates structured summaries (asked by, ministry, question summary, answer summary, category, etc.) for each question |
| **Debate-level overall summary** | `backend/json_to_db.py` | When a debate is imported into the database, the model generates a 3–4 paragraph executive-level summary of the entire session |
| **Overall session summary** | `backend/app.py` (`/api/overall-summary`) | Generates a live analytical overview paragraph across all debates in the database, using the top category breakdown as context |

### Configuration
```
Model:       llama3:8b
Temperature: 0.1   (low, for factual, consistent output)
Top-P:       0.9
Context:     8192 tokens
```
Configured in `backend/chatbot/config.py` and `summarizer/summarizer.py`.

### Accuracy & Quality Notes

The model runs in a **two-stage pipeline** for per-question summarization:

1. **Stage 1 — Text Summary**: The raw parliamentary transcript (often mixed English + Hindi) is sent to the LLM with a structured prompt asking it to extract: asked by, ministry, question summary, answer summary, overall summary, and category.
2. **Stage 2 — JSON Conversion**: A second prompt asks the model to convert the plain-text output into valid JSON with a fixed schema. A fallback retry handles any malformed JSON.

**Observed quality characteristics:**
- ✅ Factual extraction (MP names, ministry names, topics) is generally accurate for English-language questions
- ✅ Category assignment is consistent and the app applies a **post-processing normalization layer** (`_CATEGORY_MAP` in `backend/app.py`) that merges ~400 raw category variants into ~20 canonical categories
- ✅ Summary prose is professional and readable
- ⚠️ **Hindi / mixed-language questions** are harder for the model — summaries for these may be less detailed since Devanagari-heavy text is truncated or partially processed
- ⚠️ Questions with **large embedded tables** may have reduced accuracy as tables are pre-stripped before sending to the model (to avoid token overflow)
- ⚠️ Very long questions (>3,500 words) are **smart-trimmed** (head + tail preserved, middle cut) which may cause the model to miss some middle context

**No formal benchmark accuracy score** was measured — this is a domain-specific extraction task on Indian parliamentary proceedings, which no public benchmark covers. Quality was validated manually against the source PDF.

---

## 2. Embedding Model — `all-MiniLM-L6-v2`

### What it is
**`all-MiniLM-L6-v2`** is a lightweight sentence embedding model from the [SentenceTransformers](https://www.sbert.net/) library. It converts text into dense 384-dimensional vectors for semantic similarity search.

### Where it is used
The embedding model powers the **chatbot's RAG (Retrieval-Augmented Generation)** pipeline in `backend/chatbot/retriever.py`.

When a user asks a question about a debate:
1. The full debate Q&A content is **chunked** into overlapping text segments (400 characters, 80-char overlap)
2. Each chunk is **embedded** into a vector using `all-MiniLM-L6-v2`
3. A temporary **in-memory FAISS index** is built from these chunk embeddings
4. The user's question is also embedded, and the **top 15 most semantically similar chunks** are retrieved
5. These chunks (plus the overall debate summary) are passed as context to `llama3:8b` for answer generation

### Why this model?
- Very fast — loads in ~1–2 seconds and produces embeddings in milliseconds
- Small footprint — runs entirely on CPU without a GPU
- Strong semantic similarity performance for English text (evaluated on STS benchmarks: ~82 Spearman correlation on STS-B)
- Well-suited for short-to-medium length parliamentary summaries

### Configuration
```
Model:        all-MiniLM-L6-v2
Chunk size:   400 characters
Chunk overlap: 80 characters
Top-K chunks:  15
```

---

## Pipeline Summary

```
PDF (input/)
    ↓
extractor/extractor.py  [Docling — PDF → text + question splitting]
    ↓
summarizer/summarizer.py  [LLaMA 3:8b — structured question summaries]
    ↓
summarizer/final_summary.json
    ↓
backend/json_to_db.py  [LLaMA 3:8b — overall debate summary + DB import]
    ↓
debatify.db (SQLite)
    ↓
backend/app.py (FastAPI)  ←→  frontend/ (React + Vite)
    ↓
/api/summaries/{id}/chat  [all-MiniLM-L6-v2 + LLaMA 3:8b — chatbot answers]
```
