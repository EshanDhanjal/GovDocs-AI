import requests


OLLAMA_EMBEDDINGS_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Cannot generate an embedding for empty text.")

    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text,
    }

    response = requests.post(
        OLLAMA_EMBEDDINGS_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()
    embedding = data.get("embedding")

    if not embedding:
        raise RuntimeError("Ollama did not return an embedding.")

    return embedding