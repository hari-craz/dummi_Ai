import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db
from app.models.schemas import UserCreate, ContentCreate, InteractionCreate

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Tests
def test_create_user():
    response = client.post(
        "/users/",
        json={
            "user_id": "test_user",
            "interests": ["ml", "python"],
            "skill_level": "beginner"
        }
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_user"

def test_get_user():
    # Create first
    client.post(
        "/users/",
        json={
            "user_id": "test_user2",
            "interests": ["ml"],
            "skill_level": "intermediate"
        }
    )
    
    # Get
    response = client.get("/users/test_user2")
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_user2"

def test_create_content():
    response = client.post(
        "/content/",
        json={
            "content_id": "test_content",
            "title": "Test Tutorial",
            "category": "ml",
            "tags": ["tutorial", "test"]
        }
    )
    assert response.status_code == 200
    assert response.json()["content_id"] == "test_content"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
