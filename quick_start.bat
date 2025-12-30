@echo off
REM Marine Equipment QR System - Quick Start
title Marine Equipment QR System - Quick Start

echo ========================================
echo Marine Equipment QR Management System
echo Quick Start
echo ========================================
echo.
echo Starting system...
echo.

REM Stop old processes
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 1 /nobreak >nul

REM Start backend (minimized)
echo [1/2] Starting backend server...
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
timeout /t 3 /nobreak >nul

REM Start frontend (minimized)
echo [2/2] Starting frontend server...
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo.
echo Access: http://localhost:5173
echo.
echo Default Account: admin
echo Default Password: admin123
echo.
echo Close this window to continue
echo To stop servers: Close server windows or run stop_all.bat
echo.
pause
