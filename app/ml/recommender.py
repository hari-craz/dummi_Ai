import numpy as np
from typing import List, Tuple, Dict
from sqlalchemy.orm import Session
from app.ml.embeddings import EmbeddingManager
from app.ml.vector_search import VectorDatabase
from app.ml.collaborative_filtering import CollaborativeFiltering
from app.db.crud import get_user, get_all_content, get_user_interactions, get_interaction_matrix
from app.config import Config
import json

class HybridRecommender:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.vector_db = VectorDatabase()
        self.cf_model = CollaborativeFiltering(
            n_factors=Config.N_FACTORS,
            n_epochs=Config.N_EPOCHS,
            learning_rate=Config.LEARNING_RATE
        )
    
    def recommend(self, db: Session, user_id: str, n_recommendations: int = 10,
                  use_cf: bool = True, use_embeddings: bool = True, 
                  cf_weight: float = 0.5) -> List[Dict]:
        """Hybrid recommendation combining embeddings and collaborative filtering"""
        
        user = get_user(db, user_id)
        if not user:
            return []
        
        # Get user's interaction history
        user_interactions = get_user_interactions(db, user_id)
        user_interacted_items = set(inter.content_id for inter in user_interactions)
        
        # Check if cold-start user
        is_cold_start = len(user_interactions) < Config.COLD_START_THRESHOLD
        
        recommendations = {}
        
        # 1. Embedding-based recommendations
        if use_embeddings and not is_cold_start:
            embedding_recs = self._get_embedding_based_recommendations(
                db, user_id, user_interacted_items, n_recommendations * 2
            )
            for content_id, score in embedding_recs:
                recommendations[content_id] = recommendations.get(content_id, 0) + score * (1 - cf_weight)
        
        # 2. Collaborative filtering recommendations
        if use_cf and not is_cold_start:
            cf_recs = self.cf_model.recommend_for_user(
                user_id, n_recommendations * 2, user_interacted_items
            )
            for content_id, score in cf_recs:
                # Normalize CF scores to 0-1
                cf_scores = [s for _, s in cf_recs]
                min_score = np.min(cf_scores) if cf_scores else 0
                max_score = np.max(cf_scores) if cf_scores else 1
                normalized_score = (score - min_score) / (max_score - min_score + 1e-10)
                recommendations[content_id] = recommendations.get(content_id, 0) + normalized_score * cf_weight
        
        # 3. Content-based on interests (for cold-start users)
        if is_cold_start or not recommendations:
            interest_recs = self._get_interest_based_recommendations(
                db, user, user_interacted_items, n_recommendations * 2
            )
            for content_id, score in interest_recs:
                recommendations[content_id] = recommendations.get(content_id, 0) + score
        
        # Sort and return top N
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for content_id, score in sorted_recs[:n_recommendations]:
            content = next((c for c in get_all_content(db) if c.content_id == content_id), None)
            if content:
                result.append({
                    'content_id': content_id,
                    'title': content.title,
                    'category': content.category,
                    'score': float(score),
                    'method': 'hybrid'
                })
        
        return result
    
    def _get_embedding_based_recommendations(self, db: Session, user_id: str,
                                            user_interacted_items: set,
                                            n_recommendations: int) -> List[Tuple[str, float]]:
        """Get recommendations based on content similarity to user's interests"""
        user = get_user(db, user_id)
        if not user or not user.interests:
            return []
        
        # Generate user profile embedding from interests
        user_interests = json.loads(user.interests)
        user_interests_text = ' '.join(user_interests)
        user_embedding = self.embedding_manager.generate_embedding(user_interests_text)
        
        # Search for similar content
        similar_content = self.vector_db.search_similar(user_embedding, n_recommendations)
        
        # Filter out already interacted items
        recommendations = []
        for content_id, similarity in similar_content:
            if content_id not in user_interacted_items and similarity >= Config.SIMILARITY_THRESHOLD:
                recommendations.append((content_id, similarity))
        
        return recommendations
    
    def _get_interest_based_recommendations(self, db: Session, user,
                                           user_interacted_items: set,
                                           n_recommendations: int) -> List[Tuple[str, float]]:
        """Content-based recommendations using user interests"""
        all_content = get_all_content(db)
        recommendations = {}
        
        for content in all_content:
            if content.content_id in user_interacted_items:
                continue
            
            # Calculate interest match score
            content_tags = set(json.loads(content.tags)) if content.tags else set()
            user_interests = set(json.loads(user.interests)) if user.interests else set()
            
            if not user_interests:
                continue
            
            overlap = len(content_tags & user_interests)
            score = overlap / len(user_interests) if user_interests else 0
            
            if score > 0:
                recommendations[content.content_id] = score
        
        # Convert to list and sort
        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
    
    def train_cf_model(self, db: Session):
        """Train collaborative filtering model"""
        interactions = get_interaction_matrix(db)
        if not interactions:
            return None
        
        matrix, user_map, item_map = self.cf_model.build_interaction_matrix(interactions)
        
        if matrix.size == 0:
            return None
        
        self.cf_model.train(matrix)
        return self.cf_model
    
    def generate_all_embeddings(self, db: Session):
        """Generate embeddings for all content"""
        all_content = get_all_content(db)
        
        if not all_content:
            return 0
        
        content_texts = []
        content_ids = []
        
        for content in all_content:
            text = self.embedding_manager.get_content_embedding_text({
                'title': content.title,
                'category': content.category,
                'tags': json.loads(content.tags) if content.tags else [],
                'description': content.description
            })
            content_texts.append(text)
            content_ids.append(content.content_id)
        
        # Generate embeddings
        embeddings = self.embedding_manager.generate_embeddings_batch(content_texts)
        
        # Add to vector database
        self.vector_db.add_vectors(embeddings, content_ids)
        self.vector_db.save_index()
        
        return len(content_ids)
