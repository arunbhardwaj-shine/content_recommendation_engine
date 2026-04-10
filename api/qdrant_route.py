from fastapi import APIRouter
from services.qdrant_services import qdrant_recommender

router = APIRouter()


@router.get("/recommend/content/{email}")
async def recommend_content_based(email: str):
    try:
        result = await qdrant_recommender(email)
        return result
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}
