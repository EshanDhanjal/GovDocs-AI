import json

from services.local_llm import call_local_llm
from services.prompt_loader import load_prompt


def summarize_document_with_llm(
    extracted_text: str,
    classification: dict,
    extracted_fields: dict,
) -> dict:
    prompt = load_prompt("summarize-document.md")

    prompt = prompt.replace(
        "{{CLASSIFICATION}}",
        json.dumps(classification, indent=2),
    )

    prompt = prompt.replace(
        "{{EXTRACTED_FIELDS}}",
        json.dumps(extracted_fields, indent=2),
    )

    prompt = prompt.replace(
        "{{OCR_TEXT}}",
        extracted_text[:6000],
    )

    response = call_local_llm(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "error": "Local LLM did not return valid JSON",
            "raw_response": response,
        }