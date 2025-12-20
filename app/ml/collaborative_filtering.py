import numpy as np
from sklearn.decomposition import NMF
from typing import Tuple, Dict, List
import json

class CollaborativeFiltering:
    def __init__(self, n_factors: int = 50, n_epochs: int = 20, learning_rate: float = 0.01):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.learning_rate = learning_rate
        self.user_factors = None
        self.item_factors = None
        self.user_map = {}
        self.item_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
    
    def build_interaction_matrix(self, interactions: List[Tuple[str, str, str]]) -> Tuple[np.ndarray, dict, dict]:
        """Build user-item interaction matrix from interaction data
        interactions: [(user_id, content_id, interaction_type), ...]
        Returns: (matrix, user_map, item_map)
        """
        # Create mappings
        unique_users = list(set(u for u, _, _ in interactions))
        unique_items = list(set(i for _, i, _ in interactions))
        
        self.user_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.item_map = {iid: idx for idx, iid in enumerate(unique_items)}
        self.reverse_user_map = {idx: uid for uid, idx in self.user_map.items()}
        self.reverse_item_map = {idx: iid for iid, idx in self.item_map.items()}
        
        # Build matrix
        n_users = len(unique_users)
        n_items = len(unique_items)
        matrix = np.zeros((n_users, n_items))
        
        # Weight interactions
        interaction_weights = {
            'like': 5.0,
            'click': 2.0,
            'view_time': 1.0,
            'skip': -1.0
        }
        
        for user_id, item_id, interaction_type in interactions:
            u_idx = self.user_map.get(user_id)
            i_idx = self.item_map.get(item_id)
            if u_idx is not None and i_idx is not None:
                weight = interaction_weights.get(interaction_type, 1.0)
                matrix[u_idx, i_idx] += weight
        
        return matrix, self.user_map, self.item_map
    
    def train(self, matrix: np.ndarray):
        """Train CF model using NMF"""
        # Initialize with small random values
        np.random.seed(42)
        
        # Use sklearn's NMF for matrix factorization
        nmf = NMF(
            n_components=self.n_factors,
            init='random',
            random_state=42,
            max_iter=self.n_epochs
        )
        
        self.user_factors = nmf.fit_transform(matrix)
        self.item_factors = nmf.components_.T
        
        return self.user_factors, self.item_factors
    
    def predict_rating(self, user_id: str, item_id: str) -> float:
        """Predict rating for user-item pair"""
        if self.user_factors is None or self.item_factors is None:
            return 0.0
        
        u_idx = self.user_map.get(user_id)
        i_idx = self.item_map.get(item_id)
        
        if u_idx is None or i_idx is None:
            return 0.0
        
        rating = np.dot(self.user_factors[u_idx], self.item_factors[i_idx])
        return float(rating)
    
    def recommend_for_user(self, user_id: str, n_recommendations: int = 10, 
                          user_interacted_items: set = None) -> List[Tuple[str, float]]:
        """Get top-N recommendations for a user"""
        if self.user_factors is None or self.item_factors is None:
            return []
        
        u_idx = self.user_map.get(user_id)
        if u_idx is None:
            return []
        
        # Get predicted ratings for all items
        predictions = np.dot(self.user_factors[u_idx], self.item_factors.T)
        
        # Rank items
        top_item_indices = np.argsort(predictions)[::-1]
        
        recommendations = []
        if user_interacted_items is None:
            user_interacted_items = set()
        
        for idx in top_item_indices:
            item_id = self.reverse_item_map.get(idx)
            if item_id and item_id not in user_interacted_items:
                rating = float(predictions[idx])
                recommendations.append((item_id, rating))
                if len(recommendations) >= n_recommendations:
                    break
        
        return recommendations
    
    def find_similar_users(self, user_id: str, n_similar: int = 5) -> List[Tuple[str, float]]:
        """Find similar users based on factor vectors"""
        if self.user_factors is None:
            return []
        
        u_idx = self.user_map.get(user_id)
        if u_idx is None:
            return []
        
        user_vector = self.user_factors[u_idx]
        
        # Calculate cosine similarity with all users
        similarities = []
        for idx, other_vector in enumerate(self.user_factors):
            if idx != u_idx:
                sim = self._cosine_similarity(user_vector, other_vector)
                other_user_id = self.reverse_user_map.get(idx)
                if other_user_id:
                    similarities.append((other_user_id, sim))
        
        # Return top N similar users
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_similar]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return float(dot_product / (norm_vec1 * norm_vec2))
    
    def get_model_data(self) -> dict:
        """Serialize model for storage"""
        return {
            'user_factors': self.user_factors.tolist() if self.user_factors is not None else None,
            'item_factors': self.item_factors.tolist() if self.item_factors is not None else None,
            'user_map': self.user_map,
            'item_map': self.item_map,
            'n_factors': self.n_factors
        }
    
    def load_model_data(self, data: dict):
        """Load model from serialized data"""
        self.user_factors = np.array(data['user_factors']) if data['user_factors'] else None
        self.item_factors = np.array(data['item_factors']) if data['item_factors'] else None
        self.user_map = data['user_map']
        self.item_map = data['item_map']
        self.reverse_user_map = {idx: uid for uid, idx in self.user_map.items()}
        self.reverse_item_map = {idx: iid for iid, idx in self.item_map.items()}
