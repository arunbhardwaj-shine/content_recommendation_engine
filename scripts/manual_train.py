from pathlib import Path
import pandas as pd

from core.bulk_ingest import ingest_dataframe_to_qdrant
from utils.text_utils import clean_text_for_biomed, clean_pdf_text

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "output.csv"

df = pd.read_csv(CSV_PATH)

# Clean text
df["extracted_text"] = df["extracted_text"].apply(clean_text_for_biomed)
df["extracted_text"] = df["extracted_text"].apply(clean_pdf_text)

# Remove empty rows
df = df[
    df["extracted_text"].notna() &
    (df["extracted_text"].str.strip() != "")
].reset_index(drop=True)

print(f"Total valid documents: {len(df)}")

print("🔹 Ingesting into Qdrant using E5 model")
ingest_dataframe_to_qdrant(df)

print("✅ Manual training complete")