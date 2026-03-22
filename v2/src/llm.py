import requests
from src.config import OLLAMA_URL, OLLAMA_MODEL

def generate_answer(question, context):

    prompt = f"""
You are an intelligent AI assistant analyzing a Parliament debate.

Use the structured summaries provided to answer naturally.
You may combine multiple summaries if relevant.

Debate Context:
{context}

User Question:
{question}

Provide a clear, natural answer:
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 8192
        }
    }

    response = requests.post(OLLAMA_URL, json=payload)

    return response.json()["response"]