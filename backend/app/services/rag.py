import json

from backend.app.services.local_llm import call_local_llm
from backend.app.services.prompt_loader import load_prompt
from backend.app.services.vector_store import search_knowledge_base


def format_context(results: list[dict]) -> str:
    context_sections: list[str] = []

    for index, result in enumerate(results, start=1):
        section = (
            f"SOURCE {index}\n"
            f"Title: {result.get('title', '')}\n"
            f"Publisher: {result.get('source', '')}\n"
            f"URL: {result.get('url', '')}\n"
            f"Passage: {result.get('text', '')}"
        )

        context_sections.append(section)

    return "\n\n".join(context_sections)


def answer_question_with_rag(
    question: str,
    top_k: int = 5,
) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    retrieved_sources = search_knowledge_base(
        query=question,
        top_k=top_k,
    )

    if not retrieved_sources:
        return {
            "answer": (
                "I could not find relevant information in the "
                "current official-source knowledge base."
            ),
            "sources_used": [],
            "confidence": "low",
            "needs_professional_help": False,
            "professional_help_reason": None,
            "disclaimer": (
                "GovDocs-AI is for informational purposes only and "
                "does not provide legal or immigration advice."
            ),
            "retrieved_sources": [],
        }

    prompt = load_prompt("answer-question.md")

    prompt = prompt.replace(
        "{{QUESTION}}",
        question,
    )

    prompt = prompt.replace(
        "{{CONTEXT}}",
        format_context(retrieved_sources),
    )

    response = call_local_llm(prompt)

    try:
        answer = json.loads(response)
    except json.JSONDecodeError:
        answer = {
            "answer": (
                "The local language model did not return valid JSON."
            ),
            "sources_used": [],
            "confidence": "low",
            "needs_professional_help": False,
            "professional_help_reason": None,
            "disclaimer": (
                "GovDocs-AI is for informational purposes only and "
                "does not provide legal or immigration advice."
            ),
            "error": "Invalid JSON returned by local LLM.",
            "raw_response": response,
        }

    answer["retrieved_sources"] = [
        {
            "source_number": index,
            "title": source.get("title"),
            "publisher": source.get("source"),
            "url": source.get("url"),
            "similarity_score": source.get("similarity_score"),
        }
        for index, source in enumerate(retrieved_sources, start=1)
    ]

    return answer