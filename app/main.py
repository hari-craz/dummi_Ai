from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, content, recommendations, training
from app.models.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dummi AI - Content Recommendation Engine",
    description="ML-powered recommendation system with embeddings and collaborative filtering",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(content.router)
app.include_router(recommendations.router)
app.include_router(training.router)

@app.get("/")
async def root():
    return {
        "name": "Dummi AI",
        "version": "1.0.0",
        "description": "Content Recommendation Engine",
        "endpoints": {
            "users": "/users",
            "content": "/content",
            "recommendations": "/recommendations",
            "training": "/training"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
