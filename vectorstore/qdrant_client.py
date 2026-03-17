from qdrant_client import QdrantClient
from qdrant_client.http import models
from config.settings import settings


class QdrantService:
    def __init__(self):
        # Local embedded mode
        self.client = QdrantClient(path="./qdrant_data")
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        existing = [c.name for c in collections]

        if settings.COLLECTION_NAME not in existing:
            print(f"🔹 Creating collection: {settings.COLLECTION_NAME}")

            self.client.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=settings.VECTOR_SIZE,
                    distance=models.Distance.COSINE
                ),
                hnsw_config=models.HnswConfigDiff(
                    m=32,
                    ef_construct=200
                )
            )
        else:
            print(f"✅ Collection {settings.COLLECTION_NAME} already exists")

    def upsert(self, points):
        self.client.upsert(
            collection_name=settings.COLLECTION_NAME,
            points=points
        )

    def search(self, query_vector, limit=10):
        return self.client.query_points(
            collection_name=settings.COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            search_params=models.SearchParams(
                hnsw_ef=256
            )
        ).points


qdrant_service = QdrantService()