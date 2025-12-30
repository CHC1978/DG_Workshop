@echo off
REM Marine Equipment QR System - Restart All Services
chcp 65001 >nul

echo ========================================
echo 重新啟動系統...
echo Restarting System...
echo ========================================
echo.

echo [1/3] 停止舊的伺服器...
echo Stopping old servers...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo   Stopped

echo.
echo [2/3] 等待程序結束...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] 啟動新的伺服器...
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
timeout /t 3 /nobreak >nul
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"

echo.
echo ========================================
echo 系統重新啟動完成！
echo System restarted successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo 伺服器視窗已最小化到工作列
echo Server windows minimized to taskbar
echo.
pause
