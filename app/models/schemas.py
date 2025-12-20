from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    user_id: str
    interests: List[str]
    skill_level: str

class UserUpdate(BaseModel):
    interests: Optional[List[str]] = None
    skill_level: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    interests: List[str]
    skill_level: str
    history: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Content Schemas
class ContentCreate(BaseModel):
    content_id: str
    title: str
    category: str
    tags: List[str]
    description: Optional[str] = None

class ContentResponse(BaseModel):
    content_id: str
    title: str
    category: str
    tags: List[str]
    description: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Interaction Schemas
class InteractionCreate(BaseModel):
    user_id: str
    content_id: str
    interaction_type: str  # click, like, skip, view_time
    duration_seconds: Optional[int] = None

class InteractionResponse(BaseModel):
    interaction_id: int
    user_id: str
    content_id: str
    interaction_type: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationRequest(BaseModel):
    user_id: str
    n_recommendations: int = 10
    use_cf: bool = True  # Use collaborative filtering
    use_embeddings: bool = True  # Use embedding similarity
    cf_weight: float = 0.5  # Weight for CF vs embeddings

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[dict]  # [{content_id, title, score, method}]
    timestamp: datetime

# Feedback Schemas
class FeedbackRequest(BaseModel):
    user_id: str
    content_id: str
    feedback_type: str  # positive, negative, neutral

# Training Schemas
class TrainingRequest(BaseModel):
    retrain_cf: bool = True
    regenerate_embeddings: bool = False

class TrainingResponse(BaseModel):
    status: str
    message: str
    embeddings_generated: int
    cf_model_trained: bool
    timestamp: datetime
