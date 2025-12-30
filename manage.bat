@echo off
REM Marine Equipment QR System - Control Panel
chcp 65001 >nul
title Marine Equipment QR System - Control Panel

:MENU
cls
echo ========================================
echo Marine Equipment QR Management System
echo Control Panel
echo ========================================
echo.
echo [1] Start All (Backend + Frontend)
echo [2] Stop All
echo [3] Restart All
echo.
echo [4] Start Backend Only
echo [5] Start Frontend Only
echo [6] Stop Backend Only
echo [7] Stop Frontend Only
echo.
echo [8] Check Status
echo [9] First Time Setup
echo.
echo [0] Exit
echo.
echo ========================================
set /p choice="Select option (0-9): "

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto STOP_ALL
if "%choice%"=="3" goto RESTART_ALL
if "%choice%"=="4" goto START_BACKEND
if "%choice%"=="5" goto START_FRONTEND
if "%choice%"=="6" goto STOP_BACKEND
if "%choice%"=="7" goto STOP_FRONTEND
if "%choice%"=="8" goto CHECK_STATUS
if "%choice%"=="9" goto FIRST_SETUP
if "%choice%"=="0" goto EXIT
goto MENU

:START_ALL
echo.
echo Starting all services...
call :STOP_ALL_SILENT
call :CLOSE_SERVER_WINDOWS
timeout /t 2 /nobreak >nul
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
timeout /t 3 /nobreak >nul
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Services started in separate windows
pause
goto MENU

:STOP_ALL
echo.
echo Stopping all services...
call :STOP_ALL_SILENT
call :CLOSE_SERVER_WINDOWS
echo.
echo All servers stopped
pause
goto MENU

:STOP_ALL_SILENT
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
goto :EOF

:CLOSE_SERVER_WINDOWS
taskkill /FI "WindowTitle eq Backend Server*" 2>nul
taskkill /FI "WindowTitle eq Frontend Server*" 2>nul
taskkill /FI "WindowTitle eq 後端伺服器*" 2>nul
taskkill /FI "WindowTitle eq 前端伺服器*" 2>nul
goto :EOF

:RESTART_ALL
echo.
echo Restarting all services...
call :STOP_ALL_SILENT
call :CLOSE_SERVER_WINDOWS
timeout /t 2 /nobreak >nul
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
timeout /t 3 /nobreak >nul
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"
echo.
echo Services restarted
pause
goto MENU

:START_BACKEND
echo.
echo Starting backend server...
call :STOP_ALL_SILENT
call :CLOSE_SERVER_WINDOWS
timeout /t 1 /nobreak >nul
start /min "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"
echo.
echo Backend started in new window
echo URL: http://localhost:8000
pause
goto MENU

:START_FRONTEND
echo.
echo Starting frontend server...
start /min "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"
echo.
echo Frontend started in new window
echo URL: http://localhost:5173
pause
goto MENU

:STOP_BACKEND
echo.
echo Stopping backend server...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo Backend stopped
) else (
    echo No backend server running
)
pause
goto MENU

:STOP_FRONTEND
echo.
echo Stopping frontend server...
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo Frontend stopped
) else (
    echo No frontend server running
)
pause
goto MENU

:CHECK_STATUS
echo.
echo Checking service status...
echo.
echo Backend (Python/Uvicorn):
tasklist 2>nul | findstr /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Backend server is running
) else (
    echo   [STOPPED] Backend server is not running
)
echo.
echo Frontend (Bun/Node):
tasklist 2>nul | findstr /I "bun.exe" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Frontend server is running
) else (
    tasklist 2>nul | findstr /I "node.exe" >nul
    if %errorlevel% equ 0 (
        echo   [RUNNING] Frontend server is running (Node)
    ) else (
        echo   [STOPPED] Frontend server is not running
    )
)
echo.
echo URLs:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
pause
goto MENU

:FIRST_SETUP
echo.
echo Running first time setup...
call setup_first_time.bat
pause
goto MENU

:EXIT
echo.
echo Exiting...
exit /b 0
