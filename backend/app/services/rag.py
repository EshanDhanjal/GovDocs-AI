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


def format_document_context(document_context: dict | None) -> str:
    if not document_context:
        return "No uploaded document context was provided."

    classification = document_context.get("classification")
    extracted_fields = document_context.get("extracted_fields")
    summary = document_context.get("summary")
    ocr_text = document_context.get("ocr_text", "")

    return (
        "UPLOADED DOCUMENT CONTEXT:\n\n"
        f"Classification:\n"
        f"{json.dumps(classification, indent=2)}\n\n"
        f"Extracted fields:\n"
        f"{json.dumps(extracted_fields, indent=2)}\n\n"
        f"Document summary:\n"
        f"{json.dumps(summary, indent=2)}\n\n"
        f"OCR text:\n"
        f"{ocr_text[:4000]}"
    )


def answer_question_with_rag(
    question: str,
    top_k: int = 5,
    document_context: dict | None = None,
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
        "{{DOCUMENT_CONTEXT}}",
        format_document_context(document_context),
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
        for index, source in enumerate(
            retrieved_sources,
            start=1,
        )
    ]

    return answer