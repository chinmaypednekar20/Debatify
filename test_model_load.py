from sentence_transformers import SentenceTransformer
import time

print("Loading model...")
start = time.time()
_model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Model loaded in {time.time() - start:.2f} seconds")
