import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import INDEX_FILE, META_FILE, EMBED_MODEL, TOP_K

model = SentenceTransformer(EMBED_MODEL)

index = faiss.read_index(INDEX_FILE)

with open(META_FILE, "rb") as f:
    metadata = pickle.load(f)

def retrieve(query):

    query_embedding = model.encode([query]).astype("float32")

    distances, indices = index.search(query_embedding, TOP_K)

    results = [metadata[i] for i in indices[0]]

    return results