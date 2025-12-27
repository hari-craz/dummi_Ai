from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    interests = Column(Text)  # JSON string of interests
    skill_level = Column(String)  # beginner, intermediate, advanced
    history = Column(Text)  # JSON string of content_ids viewed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True)
    title = Column(String)
    category = Column(String, index=True)
    tags = Column(Text)  # JSON string of tags
    description = Column(Text, nullable=True)
    embedding_vector = Column(Text, nullable=True)  # JSON string of embedding vector
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="content")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), index=True)
    content_id = Column(String, ForeignKey("content.content_id"), index=True)
    interaction_type = Column(String)  # click, like, skip, view_time
    duration_seconds = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)  # 1-5 rating from feedback
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), index=True)
    category = Column(String)
    score = Column(Float)  # Computed preference score
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")

class CFModel(Base):
    __tablename__ = "cf_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_data = Column(Text)  # JSON string of serialized CF model parameters
    trained_at = Column(DateTime, default=datetime.utcnow)
    n_users = Column(Integer)
    n_items = Column(Integer)
    rmse = Column(Float, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
