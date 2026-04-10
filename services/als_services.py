from utils.s3_utils import docintel_code_generator
from utils.db_utils import get_engine
from helpers.data_loader import get_pdf_titles
from sqlalchemy import text
from helpers.sql_helpers import als_query
engine = get_engine()
async def als_recommender(email,request):
    try:
        als_model = request.app.state.als_model
        latest_query = text(als_query)
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
        print(user_id,"USER_ID")
        raw_recommendations = als_model.recommend(user_id)
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
            "recommendations": enriched_recommendations
        }
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}