import json
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import DATA_PATH, INDEX_FILE, META_FILE, EMBED_MODEL

print("📥 Loading structured JSON...")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []
metadata = []

for item in data:
    text_block = f"""
Question asked by: {item['summary']['asked_by']}
Ministry: {item['summary']['ministry']}
Category: {item['summary']['category']}

Question Summary:
{item['summary']['question_summary']}

Answer Summary:
{item['summary']['answer_summary']}

Overall Summary:
{item['summary']['overall_summary']}
"""
    documents.append(text_block)
    metadata.append(item)

print("🧠 Creating embeddings...")

model = SentenceTransformer(EMBED_MODEL)
embeddings = model.encode(documents).astype("float32")

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, INDEX_FILE)

with open(META_FILE, "wb") as f:
    pickle.dump(metadata, f)

print("✅ Vector index built successfully!")