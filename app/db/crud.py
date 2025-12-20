from sqlalchemy.orm import Session
from app.models.database import User, Content, Interaction, UserPreference, CFModel
from app.models.schemas import UserCreate, ContentCreate, InteractionCreate
from datetime import datetime

# ========== USER OPERATIONS ==========
def create_user(db: Session, user: UserCreate):
    db_user = User(
        user_id=user.user_id,
        interests=user.interests,
        skill_level=user.skill_level,
        history=[]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def update_user_interests(db: Session, user_id: str, interests: list):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.interests = interests
        user.updated_at = datetime.utcnow()
        db.commit()
    return user

def add_to_user_history(db: Session, user_id: str, content_id: str):
    user = get_user(db, user_id)
    if user:
        if content_id not in user.history:
            user.history.append(content_id)
            user.updated_at = datetime.utcnow()
            db.commit()
    return user

# ========== CONTENT OPERATIONS ==========
def create_content(db: Session, content: ContentCreate):
    db_content = Content(
        content_id=content.content_id,
        title=content.title,
        category=content.category,
        tags=content.tags,
        description=content.description,
        embedding_vector=None
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def get_content(db: Session, content_id: str):
    return db.query(Content).filter(Content.content_id == content_id).first()

def get_all_content(db: Session):
    return db.query(Content).all()

def get_content_by_category(db: Session, category: str):
    return db.query(Content).filter(Content.category == category).all()

def update_content_embedding(db: Session, content_id: str, embedding: list):
    content = get_content(db, content_id)
    if content:
        content.embedding_vector = embedding
        content.updated_at = datetime.utcnow()
        db.commit()
    return content

# ========== INTERACTION OPERATIONS ==========
def create_interaction(db: Session, interaction: InteractionCreate):
    db_interaction = Interaction(
        user_id=interaction.user_id,
        content_id=interaction.content_id,
        interaction_type=interaction.interaction_type,
        duration_seconds=interaction.duration_seconds
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    
    # Add to user history
    add_to_user_history(db, interaction.user_id, interaction.content_id)
    
    return db_interaction

def get_user_interactions(db: Session, user_id: str, limit: int = 100):
    return db.query(Interaction).filter(
        Interaction.user_id == user_id
    ).order_by(Interaction.timestamp.desc()).limit(limit).all()

def get_content_interactions(db: Session, content_id: str):
    return db.query(Interaction).filter(Interaction.content_id == content_id).all()

def get_all_interactions(db: Session):
    return db.query(Interaction).all()

def get_interaction_matrix(db: Session):
    """Get user-item interaction matrix as list of (user_id, content_id, rating)"""
    interactions = db.query(
        Interaction.user_id,
        Interaction.content_id,
        Interaction.interaction_type
    ).all()
    return interactions

# ========== USER PREFERENCE OPERATIONS ==========
def update_user_preference(db: Session, user_id: str, category: str, score: float):
    pref = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.category == category
    ).first()
    
    if pref:
        pref.score = score
        pref.updated_at = datetime.utcnow()
    else:
        pref = UserPreference(user_id=user_id, category=category, score=score)
        db.add(pref)
    
    db.commit()
    return pref

def get_user_preferences(db: Session, user_id: str):
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).all()

# ========== CF MODEL OPERATIONS ==========
def save_cf_model(db: Session, model_data: dict, n_users: int, n_items: int, rmse: float = None):
    cf_model = CFModel(
        model_data=model_data,
        n_users=n_users,
        n_items=n_items,
        rmse=rmse
    )
    db.add(cf_model)
    db.commit()
    db.refresh(cf_model)
    return cf_model

def get_latest_cf_model(db: Session):
    return db.query(CFModel).order_by(CFModel.trained_at.desc()).first()
