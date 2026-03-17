from helpers.sql_helpers import pdf_query
from utils.db_utils import get_engine
from utils.dataset_utils import add_extracted_text_column
import ast
import pandas as pd

def generate_tag_frequency_table(sql_query):
    try:
        engine = get_engine()
        df = pd.read_sql(pdf_query, engine)
        df_eng = df[df["popup_email_content_language"]==0].reset_index(drop=True)
        # 1. Drop NA / empty strings
        df_tags = df_eng.dropna(subset=["tags"]).copy()
        df_tags = df_tags[df_tags["tags"].str.strip() != ""]

        # 2. Convert string of list → actual list
        # Example string: "['immunogenicity', 'PUPs', 'ITI']"
        df_tags["tags"] = df_tags["tags"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

        # 3. Flatten all tags into one list
        all_tags = [tag for tags_list in df_tags["tags"] for tag in tags_list]

        # 4. Calculate frequency
        tag_freq_df = (
            pd.Series(all_tags)
            .value_counts()
            .reset_index()
        )

        # 5. Rename columns
        tag_freq_df.columns = ["tag", "frequency"]

        return tag_freq_df.head(50).to_dict(orient="records")
    except Exception as e:
        return str(e)


def deduplicate_tags(tags: list[dict]) -> list[dict]:
    """
    Deduplicate tags by name.
    Keeps highest confidence for each tag.
    """
    dedup = {}

    for item in tags:
        tag = item["tag"]
        conf = item["confidence"]

        if tag not in dedup or conf > dedup[tag]:
            dedup[tag] = conf

    return sorted(
        [{"tag": k, "confidence": round(v, 4)} for k, v in dedup.items()],
        key=lambda x: x["confidence"],
        reverse=True
    )

def merge_and_deduplicate(tags_list: list[list[dict]]) -> list[dict]:
    """
    Merge tag outputs from multiple PDFs.
    Keeps highest confidence per tag.
    """
    merged = {}

    for tags in tags_list:
        for item in tags:
            tag = item["tag"]
            conf = item["confidence"]

            if tag not in merged or conf > merged[tag]:
                merged[tag] = conf

    return sorted(
        [{"tag": k, "confidence": round(v, 4)} for k, v in merged.items()],
        key=lambda x: x["confidence"],
        reverse=True
    )