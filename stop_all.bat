@echo off
REM Marine Equipment QR System - Stop All Services
title Stop All Services

echo ========================================
echo Stopping All Servers...
echo ========================================
echo.

REM Kill uvicorn processes (backend)
echo [1/3] Stopping backend server...
taskkill /F /IM uvicorn.exe 2>nul
if %errorlevel% equ 0 (
    echo   Backend server stopped
) else (
    echo   No backend server running
)

REM Kill python processes
taskkill /F /IM python.exe 2>nul
echo.

REM Kill bun processes (frontend)
echo [2/3] Stopping frontend server...
taskkill /F /IM bun.exe 2>nul
if %errorlevel% equ 0 (
    echo   Frontend server stopped
) else (
    echo   No frontend server running
)

REM Also kill node processes
echo [3/3] Cleanup processes...
taskkill /F /IM node.exe 2>nul

echo.
echo ========================================
echo All Servers Stopped
echo ========================================
echo.

pause
