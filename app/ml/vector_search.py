import faiss
import numpy as np
import os
from app.config import Config

class VectorDatabase:
    def __init__(self):
        self.db_path = Config.VECTOR_DB_PATH
        self.dimension = Config.FAISS_DIMENSION
        self.index = None
        self.content_ids = []
        self.id_to_content_map = {}
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(self.db_path):
            self.index = faiss.read_index(self.db_path)
        else:
            # Create new IVF index for better performance on large datasets
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            self.index.nprobe = 10
    
    def add_vectors(self, vectors: np.ndarray, content_ids: list):
        """Add vectors and their corresponding content IDs"""
        if vectors.shape[0] == 0:
            return
        
        vectors_f32 = vectors.astype(np.float32)
        
        # Train index if not trained
        if not self.index.is_trained:
            self.index.train(vectors_f32)
        
        # Add vectors
        start_idx = self.index.ntotal
        self.index.add(vectors_f32)
        
        # Map indices to content IDs
        for i, content_id in enumerate(content_ids):
            self.id_to_content_map[start_idx + i] = content_id
    
    def search_similar(self, query_vector: np.ndarray, k: int = 10) -> list:
        """Search for k most similar vectors
        Returns: [(content_id, distance), ...]
        """
        if self.index.ntotal == 0:
            return []
        
        query_f32 = query_vector.astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_f32, k)
        
        results = []
        for idx, distance in zip(indices[0], indices[0]):
            if idx != -1:  # -1 means not found
                content_id = self.id_to_content_map.get(idx, None)
                if content_id:
                    # Convert L2 distance to similarity score (0-1)
                    similarity = 1 / (1 + distance)
                    results.append((content_id, float(similarity)))
        
        return results
    
    def save_index(self):
        """Save index to disk"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        faiss.write_index(self.index, self.db_path)
    
    def get_index_stats(self) -> dict:
        """Get statistics about the index"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'is_trained': self.index.is_trained
        }
