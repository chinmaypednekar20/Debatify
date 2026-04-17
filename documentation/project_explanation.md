# Debatify: Technical & Functional Overview

This document provides a detailed breakdown of the Debatify project to help you present it to your teachers. It covers the "What, How, Where, and When" of the system.

## 1. Project Objective (The "What")
**Debatify** is an AI-powered platform designed to analyze, summarize, and categorize official Indian Parliamentary debate records. It transforms dense, complex PDF documents into an interactive dashboard, allowing users to quickly understand key issues, track ministry actions, and interact with the data via an AI chatbot.

---

## 2. Technology Stack (The "How" & "Where")

### Frontend (The User Interface)
- **Framework**: React 19 + Vite 7 (Modern, fast, and high-performance).
- **Styling**: Vanilla CSS (Custom-built for a clean, professional look).
- **Navigation**: React Router 7 (Handles multi-page routing smoothly).
- **Features**: Interactive charts, category-wise breakdown, and a real-time chatbot interface.

### Backend (The Logic Engine)
- **Framework**: FastAPI (Python) (Extremely fast, modern API framework).
- **Database**: SQLite with SQLAlchemy (A lightweight, reliable relational database).
- **Authentication**: JWT (JSON Web Tokens) (Ensures secure login and user sessions).

### AI & Data Processing
- **LLM Model**: **Llama 3 (8B)** running locally via **Ollama**.
- **Embedding Model**: `all-MiniLM-L6-v2` (Used for the chatbot's search/retrieval).
- **Extraction Tool**: **Docling** (Advanced document converter).

---

## 3. The Core Workflow (The "When" & "How")

### Stage 1: Extraction (Parsing the PDF)
- **When**: When a new debate PDF is added.
- **How**: The system uses **Docling** to convert the PDF into clean text. Unlike simple PDF parsers, Docling understands headers, tables, and logical sections.
- **Logic**: Specialized Python scripts ([extractor.py](file:///c:/semV/Debatify/extractor/extractor.py)) use Regex to identify the start of every question (e.g., looking for "Will the Minister" or question numbers).

### Stage 2: Intelligence (AI Summarization)
- **When**: After extraction.
- **How**: The [summarizer.py](file:///c:/semV/Debatify/summarizer/summarizer.py) script sends each question to the **Llama 3 (8B)** model.
- **Process**:
    1. **Question Summary**: AI extracts who asked it, which ministry answered, and a 150-word summary of the question and answer.
    2. **Categorization**: AI assigns a category (e.g., Education, Agriculture).
    3. **Global Summary**: Once all questions are processed, the AI reads all of them to create a single, high-level overview of the entire day's debate.

### Stage 3: Normalization (Category Cleanup)
- **Why**: AI might label something "Schooling" while another is "Primary Education."
- **How**: The backend uses a "Canonical Mapping" system. It merges similar labels into broad, consistent categories (like "Education") so the dashboard looks organized.

### Stage 4: Retrieval-Augmented Generation (The Chatbot)
- **Feature**: You don't just read; you ask.
- **Logic**: When you ask a question, the system searches the debate text for the most relevant parts (using embeddings) and gives those parts to **Llama 3**.
- **Result**: The AI answers based *only* on the actual debate facts, not making things up (this is called RAG - Retrieval Augmented Generation).

---

## 4. Key AI Models Used

### 1. Llama 3 (8B) - The "Brain"
- **Used for**: Summarizing individual questions, generating the global debate summary, and powering the chatbot.
- **Why**: It is one of the most powerful "small" models that can run locally. This ensures data privacy and zero cost per request (unlike OpenAI).

### 2. Docling - The "Eye"
- **Used for**: Understanding the PDF structure.
- **Why**: Parliamentary records have complex layouts. Docling ensures we don't lose context between pages or inside tables.

### 3. all-MiniLM-L6-v2 - The "Librarian"
- **Used for**: Powering the chatbot's search.
- **How**: It converts text into mathematical vectors (embeddings) so the system can find the "closest" answer to your question.

---

## 5. Summary of Features for Teachers
- **Automated Pipeline**: From PDF to Dashbroad without manual entry.
- **Semantic Search**: Chat with the document using natural language.
- **Data Visualization**: See which ministries are most active and which topics dominate the session.
- **Local AI**: No cloud costs, high speed, and complete control over the model.
