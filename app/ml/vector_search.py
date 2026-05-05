"""
FAISS Vector Database — stores and searches content embeddings
for fast approximate nearest-neighbour retrieval.
"""

import os
import numpy as np
import faiss
from app.config import Config


class VectorDatabase:
    """Thin wrapper around a FAISS Flat L2 index with content-ID mapping."""

    def __init__(self):
        self.dimension = Config.FAISS_DIMENSION  # 384
        self.index_path = Config.VECTOR_DB_PATH
        self.content_ids: list[str] = []
        self.index: faiss.IndexFlatL2 = None
        self.load_or_create_index()

    # ── Index lifecycle ──────────────────────────────────────

    def load_or_create_index(self):
        """Load an existing FAISS index from disk, or create a fresh one."""
        ids_path = self.index_path + ".ids.npy"
        if os.path.exists(self.index_path) and os.path.exists(ids_path):
            self.index = faiss.read_index(self.index_path)
            self.content_ids = list(np.load(ids_path, allow_pickle=True))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.content_ids = []

    def save_index(self):
        """Persist the FAISS index and ID mapping to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        np.save(self.index_path + ".ids.npy", np.array(self.content_ids, dtype=object))

    def reset_index(self):
        """Drop current index and create a fresh one."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.content_ids = []

    # ── Read / write ─────────────────────────────────────────

    def add_vectors(self, vectors: np.ndarray, content_ids: list[str]):
        """
        Add vectors to the index.
        vectors : (N, 384) float32 matrix
        content_ids : list of N content-id strings
        """
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        vectors = vectors.astype(np.float32)
        self.index.add(vectors)
        self.content_ids.extend(content_ids)

    def search_similar(self, query_vector: np.ndarray, k: int = 10):
        """
        Find the k nearest neighbours for a query vector.
        Returns list of (content_id, distance) tuples sorted by distance.
        """
        if self.index.ntotal == 0:
            return []
        query = query_vector.astype(np.float32).reshape(1, -1)
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.content_ids):
                continue
            results.append((self.content_ids[idx], float(dist)))
        return results

    # ── Stats ────────────────────────────────────────────────

    def get_index_stats(self) -> dict:
        """Return summary statistics about the current index."""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "is_trained": self.index.ntotal > 0 if self.index else False,
        }
