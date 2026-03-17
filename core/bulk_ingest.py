import uuid
from qdrant_client.http.models import PointStruct
from helpers.chunker import chunk_text
from vectorstore.qdrant_client import qdrant_service
from embeddings.e5_model import embedding_model


def ingest_dataframe_to_qdrant(
    df,
    embed_batch_size: int = 64,
    upsert_batch_size: int = 256
):
    buffer_chunks = []
    buffer_metadata = []
    total_inserted = 0

    for _, row in df.iterrows():
        text = row.get("extracted_text")
        pdf_id = row.get("pdf_id")

        if not text:
            continue

        base_metadata = row.to_dict()
        chunks = chunk_text(text)

        for chunk in chunks:
            buffer_chunks.append(chunk)
            buffer_metadata.append({
                "pdf_id": pdf_id,
                "text": chunk,
                **base_metadata
            })

        # When enough chunks collected → embed & upsert
        if len(buffer_chunks) >= upsert_batch_size:
            total_inserted += _process_batch(
                buffer_chunks,
                buffer_metadata,
                embed_batch_size
            )
            buffer_chunks.clear()
            buffer_metadata.clear()

    # Process remaining
    if buffer_chunks:
        total_inserted += _process_batch(
            buffer_chunks,
            buffer_metadata,
            embed_batch_size
        )

    print(f"✅ Total inserted vectors: {total_inserted}")


def _process_batch(chunks, metadata_list, embed_batch_size):
    vectors = embedding_model.embed_passages(
        chunks,
        batch_size=embed_batch_size
    )

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=metadata
        )
        for vector, metadata in zip(vectors, metadata_list)
    ]

    qdrant_service.upsert(points)
    return len(points)