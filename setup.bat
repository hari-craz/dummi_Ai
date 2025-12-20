@echo off
REM Dummi AI - Quick Start Script for Windows

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Dummi AI - Quick Start Setup          ║
echo ╚══════════════════════════════════════════╝

REM Check Python version
echo.
echo [1/6] Checking Python version...
python --version
echo ✓ Python found

REM Create virtual environment
echo.
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

REM Install dependencies
echo.
echo [4/6] Installing dependencies...
pip install -q -r requirements.txt
echo ✓ Dependencies installed

REM Setup environment
echo.
echo [5/6] Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo ✓ .env file created (edit with your database credentials)
) else (
    echo ✓ .env file already exists
)

REM Initialize database
echo.
echo [6/6] Initializing database...
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"
echo ✓ Database initialized

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Setup Complete!                       ║
echo ╚══════════════════════════════════════════╝
echo.
echo Next steps:
echo 1. Edit .env file with your database credentials
echo 2. Generate sample data: python data/generate_sample_data.py
echo 3. Start the server: uvicorn app.main:app --reload
echo 4. Run setup demo: python data/setup_demo.py
echo 5. Open http://localhost:8000/docs for API documentation
echo.
