import json
import requests
import time

BASE_URL = "http://localhost:8080"

def load_sample_data():
    """Load sample data from JSON file"""
    with open("data/sample_data.json", "r") as f:
        return json.load(f)

def setup_users(data):
    """Create users"""
    print("\n=== Creating Users ===")
    for user in data["users"]:
        response = requests.post(
            f"{BASE_URL}/users/",
            json=user
        )
        if response.status_code == 200:
            print(f"✓ Created user: {user['user_id']}")
        else:
            print(f"✗ Failed to create user: {response.text}")

def setup_content(data):
    """Create content"""
    print("\n=== Creating Content ===")
    for content in data["content"]:
        response = requests.post(
            f"{BASE_URL}/content/",
            json=content
        )
        if response.status_code == 200:
            print(f"✓ Created content: {content['content_id']}")
        else:
            print(f"✗ Failed to create content: {response.text}")

def setup_interactions(data):
    """Create interactions"""
    print("\n=== Creating Interactions ===")
    for interaction in data["interactions"]:
        response = requests.post(
            f"{BASE_URL}/recommendations/interact",
            json=interaction
        )
        if response.status_code == 200:
            print(f"✓ Recorded interaction: {interaction['user_id']} -> {interaction['content_id']}")
        else:
            print(f"✗ Failed to record interaction: {response.text}")

def train_models():
    """Train ML models"""
    print("\n=== Training Models ===")
    response = requests.post(
        f"{BASE_URL}/training/train",
        json={
            "retrain_cf": True,
            "regenerate_embeddings": True
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Training completed")
        print(f"  - Embeddings generated: {result['embeddings_generated']}")
        print(f"  - CF model trained: {result['cf_model_trained']}")
    else:
        print(f"✗ Training failed: {response.text}")

def get_recommendations(user_id):
    """Get recommendations for a user"""
    print(f"\n=== Recommendations for {user_id} ===")
    response = requests.post(
        f"{BASE_URL}/recommendations/",
        json={
            "user_id": user_id,
            "n_recommendations": 5,
            "use_cf": True,
            "use_embeddings": True,
            "cf_weight": 0.5
        }
    )
    if response.status_code == 200:
        result = response.json()
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"{i}. {rec['title']} (score: {rec['score']:.3f})")
    else:
        print(f"✗ Failed to get recommendations: {response.text}")

def main():
    """Run setup pipeline"""
    print("=" * 50)
    print("Dummi AI - Setup Pipeline")
    print("=" * 50)
    
    # Load sample data
    data = load_sample_data()
    
    # Setup
    setup_users(data)
    time.sleep(1)
    
    setup_content(data)
    time.sleep(1)
    
    setup_interactions(data)
    time.sleep(1)
    
    # Train models
    train_models()
    time.sleep(2)
    
    # Get recommendations for each user
    for user in data["users"]:
        get_recommendations(user["user_id"])
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
