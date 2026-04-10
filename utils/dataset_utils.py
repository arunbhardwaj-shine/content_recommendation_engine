import pandas as pd
from typing import Optional
from utils.s3_utils import S3Client
from utils.pdf_utils import extract_text_from_pdf
from utils.video_utils import extract_text_from_video
from dotenv import load_dotenv
import os
load_dotenv()
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
def build_s3_key(row: pd.Series) -> str:
    return f"{row['file_type']}/{row['folder_name']}/{row['file_name']}"



def extract_text_for_row(row: pd.Series, s3_client: S3Client) -> Optional[str]:
    try:
        s3_key = build_s3_key(row)
        file_bytes = s3_client.read_bytes(BUCKET_NAME, s3_key)

        if not file_bytes:
            return None

        file_type = row["file_type"].lower()
        print(f"Extracting text for: {s3_key}")
        print(len(file_bytes))
        # 🔁 ROUTER
        #if file_type == "pdf":
            #return extract_text_from_pdf(file_bytes)
        if file_type in {"mp4", "video"}:
            return extract_text_from_video(file_bytes)
        #elif file_type == "ebook":
            #return extract_text_from_pdf(file_bytes)  # Assuming ebooks are also PDFs
        else:
            print(f"Unsupported file type: {file_type}")
            return None

    except Exception as e:
        print(f"Extraction failed for id={row.get('pdf_id')}: {e}")
        return None


def add_extracted_text_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Iterates over DataFrame rows and adds 'extracted_text' column.
    """
    s3_client = S3Client()

    df["extracted_text"] = df.apply(
        lambda row: extract_text_for_row(row, s3_client),
        axis=1
    )

    return df
