from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import UserCreate, UserResponse, UserUpdate
from app.models.database import get_db
from app.db import crud
import json

router = APIRouter(prefix="/users", tags=["users"])

def user_to_response(user):
    """Convert database user to response model"""
    return UserResponse(
        user_id=user.user_id,
        interests=json.loads(user.interests),
        skill_level=user.skill_level,
        history=json.loads(user.history),
        created_at=user.created_at
    )

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing_user = crud.get_user(db, user.user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_user = crud.create_user(db, user)
    return user_to_response(db_user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_response(user)

@router.get("/", response_model=list)
def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = crud.get_all_users(db)
    return [user_to_response(user) for user in users]

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.interests:
        crud.update_user_interests(db, user_id, user_update.interests)
    
    return user_to_response(crud.get_user(db, user_id))
