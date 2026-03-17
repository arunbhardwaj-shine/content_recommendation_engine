from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "medical_articles"
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"
    VECTOR_SIZE: int = 1024

settings = Settings()