@echo off
REM Marine Equipment QR System - First Time Setup Script

echo ========================================
echo Marine Equipment QR Management System
echo First Time Setup
echo ========================================
echo.

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.12+
    pause
    exit /b 1
)
python --version
echo.

REM Check Bun
echo [2/6] Checking Bun...
bun --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Bun not found! Please install Bun from https://bun.sh
    pause
    exit /b 1
)
bun --version
echo.

REM Setup Backend
echo [3/6] Setting up backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo IMPORTANT: Please edit backend\.env to set a secure SECRET_KEY
)

echo Initializing database...
alembic upgrade head

echo Creating admin user...
python -m app.scripts.create_admin

cd ..
echo Backend setup complete!
echo.

REM Setup Frontend
echo [4/6] Setting up frontend...
cd frontend

echo Installing frontend dependencies...
bun install

cd ..
echo Frontend setup complete!
echo.

REM Done
echo [5/6] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Edit backend\.env to set SECRET_KEY
echo 2. Run start_all.bat to start both servers
echo 3. Visit http://localhost:5173
echo 4. Login with: admin / admin123
echo 5. Setup 2FA on first login
echo.
echo To start servers: Run start_all.bat
echo To stop servers: Run stop_all.bat
echo ========================================
echo.

pause
