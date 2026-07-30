import json

from services.local_llm import call_local_llm
from services.prompt_loader import load_prompt


def classify_document_with_llm(extracted_text: str) -> dict:
    prompt = load_prompt("classify-document.md")

    prompt = prompt.replace(
        "{{OCR_TEXT}}",
        extracted_text[:4000]
    )

    response = call_local_llm(prompt)

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        return {
            "document_type": "UNKNOWN",
            "document_subtype": "UNKNOWN",
            "issuing_agency": "UNKNOWN",
            "confidence": 0.0,
            "error": "Local LLM did not return valid JSON",
            "raw_response": response
        }