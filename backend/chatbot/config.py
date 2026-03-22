# ── Chatbot Configuration ──────────────────────────────────────────────────

# Sentence embedding model (runs locally, no API key needed)
EMBED_MODEL = "all-MiniLM-L6-v2"

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"

# Retrieval settings
TOP_K = 15           # number of chunks to retrieve
CHUNK_SIZE = 400    # characters per chunk
CHUNK_OVERLAP = 80  # overlap between consecutive chunks
