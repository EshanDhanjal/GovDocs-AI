import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.embeddings import generate_embedding


def main() -> None:
    text = "F-1 students are admitted for duration of status."

    try:
        embedding = generate_embedding(text)
    except requests.RequestException as exc:
        raise RuntimeError(
            "Unable to reach Ollama. Start it with 'ollama serve' and ensure the 'nomic-embed-text' model is available."
        ) from exc

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")


if __name__ == "__main__":
    main()