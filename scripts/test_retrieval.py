import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.vector_store import search_knowledge_base


def main() -> None:
    question = "What does D/S mean for an F-1 student?"

    results = search_knowledge_base(
        query=question,
        top_k=3,
    )

    print(f"Question: {question}\n")

    for index, result in enumerate(results, start=1):
        print(f"Result {index}")
        print(f"Title: {result['title']}")
        print(f"Source: {result['source']}")
        print(f"Score: {result['similarity_score']:.4f}")
        print(f"Text: {result['text'][:500]}")
        print("-" * 60)


if __name__ == "__main__":
    main()