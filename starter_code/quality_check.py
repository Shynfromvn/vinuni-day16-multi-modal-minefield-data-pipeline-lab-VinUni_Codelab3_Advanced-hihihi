# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

def run_quality_gate(document_dict):
    # TODO: Reject documents with 'content' length < 20 characters
    content = str(document_dict.get("content", "")).strip()
    if len(content) < 20:
        return False

    # TODO: Reject documents containing toxic/error strings (e.g., 'Null pointer exception')
    toxic_strings = [
        "Null pointer exception",
        "Traceback",
        "OCR Error",
        "Failed to upload file",
    ]
    lowered_content = content.lower()
    if any(toxic.lower() in lowered_content for toxic in toxic_strings):
        return False

    # TODO: Flag discrepancies (e.g., if tax calculation comment says 8% but code says 10%)
    metadata = document_dict.get("source_metadata", {}) or {}
    if metadata.get("logic_discrepancy"):
        return False

    # Return True if pass, False if fail.
    return True
