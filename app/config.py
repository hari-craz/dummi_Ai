import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dummi_ai.db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db/embeddings.faiss")
    FAISS_DIMENSION = int(os.getenv("FAISS_DIMENSION", 384))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Recommendation parameters
    TOP_K = 10
    SIMILARITY_THRESHOLD = 0.3
    COLD_START_THRESHOLD = 5  # Min interactions to use CF
    
    # Collaborative filtering parameters
    N_FACTORS = 50
    N_EPOCHS = 20
    LEARNING_RATE = 0.01
