from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.schemas import TrainingRequest, TrainingResponse
from app.models.database import get_db
from app.db import crud
from app.ml.recommender import HybridRecommender

router = APIRouter(prefix="/training", tags=["training"])

recommender = HybridRecommender()

@router.post("/train", response_model=TrainingResponse)
def train_models(req: TrainingRequest, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    """Train ML models"""
    embeddings_generated = 0
    cf_trained = False
    
    # Generate embeddings
    if req.regenerate_embeddings:
        embeddings_generated = recommender.generate_all_embeddings(db)
    
    # Train CF model
    if req.retrain_cf:
        cf_model = recommender.train_cf_model(db)
        if cf_model:
            cf_trained = True
            # Save model
            model_data = cf_model.get_model_data()
            crud.save_cf_model(db, model_data, len(cf_model.user_map), len(cf_model.item_map))
    
    return TrainingResponse(
        status="completed",
        message="Model training completed",
        embeddings_generated=embeddings_generated,
        cf_model_trained=cf_trained,
        timestamp=datetime.utcnow()
    )

@router.get("/status")
def get_training_status(db: Session = Depends(get_db)):
    """Get current model training status"""
    vector_stats = recommender.vector_db.get_index_stats()
    cf_model = crud.get_latest_cf_model(db)
    
    return {
        "vector_db": vector_stats,
        "cf_model": {
            "trained": cf_model is not None,
            "trained_at": cf_model.trained_at if cf_model else None,
            "n_users": cf_model.n_users if cf_model else 0,
            "n_items": cf_model.n_items if cf_model else 0,
            "rmse": cf_model.rmse if cf_model else None
        }
    }
