import json
import random
from datetime import datetime, timedelta

# Sample data
users_data = [
    {
        "user_id": "alice",
        "interests": ["machine-learning", "python", "data-science"],
        "skill_level": "intermediate"
    },
    {
        "user_id": "bob",
        "interests": ["web-development", "javascript", "react"],
        "skill_level": "beginner"
    },
    {
        "user_id": "charlie",
        "interests": ["devops", "kubernetes", "cloud"],
        "skill_level": "advanced"
    },
    {
        "user_id": "diana",
        "interests": ["machine-learning", "nlp", "transformers"],
        "skill_level": "advanced"
    },
    {
        "user_id": "eve",
        "interests": ["python", "web-development", "fastapi"],
        "skill_level": "intermediate"
    }
]

content_data = [
    {
        "content_id": "ml101",
        "title": "Machine Learning 101: Fundamentals",
        "category": "machine-learning",
        "tags": ["beginner", "python", "fundamentals"],
        "description": "Learn the basics of machine learning including supervised and unsupervised learning"
    },
    {
        "content_id": "nlp101",
        "title": "Natural Language Processing with Transformers",
        "category": "machine-learning",
        "tags": ["nlp", "transformers", "advanced"],
        "description": "Deep dive into modern NLP using transformer models like BERT and GPT"
    },
    {
        "content_id": "cf_guide",
        "title": "Collaborative Filtering: From Theory to Practice",
        "category": "machine-learning",
        "tags": ["recommendations", "cf", "tutorial"],
        "description": "Complete guide to building recommendation systems with collaborative filtering"
    },
    {
        "content_id": "web101",
        "title": "Web Development with FastAPI",
        "category": "web-development",
        "tags": ["python", "fastapi", "beginner"],
        "description": "Build modern web APIs using FastAPI framework"
    },
    {
        "content_id": "react101",
        "title": "React for Beginners",
        "category": "web-development",
        "tags": ["javascript", "react", "frontend"],
        "description": "Learn React fundamentals and build interactive UIs"
    },
    {
        "content_id": "k8s101",
        "title": "Kubernetes Essentials",
        "category": "devops",
        "tags": ["kubernetes", "docker", "containers"],
        "description": "Master Kubernetes orchestration for containerized applications"
    },
    {
        "content_id": "embeddings101",
        "title": "Word Embeddings: From Word2Vec to Modern Approaches",
        "category": "machine-learning",
        "tags": ["embeddings", "nlp", "ml"],
        "description": "Explore the evolution of word embeddings and their applications"
    },
    {
        "content_id": "cloud101",
        "title": "Cloud Architecture Best Practices",
        "category": "devops",
        "tags": ["cloud", "aws", "architecture"],
        "description": "Design scalable and resilient cloud-based systems"
    }
]

interactions_data = [
    ("alice", "ml101", "click"),
    ("alice", "ml101", "like"),
    ("alice", "nlp101", "click"),
    ("alice", "cf_guide", "click"),
    ("alice", "embeddings101", "like"),
    
    ("bob", "web101", "click"),
    ("bob", "web101", "like"),
    ("bob", "react101", "click"),
    ("bob", "fastapi", "like"),
    
    ("charlie", "k8s101", "click"),
    ("charlie", "k8s101", "like"),
    ("charlie", "cloud101", "click"),
    
    ("diana", "nlp101", "click"),
    ("diana", "nlp101", "like"),
    ("diana", "embeddings101", "click"),
    ("diana", "ml101", "skip"),
    
    ("eve", "web101", "click"),
    ("eve", "fastapi", "click"),
    ("eve", "ml101", "click"),
]

def generate_data():
    """Generate sample data"""
    data = {
        "users": users_data,
        "content": content_data,
        "interactions": [
            {
                "user_id": user,
                "content_id": content,
                "interaction_type": itype,
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            for user, content, itype in interactions_data
        ]
    }
    return data

if __name__ == "__main__":
    data = generate_data()
    with open("sample_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Sample data generated in sample_data.json")
