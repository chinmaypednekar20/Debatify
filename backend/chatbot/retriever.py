"""
retriever.py — On-the-fly summary-specific vector retrieval.

Given a debate's combined summary text and a user question,
this module chunks the text, builds a temporary in-memory FAISS index,
and returns the most relevant chunks.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from .config import EMBED_MODEL, TOP_K, CHUNK_SIZE, CHUNK_OVERLAP

# Cache for the embedding model
_model = None

# Cache for in-memory FAISS indices
_index_cache = {}

def get_model():
    global _model
    if _model is None:
        print("DEBUG: Loading SentenceTransformer model...")
        _model = SentenceTransformer(EMBED_MODEL)
        print("DEBUG: Model loaded")
    return _model


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping character-level chunks, but respect paragraph boundaries."""
    # First, split by double newlines to keep blocks of content together
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) + 2 <= CHUNK_SIZE:
            if current_chunk:
                current_chunk += "\n\n" + p
            else:
                current_chunk = p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            # If a single paragraph is larger than CHUNK_SIZE, split it further
            if len(p) > CHUNK_SIZE:
                start = 0
                while start < len(p):
                    end = start + CHUNK_SIZE
                    chunks.append(p[start:end].strip())
                    start += CHUNK_SIZE - CHUNK_OVERLAP
                current_chunk = ""
            else:
                current_chunk = p
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return [c for c in chunks if len(c) > 20]  # drop extremely tiny chunks


def retrieve_chunks(debate_id: int, summary_text: str, question: str) -> list[str]:
    """
    Retrieve the top-k most relevant text chunks from a summary.

    Args:
        debate_id: The ID of the debate to cache index for.
        summary_text: The full debate summary text to search within.
        question: The user's question.

    Returns:
        A list of relevant text chunks (strings).
    """
    global _index_cache
    
    if debate_id not in _index_cache:
        print(f"DEBUG: Building FAISS index for debate {debate_id}...")
        chunks = _chunk_text(summary_text)
        if not chunks:
            return []

        # Build in-memory FAISS index for this summary
        model = get_model()
        chunk_embeddings = model.encode(chunks).astype("float32")
        dimension = chunk_embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(chunk_embeddings)
        
        _index_cache[debate_id] = {
            "index": index,
            "chunks": chunks
        }
        print(f"DEBUG: Index for debate {debate_id} cached with {len(chunks)} chunks.")

    cached = _index_cache[debate_id]
    index = cached["index"]
    chunks = cached["chunks"]

    # Embed the question and search
    model = get_model()
    question_embedding = model.encode([question]).astype("float32")
    k = min(TOP_K, len(chunks))
    distances, indices = index.search(question_embedding, k)

    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return results
