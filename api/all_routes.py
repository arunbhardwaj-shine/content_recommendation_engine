from fastapi import APIRouter, Request
from services.als_services import als_recommender
from services.markov_services import markov_recommender
from services.qdrant_services import qdrant_recommender
router = APIRouter()

@router.get("/all/recommend/{email}")
async def recommend(email: str, request: Request):
    try:
        als_result = await als_recommender(email,request)
        markov_result = await markov_recommender(email)
        qdrant_result = await qdrant_recommender(email)
        return {
            "email": email,
            "als_recommendations": als_result.get("recommendations", []),
            "markov_recommendations": markov_result.get("recommendations", []),
            "qdrant_recommendations": qdrant_result.get("recommendations", [])
        }
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}