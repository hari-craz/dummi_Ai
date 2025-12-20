#!/bin/bash

# Dummi AI - Quick Start Script

set -e

echo "╔══════════════════════════════════════════╗"
echo "║   Dummi AI - Quick Start Setup          ║"
echo "╚══════════════════════════════════════════╝"

# Check Python version
echo ""
echo "[1/6] Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/6] Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null || true
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "[4/6] Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Setup environment
echo ""
echo "[5/6] Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created (edit with your database credentials)"
else
    echo "✓ .env file already exists"
fi

# Initialize database
echo ""
echo "[6/6] Initializing database..."
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"
echo "✓ Database initialized"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Setup Complete!                       ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Generate sample data: python data/generate_sample_data.py"
echo "3. Start the server: uvicorn app.main:app --reload"
echo "4. Run setup demo: python data/setup_demo.py"
echo "5. Open http://localhost:8000/docs for API documentation"
echo ""
