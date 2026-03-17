from embeddings.e5_model import embedding_model
from vectorstore.qdrant_client import qdrant_service

class ContentRecommender:

    def similar_articles(self, article_text: str, limit=10):
        query_vector = embedding_model.embed_query(article_text)
        results = qdrant_service.search(query_vector, limit=limit)

        return [
            {
                "article_id": r.payload["article_id"],
                "score": r.score
            }
            for r in results
        ]

content_recommender = ContentRecommender()