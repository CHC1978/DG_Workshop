@echo off
REM Marine Equipment QR System - Restart All Services
chcp 65001 >nul

echo ========================================
echo 重新啟動系統...
echo Restarting System...
echo ========================================
echo.

echo [1/3] 停止舊的伺服器...
call stop_all.bat

echo.
echo [2/3] 等待程序結束...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] 啟動新的伺服器...
call start_all.bat

echo.
echo 系統重新啟動完成！
echo.
pause
