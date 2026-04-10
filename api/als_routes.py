from fastapi import APIRouter, Request
from services.als_services import als_recommender

router = APIRouter()
@router.get("/als/recommend/{email}")
async def recommend(email: str, request: Request):
    try:
        result = await als_recommender(email,request)
        return result
    except Exception as e:
        print(str(e))
        return {"email": email, "recommendations": []}
