# Debatify — 6-Week Project Log

This log documents the development of **Debatify**, an AI-powered parliamentary debate summarization and interactive chatbot platform, structured for formal project reporting.

---

## Weekly Work Log

### Week 1: Project Foundations & Selection
- **Status**: Completed
- **Objectives**: Finalize project topic, perform feasibility research on datasets.
- **Key Tasks**:
    - Brainstormed 3 project ideas:
        1. AI Traffic Management System.
        2. Car Marketplace Price Predictor (VehPro).
        3. **Parliamentary Debate Summarizer (Debatify)**.
    - Selected **Debatify** due to its high social utility and complex NLP challenges.
    - Researched LOK SABHA and RAJYA SABHA PDF transcript structures.
    - Literature review of current LLM-based summarization methods (Abstractive vs. Extractive).

### Week 2: Requirements Analysis & System Design
- **Status**: Completed
- **Objectives**: Define system architecture and select the technology stack.
- **Key Tasks**:
    - Finalized technical stack: **FastAPI** (Backend), **React + Vite** (Frontend), **Ollama** (Local LLM), **SQLite** (DB).
    - Designed the system architecture: 3-stage pipeline (Docling Extraction → LLM Summarization → RAG Chatbot Integration).
    - Set up the project repository and initial development environment.
    - Drafted the System Requirement Specification (SRS) and initial DB schema.

### Week 3: Data Extraction Module Development
- **Status**: Completed
- **Objectives**: Automate the conversion of raw PDFs into structured text.
- **Key Tasks**:
    - Evaluated multiple PDF parsers (PyPDF2, PDFPlumber, Tika).
    - Integrated **Docling** for high-fidelity PDF-to-Markdown conversion, preserving structural continuity.
    - Implemented custom regex-based splitting logic to segment raw transcripts into discrete "Question & Answer" blocks.
    - Developed the `extractor/` module to handle header/footer stripping and basic transcript cleaning.

### Week 4: LLM Summarization Engine Implementation
- **Status**: Completed
- **Objectives**: Build the core AI engine for structured summarization.
- **Key Tasks**:
    - Integrated **LLaMA 3 (8B)** via local Ollama API.
    - Developed a two-stage prompt pipeline:
        1. **Extraction**: Identifying MP names, ministries, and raw summaries.
        2. **JSON Structuring**: Forcing the LLM output into a valid JSON schema for downstream processing.
    - Implemented a robust **Retry/Correction Logic** for handling malformed JSON responses from the LLM.
    - Built the `summarizer/` script to process entire debate sessions and generate `final_summary.json`.

### Week 5: RAG & Chatbot Integration
- **Status**: Completed
- **Objectives**: Enable interactive querying using Retrieval-Augmented Generation.
- **Key Tasks**:
    - Integrated **`all-MiniLM-L6-v2`** for local text embeddings.
    - Implemented **FAISS** (Facebook AI Similarity Search) for efficient semantic retrieval of debate chunks.
    - Developed the RAG pipeline: Retriever finds top 15 relevant chunks → Generator (LLaMA 3) answers based on context.
    - Implemented **Category Normalization** logic to map 400+ diverse AI-generated categories into 20 canonical themes (Education, Health, Defence, etc.).

### Week 6: UI, Integration & Final Testing
- **Status**: In Progress
- **Objectives**: Build the visual interface and finalize the analytics suite.
- **Key Tasks**:
    - Developed the **React frontend** using modern UI components.
    - Built the **Analytics Dashboard** featuring:
        - Debate Calendar (Date-based filtering).
        - Category Breakdown (Heatmap/Distribution).
        - Global analytical summaries across all imported debates.
    - Finalized the **Chat Interface** for real-time interaction with specific summaries.
    - Conducted system-wide testing, bug fixes for Hindi text handling, and prepared the final report documentation.

---

## AI Model Comparison Analysis

For the summarization engine, we evaluated several candidate models before selecting **LLaMA 3 (8B)**.

### Large Language Models (LLMs) Comparison

| Model | Parameters | Speed (Local) | JSON Accuracy | Context Window | Selection Reason |
|---|---|---|---|---|---|
| **LLaMA 3 (8B)** | 8.0 B | Moderate | **High** | 8K | **Primary Choice**: Best balance of intelligence and JSON formatting consistency on local hardware. |
| **Mistral (7B)** | 7.3 B | **Fast** | Moderate | 32K | Strong alternative, but slightly higher hallucinations in tabular extraction. |
| **Phi-3 Mini** | 3.8 B | **Very Fast** | Low | 4K | Fast but lacks the reasoning depth required for complex parliamentary JSON. |
| **GPT-4 (API)** | N/A | Fast | **Extreme** | 128K | Best performance, but rejected due to data privacy concerns and high operational costs. |

### Embedding Models Comparison (for Chatbot RAG)

| Model | Dimension | MTEB Score | Latency | Selection Reason |
|---|---|---|---|---|
| **`all-MiniLM-L6-v2`** | 384 | 58.9 | **< 10ms** | **Chosen**: Extremely efficient on CPU, providing near-instant retrieval. |
| **`bge-small-en-v1.5`** | 384 | 63.3 | 25ms | Higher accuracy but requires more memory; the trade-off wasn't necessary for this scope. |

---

## Key Challenges & Technical Insights

1. **Multilingual Complexity**: Handling Hindi/English mixed transcripts required advanced prompt engineering and specific normalization layers.
2. **Context Limits**: Parliamentary transcripts often exceed 10,000 words. A "smart-trimming" (head-and-tail preservation) approach was implemented for the overall summary.
3. **Local Deployment**: Debatify was intentionally designed to run **offline** using Ollama, ensuring that sensitive legislative data (or proprietary datasets) stay local to the user's machine.
