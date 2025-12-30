@echo off
REM Marine Equipment QR System - Start All Services

echo ========================================
echo Marine Equipment QR Management System
echo ========================================
echo.
echo Starting Backend and Frontend servers...
echo.
echo Backend API: http://localhost:8000
echo Backend Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop
echo ========================================
echo.

REM Start backend in new minimized window
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new minimized window
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"

echo.
echo Both servers are starting in separate windows...
echo.
echo To stop servers: Close the command windows or press Ctrl+C
echo.

pause
