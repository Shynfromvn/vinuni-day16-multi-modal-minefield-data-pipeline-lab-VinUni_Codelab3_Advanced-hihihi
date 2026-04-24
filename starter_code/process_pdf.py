import os
import json
import time
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()
if genai is not None and os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _fallback_pdf_document(file_path, reason):
    return {
        "document_id": f"pdf-{os.path.splitext(os.path.basename(file_path))[0]}",
        "content": (
            "Summary unavailable from Gemini in the current environment. "
            f"Stored fallback record for {os.path.basename(file_path)}. Reason: {reason}."
        ),
        "source_type": "PDF",
        "author": "Unknown",
        "timestamp": None,
        "source_metadata": {
            "original_file": os.path.basename(file_path),
            "extraction_method": "fallback",
            "fallback_reason": reason,
        },
    }

def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    if genai is None:
        return _fallback_pdf_document(file_path, "google-generativeai not installed")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_pdf_document(file_path, "missing GEMINI_API_KEY")

    # Thay đổi model name để tránh lỗi 404 trên các phiên bản API cũ
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = """
Analyze this document and extract a summary and the author. 
Output exactly as a JSON object matching this exact format:
{
    "document_id": "pdf-doc-001",
    "content": "Summary: [Insert your 3-sentence summary here]",
    "source_type": "PDF",
    "author": "[Insert author name here]",
    "timestamp": null,
    "source_metadata": {"original_file": "lecture_notes.pdf"}
}
"""

    backoff_seconds = 1
    last_error = None

    for _ in range(3):
        try:
            print(f"Uploading {file_path} to Gemini...")
            pdf_file = genai.upload_file(path=file_path)
            print("Generating content from PDF using Gemini...")
            response = model.generate_content([pdf_file, prompt])
            content_text = (response.text or "").strip()

            # Simple cleanup if the response is wrapped in markdown json block
            if content_text.startswith("```json"):
                content_text = content_text[7:]
            if content_text.endswith("```"):
                content_text = content_text[:-3]
            if content_text.startswith("```"):
                content_text = content_text[3:]

            extracted_data = json.loads(content_text.strip())
            extracted_data.setdefault("document_id", f"pdf-{os.path.splitext(os.path.basename(file_path))[0]}")
            extracted_data.setdefault("content", "")
            extracted_data.setdefault("source_type", "PDF")
            extracted_data.setdefault("author", "Unknown")
            extracted_data.setdefault("timestamp", None)
            extracted_data.setdefault("source_metadata", {})
            extracted_data["source_metadata"]["original_file"] = os.path.basename(file_path)
            extracted_data["source_metadata"]["extraction_method"] = "gemini"
            return extracted_data
        except Exception as e:
            last_error = str(e)
            if "429" in last_error:
                time.sleep(backoff_seconds)
                backoff_seconds *= 2
                continue
            break

    return _fallback_pdf_document(file_path, last_error or "unknown extraction failure")
