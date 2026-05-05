"""
CRUD (Create, Read, Update, Delete) operations for the Dummi AI database.
All functions referenced by the API route handlers.
"""

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.database import User, Content, Interaction, UserPreference, CFModel


# ── Users ────────────────────────────────────────────────────


def create_user(db: Session, user_data):
    """Create a new user from a UserCreate schema."""
    db_user = User(
        user_id=user_data.user_id,
        interests=json.dumps(user_data.interests),
        skill_level=user_data.skill_level,
        history=json.dumps([]),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str):
    """Return a user by user_id or None."""
    return db.query(User).filter(User.user_id == user_id).first()


def get_all_users(db: Session):
    """Return every user."""
    return db.query(User).all()


def update_user_interests(db: Session, user_id: str, interests: list):
    """Replace a user's interests list."""
    user = get_user(db, user_id)
    if user:
        user.interests = json.dumps(interests)
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
    return user


def add_to_user_history(db: Session, user_id: str, content_id: str):
    """Append a content_id to the user's history (deduped)."""
    user = get_user(db, user_id)
    if user:
        history = json.loads(user.history)
        if content_id not in history:
            history.append(content_id)
            user.history = json.dumps(history)
            user.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
    return user


# ── Content ──────────────────────────────────────────────────


def create_content(db: Session, content_data):
    """Create a new content item from a ContentCreate schema."""
    db_content = Content(
        content_id=content_data.content_id,
        title=content_data.title,
        category=content_data.category,
        tags=json.dumps(content_data.tags),
        description=content_data.description or "",
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content


def get_content(db: Session, content_id: str):
    """Return a content item by content_id or None."""
    return db.query(Content).filter(Content.content_id == content_id).first()


def get_all_content(db: Session):
    """Return every content item."""
    return db.query(Content).all()


def get_content_by_category(db: Session, category: str):
    """Return content items filtered by category."""
    return db.query(Content).filter(Content.category == category).all()


def update_content_embedding(db: Session, content_id: str, embedding: list):
    """Store the embedding vector (as JSON) for a content item."""
    content = get_content(db, content_id)
    if content:
        content.embedding_vector = json.dumps(embedding)
        content.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(content)
    return content


# ── Interactions ─────────────────────────────────────────────


def create_interaction(db: Session, interaction_data):
    """Record a user-content interaction."""
    db_interaction = Interaction(
        user_id=interaction_data.user_id,
        content_id=interaction_data.content_id,
        interaction_type=interaction_data.interaction_type,
        duration_seconds=getattr(interaction_data, "duration_seconds", None),
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    # Also update user history
    add_to_user_history(db, interaction_data.user_id, interaction_data.content_id)
    return db_interaction


def get_user_interactions(db: Session, user_id: str):
    """Return all interactions for a given user."""
    return db.query(Interaction).filter(Interaction.user_id == user_id).all()


def get_all_interactions(db: Session):
    """Return every interaction."""
    return db.query(Interaction).all()


# ── User Preferences ────────────────────────────────────────


def update_user_preference(db: Session, user_id: str, category: str, delta: float):
    """Increment/decrement a category preference score for a user."""
    pref = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id, UserPreference.category == category)
        .first()
    )
    if pref:
        pref.score += delta
        pref.updated_at = datetime.now(timezone.utc)
    else:
        pref = UserPreference(user_id=user_id, category=category, score=max(delta, 0))
        db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


# ── CF Models ────────────────────────────────────────────────


def save_cf_model(db: Session, model_data: dict, n_users: int, n_items: int, rmse: float = None):
    """Persist a trained collaborative-filtering model."""
    cf = CFModel(
        model_data=json.dumps(model_data),
        n_users=n_users,
        n_items=n_items,
        rmse=rmse,
    )
    db.add(cf)
    db.commit()
    db.refresh(cf)
    return cf


def get_latest_cf_model(db: Session):
    """Return the most recently trained CF model, or None."""
    return db.query(CFModel).order_by(CFModel.trained_at.desc()).first()
