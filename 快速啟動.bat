@echo off
REM Quick Start - Marine Equipment QR System
chcp 65001 >nul

echo ========================================
echo 海洋設備 QR 管理系統 - 快速啟動
echo ========================================
echo.
echo 正在啟動系統...
echo.

REM Stop old processes
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 1 /nobreak >nul

REM Start backend (minimized)
echo [1/2] 啟動後端伺服器...
start /min "後端伺服器 - Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
timeout /t 3 /nobreak >nul

REM Start frontend (minimized)
echo [2/2] 啟動前端伺服器...
start /min "前端伺服器 - Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"

echo.
echo ========================================
echo 系統啟動完成！
echo ========================================
echo.
echo 請訪問: http://localhost:5173
echo.
echo 預設帳號: admin
echo 預設密碼: admin123
echo.
echo 關閉此視窗不影響伺服器運行
echo 要停止伺服器請關閉伺服器視窗或執行 stop_all.bat
echo.
pause
