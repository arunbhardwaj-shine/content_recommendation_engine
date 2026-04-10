import pandas as pd
from helpers.sql_helpers import pdf_query
from utils.db_utils import get_engine
from utils.dataset_utils import add_extracted_text_column
engine = get_engine()

df = pd.read_sql(pdf_query, engine)
df_video = df[
    (df["file_type"] == "video") #&
    #(df["popup_email_content_language"] == 0)
].reset_index(drop=True)
ids = [3425,3426,3548,3549,2716,3694]
df = df[df["pdf_id"].isin(ids)].reset_index(drop=True)
print(df_video.file_name.unique())
breakpoint()
df_video = add_extracted_text_column(df_video)
print(df_video)
df_video.to_csv("output_video_with_textv2.csv", index=False)
print(f"Saved {len(df_video)} rows to output_video_with_textv2.csv")