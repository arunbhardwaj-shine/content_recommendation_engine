import pandas as pd
from helpers.sql_helpers import pdf_query
from utils.db_utils import get_engine
from utils.dataset_utils import add_extracted_text_column
engine = get_engine()

df = pd.read_sql(pdf_query, engine)
df = add_extracted_text_column(df)
df = df.dropna()
df_eng = df[df["popup_email_content_language"]==0].reset_index(drop=True)
df_ru = df[df["popup_email_content_language"]==4].reset_index(drop=True)
print(f"English PDFs: {len(df_eng)}, Russian PDFs: {len(df_ru)}")
print(df)
df.to_csv("output_with_text.csv", index=False)
print(f"Saved {len(df)} rows to output_with_text.csv")