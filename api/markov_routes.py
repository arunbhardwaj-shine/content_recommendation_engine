from fastapi import APIRouter
from sqlalchemy import text
from utils.db_utils import get_engine
engine = get_engine()
from core.model_registry import markov_model
from utils.s3_utils import docintel_code_generator
from sqlalchemy import text
from helpers.data_loader import get_pdf_titles

router = APIRouter()

@router.get("/recommend/markov/{email}")
def recommend_markov(email: str):
    try:
        latest_query = text("""
        WITH recent_reads AS (
            SELECT 
                ptt.user_id,
                ptt.pdf_id,
                p.popup_email_content_language,
                ptt.starttime
            FROM pdf_time_tracks ptt
            JOIN pdfs p ON p.id = ptt.pdf_id
            WHERE ptt.user_id = (
                SELECT id
                FROM users
                WHERE email = :email
                ORDER BY id ASC
                LIMIT 1
            )
            ORDER BY ptt.starttime DESC
            LIMIT 5
        ),

        majority_language AS (
            SELECT popup_email_content_language
            FROM recent_reads
            GROUP BY popup_email_content_language
            ORDER BY COUNT(*) DESC
            LIMIT 1
        )

        SELECT rr.user_id, rr.pdf_id
        FROM recent_reads rr
        JOIN majority_language ml 
        ON rr.popup_email_content_language = ml.popup_email_content_language
        ORDER BY rr.starttime DESC
        LIMIT 1;
        """)
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
            latest_pdf = result.pdf_id
        print(latest_pdf,"LPID")
        # 2️⃣ Get Markov recommendations
        raw_recommendations = markov_model.recommend(latest_pdf)
        enriched_recommendations = []
        pdf_ids = [item["pdf_id"] for item in raw_recommendations]

        title_map = get_pdf_titles(engine, pdf_ids)
        for item in raw_recommendations:
            pdf_id = item["pdf_id"]
            score = float(item["score"])  # ensure JSON serializable

            # Generate DocIntel URL key
            docintel_url = docintel_code_generator(engine, pdf_id)

            enriched_recommendations.append({
                "pdf_id": pdf_id,
                "title": title_map.get(pdf_id),
                "score": score,
                "docintel_url": docintel_url
            })
        return {
            "email": email,
            "based_on_pdf": latest_pdf,
            "recommendations": enriched_recommendations
        }
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}
