from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import ContentCreate, ContentResponse
from app.models.database import get_db
from app.db import crud

router = APIRouter(prefix="/content", tags=["content"])

@router.post("/", response_model=ContentResponse)
def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    """Create new content"""
    existing = crud.get_content(db, content.content_id)
    if existing:
        raise HTTPException(status_code=400, detail="Content already exists")
    
    return crud.create_content(db, content)

@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: str, db: Session = Depends(get_db)):
    """Get content by ID"""
    content = crud.get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.get("/", response_model=list)
def get_all_content(db: Session = Depends(get_db)):
    """Get all content"""
    return crud.get_all_content(db)

@router.get("/category/{category}", response_model=list)
def get_content_by_category(category: str, db: Session = Depends(get_db)):
    """Get content by category"""
    return crud.get_content_by_category(db, category)
