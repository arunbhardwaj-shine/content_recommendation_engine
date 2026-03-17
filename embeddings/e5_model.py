from sentence_transformers import SentenceTransformer
from config.settings import settings
import torch


class E5Embedding:
    def __init__(self):
        print("🔹 Loading embedding model...")
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

        # Improve CPU performance
        if not torch.cuda.is_available():
            torch.set_num_threads(torch.get_num_threads())

    def embed_passages(self, texts: list[str], batch_size: int = 64):
        texts = [f"passage: {t}" for t in texts]
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )

    def embed_query(self, text: str):
        return self.model.encode(
            f"query: {text}",
            normalize_embeddings=True
        )


embedding_model = E5Embedding()