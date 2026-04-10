from fastapi import APIRouter
from services.markov_services import markov_recommender

router = APIRouter()

@router.get("/recommend/markov/{email}")
async def recommend_markov(email: str):
    try:
        result = await markov_recommender(email)
        return result
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}
