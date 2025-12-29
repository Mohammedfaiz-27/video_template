@echo off
REM Complete setup and test script for Video Template Generator

echo ============================================================
echo   Video Template Generator - Setup and Test
echo ============================================================
echo.

REM Step 1: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [1/6] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python 3.10+ is installed
        pause
        exit /b 1
    )
    echo     ✓ Virtual environment created
) else (
    echo [1/6] Virtual environment already exists ✓
)

echo.
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo     ✓ Activated

echo.
echo [3/6] Installing dependencies...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo     ✓ Dependencies installed

echo.
echo [4/6] Checking MongoDB...
docker ps | findstr video-gen-mongodb > nul
if errorlevel 1 (
    echo     Starting MongoDB in Docker...
    docker run -d -p 27017:27017 --name video-gen-mongodb mongo:7.0
    if errorlevel 1 (
        echo     WARNING: Could not start MongoDB Docker container
        echo     Please ensure MongoDB is running manually or:
        echo     1. Install Docker Desktop
        echo     2. Or install MongoDB locally
        pause
    ) else (
        echo     ✓ MongoDB started in Docker
        timeout /t 3 > nul
    )
) else (
    echo     ✓ MongoDB already running
)

echo.
echo [5/6] Verifying .env configuration...
findstr "PASTE_YOUR" .env > nul
if not errorlevel 1 (
    echo     ERROR: API keys not configured in .env file
    echo     Please edit .env and add your API keys
    pause
    exit /b 1
)
echo     ✓ API keys configured

echo.
echo [6/6] Setup complete!
echo.
echo ============================================================
echo   Starting Backend Server
echo ============================================================
echo.
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo Starting in 3 seconds...
timeout /t 3 > nul

python -m uvicorn app.main:app --reload --port 8000
