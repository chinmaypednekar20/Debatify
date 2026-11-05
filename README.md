# Debatify

> Turn Indian Parliament debate transcripts into searchable, categorized summaries — and chat with them.

Debatify takes official Lok Sabha debate PDFs, splits them into individual questions, summarizes each one with a locally hosted LLM, and serves the results through a React dashboard. You can browse debates by date, explore topics by category, read an overall summary, and ask questions about a debate through a RAG-based chatbot.

All AI inference runs locally through [Ollama](https://ollama.com). No paid API keys are needed, and no data leaves your machine.

---

## Features

- **PDF → structured Q&A**: [Docling](https://github.com/DS4SD/docling) parses the transcript, and regex heuristics split it into individual parliamentary questions.
- **Per-question summaries**: Llama 3 (8B) pulls out who asked, the ministry, who answered, a question summary, an answer summary and a category for each question.
- **Debate-level overview**: a global summary of each session's debate.
- **Category normalization**: maps free-form LLM labels (e.g. *"Schooling"*, *"Primary Education"*) onto a fixed set of categories.
- **Debate chatbot (RAG)**: `all-MiniLM-L6-v2` embeddings and a FAISS index retrieve the most relevant transcript chunks, and Llama 3 answers using only those chunks.
- **JWT authentication**: signup and login with bcrypt-hashed passwords.

## Tech Stack

| Layer      | Technology                                                      |
| ---------- | --------------------------------------------------------------- |
| Frontend   | React 19, Vite 7, React Router 7, vanilla CSS                   |
| Backend    | FastAPI, SQLAlchemy, SQLite, python-jose (JWT), bcrypt          |
| AI / NLP   | Ollama + Llama 3 8B, sentence-transformers, FAISS, Docling      |

## Architecture

```
          ┌──────────────┐     ┌───────────────┐     ┌──────────────────┐
 PDF ───▶ │  extractor/  │ ──▶ │  summarizer/  │ ──▶ │ final_summary.json│
          │   (Docling)  │     │ (Llama 3 via  │     └────────┬─────────┘
          └──────────────┘     │    Ollama)    │              │ backend.json_to_db
                               └───────────────┘              ▼
                                                      ┌──────────────┐
 React UI  ◀──── REST /api ────  FastAPI backend ◀──▶ │ debatify.db  │
 (Vite)                          │                    │   (SQLite)   │
                                 └── chatbot/ ── FAISS + Ollama (RAG)
```

## Project Structure

```
Debatify/
├── backend/
│   ├── app.py            # FastAPI app: routes, schemas, category normalization
│   ├── auth.py           # JWT + bcrypt helpers
│   ├── database.py       # SQLAlchemy engine / session (SQLite)
│   ├── models.py         # User, Debate, Question models
│   ├── json_to_db.py     # Imports summary JSON into the database
│   ├── chatbot/
│   │   ├── config.py     # Embedding model, Ollama URL/model, retrieval params
│   │   ├── retriever.py  # Chunking + FAISS similarity search
│   │   └── llm.py        # Grounded answer generation via Ollama
│   └── requirements.txt
├── extractor/
│   └── extractor.py      # PDF → text → individual questions
├── summarizer/
│   └── summarizer.py     # Question summaries + global summary via Llama 3
├── outputs/
│   └── <DD-MM-YYYY>/     # Processed sessions (final_summary.json, questions.txt, extracted_text.txt)
├── frontend/
│   └── src/
│       ├── api.js        # API client
│       ├── components/   # Navbar
│       └── pages/        # Home, Debate, Categories, Overall Summary, Login, Signup
└── main.py               # Runs the full extraction + summarization pipeline
```

## Getting Started

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and npm
- **Ollama** with the Llama 3 model pulled:
  ```bash
  ollama pull llama3:8b
  ```

### 1. Clone the repository

```bash
git clone https://github.com/chinmaypednekar20/Debatify.git
cd Debatify
```

### 2. Set up the backend

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
pip install docling        # only needed to run the PDF extraction pipeline
```

### 3. Seed the database

The SQLite database is not committed. Build it from the processed sessions in `outputs/`:

```bash
python -m backend.json_to_db outputs/22-07-2025/final_summary.json outputs/23-07-2025/final_summary.json
```

`json_to_db` also reads `questions.txt` and `extracted_text.txt` from the same folder, so it can attach full question text and the full transcript to each record. Running it again on the same file updates the existing debate and does not create a duplicate.

### 4. Start the API

```bash
ollama serve                              # if Ollama isn't already running
uvicorn backend.app:app --reload --port 8000
```

Interactive API docs: <http://localhost:8000/docs>

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

## Processing a New Debate

1. Set `PDF_PATH` in [`extractor/extractor.py`](extractor/extractor.py) to the new transcript.
2. Run the pipeline from the project root:
   ```bash
   python main.py
   ```
   This writes the extracted text and the split questions, then produces `final_summary.json`. The summarizer can resume if it is interrupted.
3. Move the outputs into a dated session folder, named so they match what `json_to_db` expects:
   ```
   outputs/<DD-MM-YYYY>/
   ├── final_summary.json
   ├── questions.txt
   └── extracted_text.txt
   ```
4. Import it:
   ```bash
   python -m backend.json_to_db outputs/<DD-MM-YYYY>/final_summary.json
   ```

> Summarization takes a while: each question is a separate LLM call. On consumer hardware, expect several minutes per hundred questions.

## API Reference

All routes are prefixed with `/api`.

| Method | Endpoint                           | Description                                 |
| ------ | ---------------------------------- | ------------------------------------------- |
| POST   | `/auth/signup`                     | Create an account, returns a JWT            |
| POST   | `/auth/login`                      | Log in, returns a JWT                       |
| GET    | `/debates?date=YYYY-MM-DD`         | List debates, optionally filtered by date   |
| GET    | `/debates/{id}`                    | Debate detail with all questions            |
| GET    | `/dates`                           | Dates that have debates                     |
| GET    | `/categories`                      | Normalized categories with question counts  |
| GET    | `/categories/{name}/summary`       | All questions in a category                 |
| GET    | `/overall-summary`                 | Aggregate summary across debates            |
| POST   | `/summaries/{id}/chat`             | Ask the chatbot about a debate              |

## Configuration

| Setting                          | Location                                     | Default                              |
| -------------------------------- | -------------------------------------------- | ------------------------------------ |
| Ollama endpoint / model          | `backend/chatbot/config.py`, `summarizer/summarizer.py` | `http://localhost:11434`, `llama3:8b` |
| Embedding model                  | `backend/chatbot/config.py`                  | `all-MiniLM-L6-v2`                   |
| Retrieval (`TOP_K`, chunk size)  | `backend/chatbot/config.py`                  | `15`, `400` chars, `80` overlap      |
| JWT secret / expiry              | `backend/auth.py`                            | 24 h token lifetime                  |
| API base URL (frontend)          | `frontend/src/api.js`                        | `http://localhost:8000/api`          |
| Database file                    | `backend/database.py`                        | `./debatify.db`                      |

> ⚠️ **Before you deploy:** `SECRET_KEY` in `backend/auth.py` is hard-coded, and CORS allows all origins. Move the secret into an environment variable and limit `allow_origins` to your frontend's domain.

## Troubleshooting

- **Chatbot returns an error or times out**: check that Ollama is running (`ollama list`) and that `llama3:8b` is installed.
- **Dashboard is empty**: the database hasn't been seeded. Run step 3 again.
- **First chat request is slow**: the first request downloads the embedding model and loads it into memory. Later requests are faster.

## Roadmap

- [ ] Move configuration to environment variables (`.env`)
- [ ] Accept the PDF path as a CLI argument instead of hard-coding it
- [ ] Persist FAISS indexes per debate instead of rebuilding them in memory
- [ ] Support Rajya Sabha transcripts

## License

This project was built as an academic project. Add a license before using or distributing it.
