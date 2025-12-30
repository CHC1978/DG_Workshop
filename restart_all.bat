@echo off
REM Marine Equipment QR System - Restart All Services
title Restart All Services

echo ========================================
echo Restarting System...
echo ========================================
echo.

echo [1/3] Stopping old servers...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo   Stopped

echo.
echo [2/3] Waiting for processes to end...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] Starting new servers...
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
timeout /t 3 /nobreak >nul
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"

echo.
echo ========================================
echo System Restarted Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Server windows minimized to taskbar
echo.
pause
