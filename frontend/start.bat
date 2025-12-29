@echo off
REM Startup script for Video Template Generator Frontend (Windows)

echo ============================================================
echo   Video Template Generator - Frontend Dev Server
echo ============================================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Vite dev server...
echo.
echo Frontend will be available at: http://localhost:5173
echo.
echo Make sure the backend is running at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
