import pandas as pd
from helpers.sql_helpers import user_sequences_query

def prepare_als_data(engine):
    df = pd.read_sql(user_sequences_query, engine)
    # Aggregate repeated reads
    interaction_df = (
        df.groupby(["user_id", "pdf_id"])
          .size()
          .reset_index(name="strength")
    )

    # Remove sparse users
    user_counts = interaction_df["user_id"].value_counts()
    active_users = user_counts[user_counts >= 2].index
    interaction_df = interaction_df[
        interaction_df["user_id"].isin(active_users)
    ]

    # Remove sparse PDFs
    pdf_counts = interaction_df["pdf_id"].value_counts()
    active_pdfs = pdf_counts[pdf_counts >= 2].index
    interaction_df = interaction_df[
        interaction_df["pdf_id"].isin(active_pdfs)
    ]

    return interaction_df