def classify_document(extracted_text: str) -> dict:
    text = extracted_text.lower()

    if "i-94" in text or "arrival/departure record" in text:
        return {
            "document_type": "I-94",
            "document_subtype": "Arrival / Departure Record",
            "issuing_agency": "U.S. Customs and Border Protection (CBP)",
            "confidence": 0.99
        }

    if "form i-20" in text or "certificate of eligibility for nonimmigrant student status" in text:
        return {
            "document_type": "I-20",
            "document_subtype": "Certificate of Eligibility for Nonimmigrant Student Status",
            "issuing_agency": "Department of Homeland Security (DHS) / SEVP",
            "confidence": 0.98
        }

    if "employment authorization document" in text or "form i-766" in text:
        return {
            "document_type": "I-766",
            "document_subtype": "Employment Authorization Document (EAD)",
            "issuing_agency": "U.S. Citizenship and Immigration Services (USCIS)",
            "confidence": 0.98
        }

    if "i-797a" in text or "notice type: approval notice" in text:
        return {
            "document_type": "I-797A",
            "document_subtype": "Approval Notice",
            "issuing_agency": "U.S. Citizenship and Immigration Services (USCIS)",
            "confidence": 0.97
        }

    if "i-797c" in text or "receipt notice" in text:
        return {
            "document_type": "I-797C",
            "document_subtype": "Receipt Notice",
            "issuing_agency": "U.S. Citizenship and Immigration Services (USCIS)",
            "confidence": 0.97
        }

    if "i-797" in text or "notice of action" in text:
        return {
            "document_type": "I-797",
            "document_subtype": "Notice of Action",
            "issuing_agency": "U.S. Citizenship and Immigration Services (USCIS)",
            "confidence": 0.90
        }

    return {
        "document_type": "UNKNOWN",
        "document_subtype": "UNKNOWN",
        "issuing_agency": "UNKNOWN",
        "confidence": 0.0
    }