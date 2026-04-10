from sqlalchemy import text
from typing import Dict
import heapq
import numpy as np
from sqlalchemy import text
from utils.db_utils import get_engine
from vectorstore.qdrant_client import qdrant_service
from embeddings.e5_model import embedding_model
from utils.s3_utils import S3Client, docintel_code_generator
from helpers.sql_helpers import pdf_file_lookup_query
from utils.pdf_utils import extract_text_from_pdf
from helpers.chunker import chunk_text
from helpers.data_loader import get_pdf_titles
from helpers.sql_helpers import qdrant_query
import os
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
engine = get_engine()
async def qdrant_recommender(email: str):
    try:
        latest_query = text(qdrant_query)
        print(email,"EMAIL")
        with engine.connect() as conn:

            result = conn.execute(
                latest_query,
                {"email": email}
            ).fetchone()
            print(result,"RESULT")
            if not result:
                return {"email": email, "recommendations": []}

            user_id = result.user_id
            latest_pdf_id = result.pdf_id
            print(latest_pdf_id,"LPID")
            # 2️⃣ Fetch metadata
            row = conn.execute(
                text(pdf_file_lookup_query),
                {"pdf_id": latest_pdf_id}
            ).mappings().fetchone()

            if not row:
                return {"email": email, "recommendations": []}

            file_type = row["file_type"].lower()
            file_name = row["file_name"]
            folder_name = row["folder_name"]

            if not file_name or not folder_name:
                return {"email": email, "recommendations": []}

            # 3️⃣ Build S3 key
            s3_key = f"{file_type}/{folder_name}/{file_name}"

            s3_client = S3Client()
            file_bytes = s3_client.read_bytes(BUCKET_NAME, s3_key)
            print(len(file_bytes))
            if not file_bytes:
                return {"email": email, "recommendations": []}

            # 4️⃣ Extract text
            text_content = extract_text_from_pdf(file_bytes)

            if not text_content:
                return {"email": email, "recommendations": []}

            # 5️⃣ Chunk text
            chunks = chunk_text(text_content)

            if not chunks:
                return {"email": email, "recommendations": []}

            # Limit chunks for performance
            chunks = chunks[:8]
            # 6️⃣ Embed chunks as QUERY
            query_vectors = embedding_model.embed_passages(chunks)
            print(query_vectors,"QV")
            if isinstance(query_vectors, np.ndarray):
                query_vectors = query_vectors.tolist()

            best_scores: Dict[int, float] = {}

            # 7️⃣ Search Qdrant
            for vector in query_vectors:

                hits = qdrant_service.search(
                    query_vector=vector,
                    limit=10
                )

                for hit in hits:

                    payload = hit.payload
                    if not payload:
                        continue

                    pdf_id = payload.get("pdf_id")

                    if not pdf_id:
                        continue

                    if pdf_id == latest_pdf_id:
                        continue

                    score = float(hit.score)

                    # Keep maximum similarity score per document
                    if pdf_id not in best_scores or score > best_scores[pdf_id]:
                        best_scores[pdf_id] = score

            if not best_scores:
                return {"email": email, "recommendations": []}

            # 8️⃣ Rank top 3
            top_3 = heapq.nlargest(
                3,
                best_scores.items(),
                key=lambda x: x[1]
            )

            recommendations = []
            pdf_ids = [pdf_id for pdf_id, _ in top_3]
            print(pdf_ids,"PDF")
            title_map = get_pdf_titles(engine, pdf_ids)
            for pdf_id, score in top_3:

                docintel_url = docintel_code_generator(engine, pdf_id)

                recommendations.append({
                    "pdf_id": pdf_id,
                    "title": title_map.get(pdf_id),
                    "score": round(score, 4),
                    "docintel_url": docintel_url
                })
        print({
            "email": email,
            "based_on_pdf": latest_pdf_id,
            "recommendations": recommendations
        })
        return {
            "email": email,
            "based_on_pdf": latest_pdf_id,
            "recommendations": recommendations
        }
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}