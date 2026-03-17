import pdfplumber
from typing import Optional
import io
import os
from helpers.sql_helpers import pdf_file_lookup_query
from utils.s3_utils import S3Client
from helpers.sql_helpers import pdf_file_lookup_query
from sqlalchemy import text
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pdfplumber.
    Drop-in replacement for PyMuPDF version.
    """
    text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

    return "\n".join(text)

def get_pdf_text_by_id(engine, pdf_id: int) -> str | None:
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(pdf_file_lookup_query),
                {"pdf_id": pdf_id}
            ).mappings().fetchone()

        if not row:
            return None

        file_type = row["file_type"].lower()
        file_name = row["file_name"]
        folder_name = row["folder_name"]
        language = row["popup_email_content_language"]

        # 🚫 Skip non-English
        if language != 0:
            return None

        # 🚫 Skip videos
        if file_type == "video":
            return None

        if not file_name or not folder_name:
            return None

        s3_key = f"{file_type}/{folder_name}/{file_name}"

        s3_client = S3Client()
        file_bytes = s3_client.read_bytes(BUCKET_NAME, s3_key)

        if not file_bytes:
            return None

        if file_type in {"pdf", "ebook"}:
            return extract_text_from_pdf(file_bytes)

        return None

    except Exception as e:
        print(f"S3 extraction failed for pdf_id={pdf_id}: {e}")
        return None