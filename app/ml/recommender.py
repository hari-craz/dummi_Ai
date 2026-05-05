"""
Hybrid Recommender — combines embedding similarity, collaborative
filtering, and interest-based matching with cold-start handling.
"""

import json
import logging
import numpy as np
from sqlalchemy.orm import Session

from app.config import Config
from app.db import crud
from app.ml.embeddings import EmbeddingManager
from app.ml.vector_search import VectorDatabase
from app.ml.collaborative_filtering import CollaborativeFiltering

logger = logging.getLogger(__name__)


class HybridRecommender:
    """End-to-end recommendation pipeline."""

    def __init__(self):
        self.embeddings = EmbeddingManager()
        self.vector_db = VectorDatabase()
        self.cf_model: CollaborativeFiltering | None = None
        self.config = Config

    # ── Public API ───────────────────────────────────────────

    def recommend(
        self,
        db: Session,
        user_id: str,
        n_recommendations: int = 10,
        use_cf: bool = True,
        use_embeddings: bool = True,
        cf_weight: float = 0.5,
    ) -> list[dict]:
        """
        Return a ranked list of recommendation dicts:
        [{content_id, title, category, score, method}, ...]
        """
        user = crud.get_user(db, user_id)
        if not user:
            return []

        interactions = crud.get_user_interactions(db, user_id)
        interacted_ids = {i.content_id for i in interactions}
        is_cold_start = len(interactions) < self.config.COLD_START_THRESHOLD

        if is_cold_start:
            return self._cold_start_recommend(db, user, interacted_ids, n_recommendations)

        scores: dict[str, dict] = {}  # content_id → {score, method, ...}

        # Embedding-based scores
        if use_embeddings and self.vector_db.index.ntotal > 0:
            emb_scores = self._embedding_scores(user, n_recommendations * 3)
            for cid, sim in emb_scores.items():
                if cid not in interacted_ids:
                    scores[cid] = {"emb_score": sim, "cf_score": 0.0}

        # Collaborative-filtering scores
        if use_cf and self.cf_model is not None:
            cf_scores = self.cf_model.predict_all_for_user(user_id)
            if cf_scores:
                max_cf = max(cf_scores.values()) or 1.0
                for cid, raw in cf_scores.items():
                    if cid not in interacted_ids:
                        norm = raw / max_cf  # normalise to 0-1
                        if cid in scores:
                            scores[cid]["cf_score"] = norm
                        else:
                            scores[cid] = {"emb_score": 0.0, "cf_score": norm}

        # Hybrid combination
        for cid, s in scores.items():
            if use_cf and use_embeddings:
                s["score"] = cf_weight * s["cf_score"] + (1 - cf_weight) * s["emb_score"]
                s["method"] = "hybrid"
            elif use_cf:
                s["score"] = s["cf_score"]
                s["method"] = "collaborative"
            else:
                s["score"] = s["emb_score"]
                s["method"] = "embedding"

        # If we still have no scores, fall back to cold-start
        if not scores:
            return self._cold_start_recommend(db, user, interacted_ids, n_recommendations)

        # Sort and enrich
        ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:n_recommendations]
        results = []
        for cid, meta in ranked:
            content = crud.get_content(db, cid)
            results.append({
                "content_id": cid,
                "title": content.title if content else cid,
                "category": content.category if content else "",
                "score": round(meta["score"], 4),
                "method": meta["method"],
            })
        return results

    # ── Training helpers ─────────────────────────────────────

    def generate_all_embeddings(self, db: Session) -> int:
        """Generate embeddings for every content item and rebuild the FAISS index."""
        all_content = crud.get_all_content(db)
        if not all_content:
            return 0

        texts = [self.embeddings.get_content_embedding_text(c) for c in all_content]
        vectors = self.embeddings.generate_embeddings_batch(texts)
        ids = [c.content_id for c in all_content]

        # Reset and rebuild index
        self.vector_db.reset_index()
        self.vector_db.add_vectors(vectors, ids)
        self.vector_db.save_index()

        # Store embeddings in DB too
        for content, vec in zip(all_content, vectors):
            crud.update_content_embedding(db, content.content_id, vec.tolist())

        logger.info("Generated embeddings for %d content items", len(all_content))
        return len(all_content)

    def train_cf_model(self, db: Session) -> CollaborativeFiltering | None:
        """Train collaborative filtering model from all interactions."""
        interactions = crud.get_all_interactions(db)
        if not interactions:
            logger.warning("No interactions found — skipping CF training")
            return None

        cf = CollaborativeFiltering()
        result = cf.train(interactions)
        if result is None:
            logger.warning("Not enough data for CF training")
            return None

        self.cf_model = cf
        logger.info(
            "CF model trained — %d users, %d items, RMSE=%.4f",
            len(cf.user_map), len(cf.item_map), cf.rmse or 0,
        )
        return cf

    # ── Private helpers ──────────────────────────────────────

    def _embedding_scores(self, user, k: int) -> dict[str, float]:
        """Query FAISS with the user's interest embedding."""
        interests = json.loads(user.interests)
        if not interests:
            return {}
        query_text = " ".join(interests)
        query_vec = self.embeddings.generate_embedding(query_text)
        results = self.vector_db.search_similar(query_vec, k)

        # Convert L2 distance → similarity score (1 / (1 + dist))
        scores = {}
        for cid, dist in results:
            scores[cid] = 1.0 / (1.0 + dist)
        return scores

    def _cold_start_recommend(self, db, user, interacted_ids, n) -> list[dict]:
        """Interest-based recommendations for new users."""
        interests = json.loads(user.interests)
        all_content = crud.get_all_content(db)
        if not all_content:
            return []

        scored = []
        for content in all_content:
            if content.content_id in interacted_ids:
                continue
            tags = json.loads(content.tags) if content.tags else []
            # Score = number of interest/tag overlaps + category match
            overlap = len(set(interests) & set(tags))
            if content.category and content.category in interests:
                overlap += 1
            scored.append((content, overlap))

        # If we have embeddings, add similarity-based boost
        if self.vector_db.index.ntotal > 0 and interests:
            emb_scores = self._embedding_scores(user, n * 3)
            for i, (content, tag_score) in enumerate(scored):
                emb_sim = emb_scores.get(content.content_id, 0.0)
                scored[i] = (content, tag_score + emb_sim)

        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for content, score in scored[:n]:
            results.append({
                "content_id": content.content_id,
                "title": content.title,
                "category": content.category,
                "score": round(float(score), 4),
                "method": "cold_start",
            })
        return results
