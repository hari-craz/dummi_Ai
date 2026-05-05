"""
SQLAlchemy ORM models and database engine configuration
for Dummi AI Content Recommendation System.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, create_engine
)
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from app.config import Config

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ORM Models ──────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    interests = Column(Text, default="[]")        # JSON array
    skill_level = Column(String, default="beginner")
    history = Column(Text, default="[]")           # JSON array of content_ids
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, index=True)
    tags = Column(Text, default="[]")              # JSON array
    description = Column(Text, default="")
    embedding_vector = Column(Text, default=None)  # JSON 384-dim float list
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    content_id = Column(String, index=True, nullable=False)
    interaction_type = Column(String, nullable=False)   # click | like | skip | view_time
    duration_seconds = Column(Integer, default=None)
    rating = Column(Float, default=None)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class CFModel(Base):
    __tablename__ = "cf_models"

    id = Column(Integer, primary_key=True, index=True)
    model_data = Column(Text, nullable=False)      # JSON serialised factors & maps
    trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    n_users = Column(Integer, default=0)
    n_items = Column(Integer, default=0)
    rmse = Column(Float, default=None)
