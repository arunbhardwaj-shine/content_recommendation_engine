import uuid
from typing import Dict
from qdrant_client.http.models import PointStruct

from embeddings.e5_model import embedding_model
from helpers.chunker import chunk_text
from vectorstore.qdrant_client import qdrant_service


def ingest_dataframe_to_qdrant(df):
    points = []

    for _, row in df.iterrows():
        pdf_id = row.get("pdf_id")
        text = row.get("extracted_text")

        if not text:
            continue

        chunks = chunk_text(text)

        for chunk in chunks:
            vector = embedding_model.embed_passage(chunk)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "pdf_id": pdf_id,
                    "text": chunk,
                    # store any other metadata columns dynamically
                    **row.to_dict()
                }
            )
            points.append(point)

    if points:
        qdrant_service.upsert(points)
        print(f"✅ Inserted {len(points)} vectors into Qdrant")
    else:
        print("⚠️ No points to insert")