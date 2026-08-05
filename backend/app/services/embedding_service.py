import numpy as np
from typing import List
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from app.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Loads and caches sentence-transformers model in memory using ONNX backend.
    Default model: all-MiniLM-L6-v2 (can be swapped via EMBEDDING_MODEL_NAME setting).
    """
    from sentence_transformers import SentenceTransformer
    model_name = settings.EMBEDDING_MODEL_NAME or "all-MiniLM-L6-v2"
    try:
        return SentenceTransformer(model_name, backend='onnx')
    except Exception:
        return SentenceTransformer(model_name)


class EmbeddingService:
    """
    NLP Vector Embedding Service utilizing Sentence Transformers
    for semantic similarity calculation.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = get_embedding_model()
        return self._model

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate 384-dimensional vector embedding for text string."""
        if not text or not text.strip():
            return np.zeros((384,), dtype=np.float32)
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        Returns a score scaled between 0.0 and 100.0.
        """
        if not text1.strip() or not text2.strip():
            return 0.0

        emb1 = self.generate_embedding(text1).reshape(1, -1)
        emb2 = self.generate_embedding(text2).reshape(1, -1)

        sim = float(cosine_similarity(emb1, emb2)[0][0])
        # Clamp between 0.0 and 1.0, then scale to 0–100
        sim_clamped = max(0.0, min(1.0, sim))
        return round(sim_clamped * 100.0, 2)
