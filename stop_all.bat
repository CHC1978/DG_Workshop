@echo off
REM Marine Equipment QR System - Stop All Services
chcp 65001 >nul

echo ========================================
echo 停止所有伺服器...
echo Stopping all servers...
echo ========================================
echo.

REM Kill uvicorn processes (backend)
echo [1/3] 停止後端伺服器...
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
echo [2/3] 停止前端伺服器...
taskkill /F /IM bun.exe 2>nul
if %errorlevel% equ 0 (
    echo   Frontend server stopped
) else (
    echo   No frontend server running
)

REM Also kill node processes (in case Vite is running)
echo [3/3] 清理相關程序...
taskkill /F /IM node.exe 2>nul

echo.
echo ========================================
echo 所有伺服器已停止
echo All servers stopped
echo ========================================
echo.

pause
