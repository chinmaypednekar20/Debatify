"""
llm.py — Send a context + question to Ollama and return the generated answer.

Includes a safety guard: the prompt instructs the model to only answer from the
provided debate summary context. If it cannot, it must respond with the
standard out-of-scope message.
"""

import requests
from .config import OLLAMA_URL, OLLAMA_MODEL

SAFETY_FALLBACK = "I'm sorry, I can only answer questions that are directly related to this specific debate summary. Could you please rephrase your question or ask about a different part of the summary?"


def generate_answer(question: str, context: str) -> str:
    """
    Call Ollama with a debate-assistant prompt.

    Args:
        question: The user's question.
        context: Retrieved chunks from the debate summary.

    Returns:
        The LLM's answer string.
    """
    prompt = f"""You are a helpful AI Assistant for parliamentary debates. Your goal is to provide accurate information based ONLY on the provided debate summary context.

--- Debate Summary Context ---
{context}
--- End of Context ---

STRICT INSTRUCTIONS:
1. Ground your answer strictly in the context above. 
2. If the context does not contain enough information to answer the question, or if the question is unrelated to the debate, respond with the exact phrase: "{SAFETY_FALLBACK}"
3. Be professional, concise, and helpful.
4. If asked for a summary, provide a high-level overview of the provided context.

Question: {question}

Answer:"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 8192,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", SAFETY_FALLBACK).strip()
    except requests.exceptions.ConnectionError:
        return (
            "Ollama is not running. Please start Ollama with: ollama serve"
        )
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"
