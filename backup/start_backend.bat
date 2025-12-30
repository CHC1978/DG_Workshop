@echo off
REM Marine Equipment QR System - Backend Startup Script

echo ========================================
echo Starting Backend Server...
echo ========================================

cd backend

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Copying from .env.example...
    copy .env.example .env
    echo Please edit .env to set SECRET_KEY
    pause
)

echo.
echo Virtual environment activated
echo Starting uvicorn server...
echo API Docs: http://localhost:8000/docs
echo.

REM Start uvicorn
python -m uvicorn app.main:app --reload --port 8000

REM Keep window open if server stops
pause
