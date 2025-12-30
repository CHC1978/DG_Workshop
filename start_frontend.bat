@echo off
REM Marine Equipment QR System - Frontend Startup Script

echo ========================================
echo Starting Frontend Development Server...
echo ========================================

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo WARNING: Dependencies not installed!
    echo Installing dependencies...
    bun install
)

echo.
echo Starting Vite development server...
echo Frontend: http://localhost:5173
echo.

REM Start bun dev
bun dev

REM Keep window open if server stops
pause
