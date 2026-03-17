from sqlalchemy import text
import pandas as pd
from .sql_helpers import user_sequences_query
def load_user_sequences(engine):
    query = text(user_sequences_query)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    print(df,"DF")
    df["starttime"] = pd.to_datetime(df["starttime"])
    df = df.sort_values(["user_id", "starttime"])

    return df

def get_pdf_titles(engine, pdf_ids):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, title FROM pdfs WHERE id IN :ids"),
            {"ids": tuple(pdf_ids)}
        ).mappings().all()

    return {row["id"]: row["title"] for row in rows}