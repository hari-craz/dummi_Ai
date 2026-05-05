"""
Collaborative Filtering — Non-negative Matrix Factorization (NMF)
for predicting user-item affinity scores.
"""

import json
import numpy as np
from sklearn.decomposition import NMF
from sklearn.metrics import mean_squared_error
from app.config import Config


# Interaction-type to weight mapping
INTERACTION_WEIGHTS = {
    "like": 5.0,
    "click": 2.0,
    "view_time": 1.0,
    "skip": 0.1,   # NMF requires non-negative — use a small positive instead of -1
}


class CollaborativeFiltering:
    """Train and use an NMF model for collaborative filtering predictions."""

    def __init__(self):
        self.n_factors = Config.N_FACTORS        # 50
        self.n_epochs = Config.N_EPOCHS          # 20 (max_iter for NMF)
        self.user_factors = None                 # (n_users, 50)
        self.item_factors = None                 # (n_items, 50)
        self.user_map: dict[str, int] = {}       # user_id → row index
        self.item_map: dict[str, int] = {}       # content_id → col index
        self.rmse: float | None = None

    # ── Training ─────────────────────────────────────────────

    def train(self, interactions: list):
        """
        Build user-item matrix from interaction records and factorise via NMF.
        interactions: list of objects with user_id, content_id, interaction_type.
        Returns self or None if not enough data.
        """
        if not interactions:
            return None

        # Build maps
        users = sorted(set(i.user_id for i in interactions))
        items = sorted(set(i.content_id for i in interactions))
        self.user_map = {uid: idx for idx, uid in enumerate(users)}
        self.item_map = {cid: idx for idx, cid in enumerate(items)}

        n_users = len(users)
        n_items = len(items)

        if n_users < 2 or n_items < 2:
            return None

        # Build interaction matrix
        matrix = np.zeros((n_users, n_items), dtype=np.float32)
        for inter in interactions:
            u = self.user_map[inter.user_id]
            i = self.item_map[inter.content_id]
            weight = INTERACTION_WEIGHTS.get(inter.interaction_type, 1.0)
            matrix[u, i] += weight

        # Ensure non-negative
        matrix = np.clip(matrix, 0, None)

        # NMF factorisation
        model = NMF(
            n_components=min(self.n_factors, min(n_users, n_items)),
            init="random",
            random_state=42,
            max_iter=self.n_epochs * 10,  # sklearn iter ≠ epoch
            solver="cd",
        )
        self.user_factors = model.fit_transform(matrix)
        self.item_factors = model.components_.T  # (n_items, n_factors)

        # Compute RMSE on non-zero entries
        reconstructed = self.user_factors @ self.item_factors.T
        mask = matrix > 0
        if mask.sum() > 0:
            self.rmse = float(np.sqrt(mean_squared_error(
                matrix[mask], reconstructed[mask]
            )))
        else:
            self.rmse = None

        return self

    # ── Prediction ───────────────────────────────────────────

    def predict(self, user_id: str, content_id: str) -> float:
        """Predict affinity score for a (user, item) pair."""
        if (
            self.user_factors is None
            or user_id not in self.user_map
            or content_id not in self.item_map
        ):
            return 0.0
        u = self.user_map[user_id]
        i = self.item_map[content_id]
        return float(np.dot(self.user_factors[u], self.item_factors[i]))

    def predict_all_for_user(self, user_id: str) -> dict[str, float]:
        """Return {content_id: score} for every item for a user."""
        if self.user_factors is None or user_id not in self.user_map:
            return {}
        u = self.user_map[user_id]
        scores = self.user_factors[u] @ self.item_factors.T
        return {cid: float(scores[idx]) for cid, idx in self.item_map.items()}

    # ── Serialisation ────────────────────────────────────────

    def get_model_data(self) -> dict:
        """Serialise the model for database storage."""
        return {
            "user_factors": self.user_factors.tolist(),
            "item_factors": self.item_factors.tolist(),
            "user_map": self.user_map,
            "item_map": self.item_map,
            "rmse": self.rmse,
        }

    def load_model_data(self, data: dict):
        """Restore model from deserialised data."""
        if isinstance(data, str):
            data = json.loads(data)
        self.user_factors = np.array(data["user_factors"], dtype=np.float32)
        self.item_factors = np.array(data["item_factors"], dtype=np.float32)
        self.user_map = data["user_map"]
        self.item_map = data["item_map"]
        self.rmse = data.get("rmse")
        return self
