@echo off
REM Marine Equipment QR System - Stop All Services

echo ========================================
echo Stopping all servers...
echo ========================================

REM Kill uvicorn processes (backend)
echo Stopping backend server...
taskkill /F /IM uvicorn.exe 2>nul
if %errorlevel% equ 0 (
    echo Backend server stopped
) else (
    echo No backend server running
)

REM Kill bun processes (frontend)
echo Stopping frontend server...
taskkill /F /IM bun.exe 2>nul
if %errorlevel% equ 0 (
    echo Frontend server stopped
) else (
    echo No frontend server running
)

REM Also kill node processes (in case Vite is running)
taskkill /F /IM node.exe 2>nul

echo.
echo All servers stopped
echo.

pause
