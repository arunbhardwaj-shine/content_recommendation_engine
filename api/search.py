from fastapi import APIRouter
from core.content_recommender import content_recommender

router = APIRouter()

@router.post("/recommend/similar")
def get_similar_articles(request: dict):
    article_text = request["article_text"]
    return content_recommender.similar_articles(article_text)

@router.post("/recommend/collaborative")
def get_collaborative_recommendations(request: dict):
    user_id = request["user_id"]
    return content_recommender.collaborative_recommendations(user_id)