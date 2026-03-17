from pathlib import Path
import pandas as pd

CSV_PATH = "output_video_with_text.csv"

df = pd.read_csv(CSV_PATH)
print(df)
breakpoint()
df["extracted_text"] = df["extracted_text"].apply(clean_text_for_biomed)
#df_eng = df[df["popup_email_content_language"]==0].reset_index(drop=True)
#df_ru = df[df["popup_email_content_language"]==4].reset_index(drop=True)
#print(f"English PDFs: {len(df_eng)}, Russian PDFs: {len(df_ru)}")
df = df[
    df["extracted_text"].notna() &
    (df["extracted_text"].str.strip() != "")
].reset_index(drop=True)
print(df)
breakpoint()
translator = RUENTranslator()
# Translate Russian → English
"""df_ru_translated = translator.translate_column(
    df=df_ru,
    source_col="extracted_text",
    target_col="extracted_text",
    batch_size=16
)"""

df_ru_translated = translator.translate_df_column(
    df=df_ru,
    source_col="extracted_text"
)

print(df_ru_translated,"Translated Russian DataFrame")
breakpoint()
df = pd.concat([df_eng, df_ru_translated]).reset_index(drop=True)
print(f"Total PDFs after translation: {len(df)}")
token_collection = get_collection(TOKEN_COLLECTION_NAME, reset=False)
sentence_collection = get_collection(SENTENCE_COLLECTION_NAME, reset=False)

token_embedder = TokenEmbedder(batch_size=512, max_length=512)
sentence_embedder = SentenceEmbedder(batch_size=128)

print("🔹 Ingesting TOKEN-level embeddings")
ingest_dataframe(df, token_embedder, token_collection)

print("🔹 Ingesting SENTENCE-level embeddings")
ingest_dataframe_sentences(df, sentence_embedder, sentence_collection)

print("TOKEN count:", token_collection.count())
print("SENTENCE count:", sentence_collection.count())

print("✅ Manual training complete (auto-persisted)")
