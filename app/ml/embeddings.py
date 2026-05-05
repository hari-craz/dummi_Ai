"""
Embedding Manager — wraps Sentence Transformers (all-MiniLM-L6-v2)
for generating 384-dimensional text embeddings.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import Config


class EmbeddingManager:
    """Generate and compare text embeddings using a pre-trained model."""

    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.dimension = Config.FAISS_DIMENSION  # 384

    def generate_embedding(self, text: str) -> np.ndarray:
        """Encode a single text string into a 384-dim float32 vector."""
        return self.model.encode(text, convert_to_numpy=True).astype(np.float32)

    def generate_embeddings_batch(self, texts: list) -> np.ndarray:
        """Encode a list of texts into an (N, 384) float32 matrix."""
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True).astype(np.float32)

    @staticmethod
    def get_content_embedding_text(content) -> str:
        """
        Build a single text string from content metadata.
        Used as input to the embedding model.
        """
        import json
        parts = [content.title, content.category]
        tags = json.loads(content.tags) if isinstance(content.tags, str) else content.tags
        if tags:
            parts.append(" ".join(tags))
        if content.description:
            parts.append(content.description)
        return " ".join(parts)

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot = np.dot(vec1, vec2)
        norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        if norm == 0:
            return 0.0
        return float(dot / norm)
