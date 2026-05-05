"""
Seed Data Generator for Dummi AI
Populates the database with sample users, content, and interactions
so the AI can be trained immediately.

Usage:  python -m data.seed_data
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base, engine, SessionLocal
from app.db import crud
from app.models.schemas import UserCreate, ContentCreate, InteractionCreate
import random

# ── Sample data ──────────────────────────────────────────────

USERS = [
    UserCreate(user_id="alice", interests=["machine-learning", "python", "deep-learning"], skill_level="intermediate"),
    UserCreate(user_id="bob", interests=["web-dev", "javascript", "react"], skill_level="advanced"),
    UserCreate(user_id="charlie", interests=["data-science", "python", "statistics"], skill_level="beginner"),
    UserCreate(user_id="diana", interests=["machine-learning", "nlp", "transformers"], skill_level="advanced"),
    UserCreate(user_id="eve", interests=["python", "automation", "scripting"], skill_level="beginner"),
    UserCreate(user_id="frank", interests=["web-dev", "typescript", "node"], skill_level="intermediate"),
    UserCreate(user_id="grace", interests=["data-science", "visualization", "pandas"], skill_level="intermediate"),
    UserCreate(user_id="hank", interests=["deep-learning", "computer-vision", "pytorch"], skill_level="advanced"),
    UserCreate(user_id="ivy", interests=["machine-learning", "python", "scikit-learn"], skill_level="beginner"),
    UserCreate(user_id="jack", interests=["web-dev", "css", "design"], skill_level="beginner"),
]

CONTENT = [
    # Machine Learning
    ContentCreate(content_id="ml-101", title="Introduction to Machine Learning", category="machine-learning",
                  tags=["beginner", "tutorial", "python"], description="A comprehensive beginner's guide to machine learning concepts and algorithms."),
    ContentCreate(content_id="ml-102", title="Linear Regression Deep Dive", category="machine-learning",
                  tags=["regression", "statistics", "python"], description="Understanding linear regression from theory to implementation."),
    ContentCreate(content_id="ml-103", title="Decision Trees and Random Forests", category="machine-learning",
                  tags=["classification", "ensemble", "scikit-learn"], description="Master tree-based models for classification and regression tasks."),
    ContentCreate(content_id="ml-104", title="Support Vector Machines Explained", category="machine-learning",
                  tags=["svm", "classification", "kernel"], description="Deep dive into SVMs, kernel tricks, and practical applications."),
    ContentCreate(content_id="ml-105", title="Feature Engineering Best Practices", category="machine-learning",
                  tags=["features", "preprocessing", "pipeline"], description="Learn how to create powerful features for ML models."),

    # Deep Learning
    ContentCreate(content_id="dl-101", title="Neural Networks from Scratch", category="deep-learning",
                  tags=["neural-network", "python", "math"], description="Build a neural network from scratch using numpy."),
    ContentCreate(content_id="dl-102", title="Convolutional Neural Networks", category="deep-learning",
                  tags=["cnn", "computer-vision", "pytorch"], description="Everything about CNNs: architecture, training, and transfer learning."),
    ContentCreate(content_id="dl-103", title="Transformers and Attention Mechanisms", category="deep-learning",
                  tags=["transformers", "nlp", "attention"], description="Understanding the transformer architecture that powers modern NLP."),
    ContentCreate(content_id="dl-104", title="Generative Adversarial Networks", category="deep-learning",
                  tags=["gan", "generative", "image"], description="Learn to build GANs for image generation and style transfer."),
    ContentCreate(content_id="dl-105", title="Recurrent Neural Networks and LSTMs", category="deep-learning",
                  tags=["rnn", "lstm", "sequence"], description="Sequence modeling with RNNs, LSTMs, and GRUs."),

    # Data Science
    ContentCreate(content_id="ds-101", title="Exploratory Data Analysis with Pandas", category="data-science",
                  tags=["pandas", "eda", "python"], description="Master EDA techniques using pandas and matplotlib."),
    ContentCreate(content_id="ds-102", title="Statistical Hypothesis Testing", category="data-science",
                  tags=["statistics", "hypothesis", "p-value"], description="Understanding t-tests, chi-square tests, and ANOVA."),
    ContentCreate(content_id="ds-103", title="Data Visualization with Plotly", category="data-science",
                  tags=["visualization", "plotly", "dashboard"], description="Create interactive visualizations and dashboards."),
    ContentCreate(content_id="ds-104", title="Time Series Analysis", category="data-science",
                  tags=["time-series", "forecasting", "arima"], description="Techniques for analyzing and forecasting time series data."),
    ContentCreate(content_id="ds-105", title="A/B Testing Guide", category="data-science",
                  tags=["ab-testing", "experimentation", "statistics"], description="Design and analyze A/B tests for product decisions."),

    # Web Development
    ContentCreate(content_id="web-101", title="Modern React Patterns", category="web-dev",
                  tags=["react", "hooks", "javascript"], description="Advanced React patterns including hooks, context, and suspense."),
    ContentCreate(content_id="web-102", title="Building REST APIs with FastAPI", category="web-dev",
                  tags=["fastapi", "python", "rest"], description="Create high-performance APIs with Python FastAPI framework."),
    ContentCreate(content_id="web-103", title="CSS Grid and Flexbox Mastery", category="web-dev",
                  tags=["css", "layout", "design"], description="Complete guide to modern CSS layout techniques."),
    ContentCreate(content_id="web-104", title="TypeScript for JavaScript Developers", category="web-dev",
                  tags=["typescript", "javascript", "types"], description="Transition from JavaScript to TypeScript smoothly."),
    ContentCreate(content_id="web-105", title="Node.js Microservices", category="web-dev",
                  tags=["node", "microservices", "docker"], description="Design and deploy microservices with Node.js."),

    # Python
    ContentCreate(content_id="py-101", title="Python Advanced Patterns", category="python",
                  tags=["python", "design-patterns", "oop"], description="Decorators, metaclasses, context managers and more."),
    ContentCreate(content_id="py-102", title="Async Python with asyncio", category="python",
                  tags=["python", "async", "concurrency"], description="Asynchronous programming in Python using asyncio."),
    ContentCreate(content_id="py-103", title="Python Testing with pytest", category="python",
                  tags=["python", "testing", "pytest"], description="Comprehensive testing strategies with pytest."),
    ContentCreate(content_id="py-104", title="Python Automation Scripts", category="python",
                  tags=["python", "automation", "scripting"], description="Automate daily tasks with Python scripting."),
    ContentCreate(content_id="py-105", title="Python Data Structures", category="python",
                  tags=["python", "data-structures", "algorithms"], description="Master Python's built-in data structures and when to use each."),

    # NLP
    ContentCreate(content_id="nlp-101", title="Introduction to NLP", category="nlp",
                  tags=["nlp", "text", "python"], description="Fundamentals of Natural Language Processing."),
    ContentCreate(content_id="nlp-102", title="Sentiment Analysis with BERT", category="nlp",
                  tags=["bert", "sentiment", "transformers"], description="Fine-tune BERT for sentiment analysis tasks."),
    ContentCreate(content_id="nlp-103", title="Text Classification Pipeline", category="nlp",
                  tags=["classification", "tfidf", "sklearn"], description="Build end-to-end text classification systems."),
    ContentCreate(content_id="nlp-104", title="Word Embeddings: Word2Vec to GPT", category="nlp",
                  tags=["embeddings", "word2vec", "gpt"], description="Evolution of word representations in NLP."),
    ContentCreate(content_id="nlp-105", title="Named Entity Recognition", category="nlp",
                  tags=["ner", "spacy", "entities"], description="Extract entities from text using modern NER techniques."),
]

INTERACTION_TYPES = ["click", "like", "skip", "view_time"]

# Define interest-to-content affinity (users are more likely to interact
# with content matching their interests)
CATEGORY_MAP = {
    "machine-learning": ["ml-101", "ml-102", "ml-103", "ml-104", "ml-105"],
    "deep-learning":    ["dl-101", "dl-102", "dl-103", "dl-104", "dl-105"],
    "data-science":     ["ds-101", "ds-102", "ds-103", "ds-104", "ds-105"],
    "web-dev":          ["web-101", "web-102", "web-103", "web-104", "web-105"],
    "python":           ["py-101", "py-102", "py-103", "py-104", "py-105"],
    "nlp":              ["nlp-101", "nlp-102", "nlp-103", "nlp-104", "nlp-105"],
}


def generate_interactions():
    """Generate realistic interactions based on user interests."""
    interactions = []
    all_content_ids = [c.content_id for c in CONTENT]

    for user in USERS:
        # Find content matching user interests
        relevant = []
        for interest in user.interests:
            relevant.extend(CATEGORY_MAP.get(interest, []))
        relevant = list(set(relevant))

        # Generate 8-15 interactions per user
        n_interactions = random.randint(8, 15)
        for _ in range(n_interactions):
            # 70% chance to interact with relevant content, 30% random
            if relevant and random.random() < 0.7:
                content_id = random.choice(relevant)
            else:
                content_id = random.choice(all_content_ids)

            # Bias interaction type: relevant → more likes, irrelevant → more skips
            if content_id in relevant:
                itype = random.choices(
                    INTERACTION_TYPES,
                    weights=[30, 40, 5, 25],  # click, like, skip, view_time
                    k=1
                )[0]
            else:
                itype = random.choices(
                    INTERACTION_TYPES,
                    weights=[20, 10, 40, 30],
                    k=1
                )[0]

            interactions.append(InteractionCreate(
                user_id=user.user_id,
                content_id=content_id,
                interaction_type=itype,
            ))

    return interactions


def seed():
    """Seed the database with sample data."""
    random.seed(42)

    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Users
        created_users = 0
        for user in USERS:
            if not crud.get_user(db, user.user_id):
                crud.create_user(db, user)
                created_users += 1
        print(f"  ✓ Created {created_users} users (skipped {len(USERS) - created_users} existing)")

        # Content
        created_content = 0
        for content in CONTENT:
            if not crud.get_content(db, content.content_id):
                crud.create_content(db, content)
                created_content += 1
        print(f"  ✓ Created {created_content} content items (skipped {len(CONTENT) - created_content} existing)")

        # Interactions
        interactions = generate_interactions()
        for inter in interactions:
            crud.create_interaction(db, inter)
        print(f"  ✓ Created {len(interactions)} interactions")

        print("\n🎉 Database seeded successfully!")
        print(f"   Total: {len(USERS)} users, {len(CONTENT)} content items, {len(interactions)} interactions")

    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding Dummi AI database...\n")
    seed()
