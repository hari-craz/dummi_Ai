from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import ContentCreate, ContentResponse
from app.models.database import get_db
from app.db import crud
import json

router = APIRouter(prefix="/content", tags=["content"])

def content_to_response(content):
    """Convert database content to response model"""
    return ContentResponse(
        content_id=content.content_id,
        title=content.title,
        category=content.category,
        tags=json.loads(content.tags) if content.tags else [],
        description=content.description,
        embedding_vector=json.loads(content.embedding_vector) if content.embedding_vector else None,
        created_at=content.created_at
    )

@router.post("/", response_model=ContentResponse)
def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    """Create new content"""
    existing = crud.get_content(db, content.content_id)
    if existing:
        raise HTTPException(status_code=400, detail="Content already exists")
    
    db_content = crud.create_content(db, content)
    return content_to_response(db_content)

@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: str, db: Session = Depends(get_db)):
    """Get content by ID"""
    content = crud.get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content_to_response(content)

@router.get("/", response_model=list)
def get_all_content(db: Session = Depends(get_db)):
    """Get all content"""
    contents = crud.get_all_content(db)
    return [content_to_response(content) for content in contents]

@router.get("/category/{category}", response_model=list)
def get_content_by_category(category: str, db: Session = Depends(get_db)):
    """Get content by category"""
    contents = crud.get_content_by_category(db, category)
    return [content_to_response(content) for content in contents]
