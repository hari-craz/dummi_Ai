from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.schemas import RecommendationRequest, RecommendationResponse, InteractionCreate, FeedbackRequest
from app.models.database import get_db
from app.db import crud
from app.ml.recommender import HybridRecommender

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Initialize recommender
recommender = HybridRecommender()

@router.post("/", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    """Get personalized recommendations for a user"""
    user = crud.get_user(db, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    recommendations = recommender.recommend(
        db,
        req.user_id,
        n_recommendations=req.n_recommendations,
        use_cf=req.use_cf,
        use_embeddings=req.use_embeddings,
        cf_weight=req.cf_weight
    )
    
    return RecommendationResponse(
        user_id=req.user_id,
        recommendations=recommendations,
        timestamp=datetime.utcnow()
    )

@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """Record user feedback on recommendations"""
    interaction_type = feedback.feedback_type
    
    # Map feedback to interaction type
    if feedback.feedback_type == "positive":
        interaction_type = "like"
    elif feedback.feedback_type == "negative":
        interaction_type = "skip"
    else:
        interaction_type = "click"
    
    interaction = InteractionCreate(
        user_id=feedback.user_id,
        content_id=feedback.content_id,
        interaction_type=interaction_type
    )
    
    crud.create_interaction(db, interaction)
    
    return {"status": "feedback recorded", "user_id": feedback.user_id, "content_id": feedback.content_id}

@router.post("/interact")
def record_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    """Record user interaction with content"""
    user = crud.get_user(db, interaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    content = crud.get_content(db, interaction.content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    recorded = crud.create_interaction(db, interaction)
    
    return {
        "status": "interaction recorded",
        "interaction_id": recorded.id,
        "interaction_type": recorded.interaction_type
    }
