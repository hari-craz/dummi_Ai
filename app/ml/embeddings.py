import numpy as np
import json
from sentence_transformers import SentenceTransformer
from app.config import Config

class EmbeddingManager:
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: list) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings
    
    def get_content_embedding_text(self, content: dict) -> str:
        """Create text representation of content for embedding"""
        parts = [
            content.get('title', ''),
            content.get('category', ''),
            ' '.join(content.get('tags', [])),
            content.get('description', '')
        ]
        return ' '.join(filter(None, parts))
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return float(dot_product / (norm_vec1 * norm_vec2))
    
    def embedding_to_list(self, embedding: np.ndarray) -> list:
        """Convert numpy array to list for storage"""
        return embedding.tolist()
    
    def list_to_embedding(self, embedding_list: list) -> np.ndarray:
        """Convert stored list back to numpy array"""
        return np.array(embedding_list)
