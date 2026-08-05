import os
import numpy as np
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity
import onnxruntime as ort
from transformers import AutoTokenizer
from app.config import get_settings

settings = get_settings()

ONNX_MODEL_DIR = os.environ.get("ONNX_MODEL_DIR", "/app/onnx_model")


@lru_cache(maxsize=1)
def get_embedding_session():
    """Load and cache the ONNX Runtime session + tokenizer (no torch dependency)."""
    model_dir = ONNX_MODEL_DIR

    # If ONNX_MODEL_DIR path does not exist on filesystem (e.g. running pytest outside Docker)
    if not os.path.exists(model_dir) or not os.path.exists(os.path.join(model_dir, "model.onnx")):
        local_onnx = os.path.join(os.path.dirname(__file__), "..", "..", "onnx_model")
        if os.path.exists(local_onnx) and os.path.exists(os.path.join(local_onnx, "model.onnx")):
            model_dir = local_onnx
        else:
            try:
                from optimum.onnxruntime import ORTModelForFeatureExtraction
                model = ORTModelForFeatureExtraction.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", export=True)
                os.makedirs(local_onnx, exist_ok=True)
                model.save_pretrained(local_onnx)
                tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
                tok.save_pretrained(local_onnx)
                model_dir = local_onnx
            except Exception:
                model_dir = local_onnx

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    session = ort.InferenceSession(
        os.path.join(model_dir, "model.onnx"),
        providers=["CPUExecutionProvider"],
    )

    return tokenizer, session


def _mean_pooling(token_embeddings: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Mean pool token embeddings, weighted by attention mask (matches sentence-transformers behavior)."""
    mask = attention_mask[..., np.newaxis].astype(np.float32)
    summed = np.sum(token_embeddings * mask, axis=1)
    counts = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
    return summed / counts


class EmbeddingService:
    """
    NLP Vector Embedding Service using ONNX Runtime directly (no PyTorch dependency)
    for lightweight, low-memory semantic similarity calculation.
    """

    def __init__(self):
        self._tokenizer = None
        self._session = None

    def _ensure_loaded(self):
        if self._session is None:
            self._tokenizer, self._session = get_embedding_session()

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate 384-dimensional vector embedding for text string."""
        if not text or not text.strip():
            return np.zeros((384,), dtype=np.float32)

        self._ensure_loaded()

        inputs = self._tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="np",
        )

        onnx_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
        }
        session_input_names = [i.name for i in self._session.get_inputs()]
        if "token_type_ids" in session_input_names:
            onnx_inputs["token_type_ids"] = inputs.get(
                "token_type_ids", np.zeros_like(inputs["input_ids"])
            ).astype(np.int64)

        outputs = self._session.run(None, onnx_inputs)
        token_embeddings = outputs[0]

        pooled = _mean_pooling(token_embeddings, inputs["attention_mask"])
        norm = np.linalg.norm(pooled, axis=1, keepdims=True)
        norm = np.clip(norm, a_min=1e-9, a_max=None)
        normalized = pooled / norm

        return normalized[0].astype(np.float32)

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
        sim_clamped = max(0.0, min(1.0, sim))
        return round(sim_clamped * 100.0, 2)
