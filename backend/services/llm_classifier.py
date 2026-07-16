import json

from services.local_llm import call_local_llm


def classify_document_with_llm(extracted_text: str) -> dict:
    prompt = f"""
You are an expert document classification assistant for GovDocs-AI.

Your job is to classify an OCR-extracted U.S. government document.

Return ONLY valid JSON.

Do not use markdown.
Do not explain your reasoning.
Do not return any text before or after the JSON.

Use ONLY one of these document types:

- I-20
- I-94
- I-797
- I-797A
- I-797C
- I-766
- UNKNOWN

Use the following subtype mappings:

I-20
Subtype:
"Certificate of Eligibility for Nonimmigrant Student Status"

I-94
Subtype:
"Arrival / Departure Record"

I-797
Subtype:
"Notice of Action"

I-797A
Subtype:
"Approval Notice"

I-797C
Subtype:
"Receipt Notice"

I-766
Subtype:
"Employment Authorization Document"

Use the following issuing agencies:

I-20:
Department of Homeland Security (DHS) / SEVP

I-94:
U.S. Customs and Border Protection (CBP)

I-797 / I-797A / I-797C / I-766:
U.S. Citizenship and Immigration Services (USCIS)

Return JSON in exactly this format:

{{
    "document_type": "",
    "document_subtype": "",
    "issuing_agency": "",
    "confidence": 0.0
}}

OCR Text:

{extracted_text[:4000]}
"""

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