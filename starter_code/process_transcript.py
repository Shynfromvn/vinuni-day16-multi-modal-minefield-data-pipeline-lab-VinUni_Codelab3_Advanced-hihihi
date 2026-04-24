import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Clean the transcript text and extract key information.

def clean_transcript(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # ------------------------------------------
    
    # TODO: Remove noise tokens like [Music], [inaudible], [Laughter]
    text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]\s*", "", text)
    text = re.sub(r"\[(?:Music starts|Music ends|Music|inaudible|Laughter)\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[Speaker\s*\d+\]:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    # TODO: Find the price mentioned in Vietnamese words ("năm trăm nghìn")
    detected_price_vnd = None
    if re.search(r"năm\s+trăm\s+nghìn", text, flags=re.IGNORECASE):
        detected_price_vnd = 500000
    else:
        numeric_match = re.search(r"500[,\.]?000\s*VND", text, flags=re.IGNORECASE)
        if numeric_match:
            detected_price_vnd = 500000

    # TODO: Return a cleaned dictionary for the UnifiedDocument schema.
    return {
        "document_id": "video-demo-transcript",
        "content": text,
        "source_type": "Video",
        "author": "Speaker 1",
        "timestamp": None,
        "source_metadata": {
            "original_file": file_path.split("\\")[-1].split("/")[-1],
            "detected_price_vnd": detected_price_vnd,
        },
    }

