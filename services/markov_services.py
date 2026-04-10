from utils.db_utils import get_engine
from helpers.sql_helpers import markov_query
from utils.s3_utils import docintel_code_generator
from sqlalchemy import text
from helpers.data_loader import get_pdf_titles
from core.model_registry import markov_model
from helpers.sql_helpers import markov_query

engine = get_engine()
async def markov_recommender(email: str):
    try:
        latest_query = text(markov_query)
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