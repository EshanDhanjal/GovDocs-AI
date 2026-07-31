import json
import math
from pathlib import Path
from typing import Any

from backend.app.services.embeddings import generate_embedding


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VECTOR_FILE = PROJECT_ROOT / "data" / "processed" / "knowledge_vectors.json"


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding dimensions do not match.")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a)
    )
    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def load_vectors() -> list[dict[str, Any]]:
    if not VECTOR_FILE.exists():
        raise FileNotFoundError(
            "Knowledge vectors were not found. Run "
            "'python scripts/ingest_documents.py' first."
        )

    with VECTOR_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def search_knowledge_base(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    query_embedding = generate_embedding(query)
    stored_chunks = load_vectors()

    scored_chunks: list[dict[str, Any]] = []

    for chunk in stored_chunks:
        embedding = chunk.get("embedding")

        if not embedding:
            continue

        score = cosine_similarity(
            query_embedding,
            embedding,
        )

        scored_chunks.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "title": chunk.get("title"),
                "source": chunk.get("source"),
                "url": chunk.get("url"),
                "document_types": chunk.get("document_types"),
                "topics": chunk.get("topics"),
                "text": chunk.get("text"),
                "similarity_score": score,
            }
        )

    scored_chunks.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return scored_chunks[:top_k]