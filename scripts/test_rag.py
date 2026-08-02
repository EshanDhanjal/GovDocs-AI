import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag import answer_question_with_rag


def main() -> None:
    question = "What does D/S mean for an F-1 student?"

    result = answer_question_with_rag(
        question=question,
        top_k=3,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()