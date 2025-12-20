from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import UserCreate, UserResponse, UserUpdate
from app.models.database import get_db
from app.db import crud

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing_user = crud.get_user(db, user.user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    return crud.create_user(db, user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list)
def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    return crud.get_all_users(db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.interests:
        crud.update_user_interests(db, user_id, user_update.interests)
    
    return crud.get_user(db, user_id)
