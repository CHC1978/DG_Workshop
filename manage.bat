@echo off
setlocal enabledelayedexpansion
REM Marine Equipment QR System - Control Panel
title Marine Equipment QR System - Control Panel

REM Default to localhost mode
set NETWORK_MODE=0
set SELECTED_IP=

:MENU
cls

REM Get all IPv4 addresses
set IP_COUNT=0
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set /a IP_COUNT+=1
    for /f "tokens=* delims= " %%b in ("%%a") do set IP_!IP_COUNT!=%%b
)

echo ========================================
echo Marine Equipment QR Management System
echo Control Panel
echo ========================================
echo.
echo Detected IP addresses:
if %IP_COUNT%==0 (
    echo   No IP addresses detected
    echo   Make sure network is connected
) else (
    for /L %%i in (1,1,%IP_COUNT%) do (
        echo   [%%i] !IP_%%i!
    )
)
echo.
if "!NETWORK_MODE!"=="1" (
    echo Current Mode: Network Mode (IP: !SELECTED_IP!)
) else (
    echo Current Mode: Localhost Mode
)
echo.
echo [1] Start All - Localhost Mode
echo [2] Stop All
echo [3] Restart All
echo.
echo [4] Start Backend Only
echo [5] Start Frontend Only
echo [6] Restart Backend Only
echo [7] Restart Frontend Only
echo.
echo [8] Stop Backend Only
echo [9] Stop Frontend Only
echo.
echo [N] Start All - Network Mode (Choose IP)
echo [S] Check Status
echo [H] First Time Setup
echo.
echo [0] Exit
echo.
echo ========================================
set /p choice="Select option: "

if /I "%choice%"=="1" goto START_ALL_LOCALHOST
if /I "%choice%"=="2" goto STOP_ALL
if /I "%choice%"=="3" goto RESTART_ALL
if /I "%choice%"=="4" goto START_BACKEND
if /I "%choice%"=="5" goto START_FRONTEND
if /I "%choice%"=="6" goto RESTART_BACKEND
if /I "%choice%"=="7" goto RESTART_FRONTEND
if /I "%choice%"=="8" goto STOP_BACKEND
if /I "%choice%"=="9" goto STOP_FRONTEND
if /I "%choice%"=="N" goto SELECT_IP_FOR_NETWORK
if /I "%choice%"=="S" goto CHECK_STATUS
if /I "%choice%"=="H" goto FIRST_SETUP
if /I "%choice%"=="0" goto EXIT
goto MENU

:SELECT_IP_FOR_NETWORK
cls
echo ========================================
echo Select IP Address for Network Mode
echo ========================================
echo.
if %IP_COUNT%==0 (
    echo No IP addresses detected!
    echo Please check your network connection.
    pause
    goto MENU
)
echo Available IP addresses:
for /L %%i in (1,1,%IP_COUNT%) do (
    echo   [%%i] !IP_%%i!
)
echo.
echo [0] Cancel and return to menu
echo.
set /p ip_choice="Select IP address (1-%IP_COUNT%): "

if "%ip_choice%"=="0" goto MENU
if "%ip_choice%"=="" goto SELECT_IP_FOR_NETWORK
if %ip_choice% LEQ 0 goto SELECT_IP_FOR_NETWORK
if %ip_choice% GTR %IP_COUNT% goto SELECT_IP_FOR_NETWORK

REM Get selected IP and set network mode
set SELECTED_IP=!IP_%ip_choice%!
set NETWORK_MODE=1
goto START_ALL

:START_ALL_LOCALHOST
REM Explicitly set localhost mode
set NETWORK_MODE=0
set SELECTED_IP=
goto START_ALL

:START_ALL
echo.
if "!NETWORK_MODE!"=="1" (
    echo Starting all services (Network mode - IP: !SELECTED_IP!)...
) else (
    echo Starting all services (Localhost mode)...
)
call :STOP_ALL_SILENT
call :CLOSE_SERVER_WINDOWS
timeout /t 2 /nobreak >nul

if "!NETWORK_MODE!"=="1" (
    REM Network mode
    start /min "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --reload --port 8000"
    timeout /t 3 /nobreak >nul
    start /min "Frontend" cmd /k "cd frontend && bun dev --host 0.0.0.0"
    echo.
    echo Network Mode - Access from other devices
    echo Backend: http://!SELECTED_IP!:8000
    echo Frontend: http://!SELECTED_IP!:5173
    echo.
) else (
    REM Localhost mode
    start /min "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"
    timeout /t 3 /nobreak >nul
    start /min "Frontend" cmd /k "cd frontend && bun dev"
    echo.
    echo Localhost Mode
    echo Backend: http://localhost:8000
    echo Frontend: http://localhost:5173
    echo.
)
echo Services started
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
goto :EOF

:RESTART_ALL
REM Use the same mode as before
goto START_ALL

:START_BACKEND
echo.
echo Starting backend server...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /FI "WindowTitle eq Backend Server*" 2>nul
timeout /t 1 /nobreak >nul

if "!NETWORK_MODE!"=="1" (
    start /min "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --reload --port 8000"
    echo Backend started - Network mode
    echo URL: http://!SELECTED_IP!:8000
) else (
    start /min "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"
    echo Backend started - Localhost mode
    echo URL: http://localhost:8000
)
echo.
pause
goto MENU

:START_FRONTEND
echo.
echo Starting frontend server...

if "!NETWORK_MODE!"=="1" (
    start /min "Frontend" cmd /k "cd frontend && bun dev --host 0.0.0.0"
    echo Frontend started - Network mode
    echo URL: http://!SELECTED_IP!:5173
) else (
    start /min "Frontend" cmd /k "cd frontend && bun dev"
    echo Frontend started - Localhost mode
    echo URL: http://localhost:5173
)
echo.
pause
goto MENU

:RESTART_BACKEND
echo.
echo Restarting backend server...
echo Stopping backend...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /FI "WindowTitle eq Backend Server*" 2>nul
timeout /t 2 /nobreak >nul
echo Starting backend...

if "!NETWORK_MODE!"=="1" (
    start /min "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --reload --port 8000"
    echo Backend restarted - Network mode
    echo URL: http://!SELECTED_IP!:8000
) else (
    start /min "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"
    echo Backend restarted - Localhost mode
    echo URL: http://localhost:8000
)
echo.
pause
goto MENU

:RESTART_FRONTEND
echo.
echo Restarting frontend server...
echo Stopping frontend...
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
taskkill /FI "WindowTitle eq Frontend Server*" 2>nul
timeout /t 2 /nobreak >nul
echo Starting frontend...

if "!NETWORK_MODE!"=="1" (
    start /min "Frontend" cmd /k "cd frontend && bun dev --host 0.0.0.0"
    echo Frontend restarted - Network mode
    echo URL: http://!SELECTED_IP!:5173
) else (
    start /min "Frontend" cmd /k "cd frontend && bun dev"
    echo Frontend restarted - Localhost mode
    echo URL: http://localhost:5173
)
echo.
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
echo Backend - Python/Uvicorn:
tasklist 2>nul | findstr /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Backend server is running
) else (
    echo   [STOPPED] Backend server is not running
)
echo.
echo Frontend - Bun/Node:
tasklist 2>nul | findstr /I "bun.exe" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Frontend server is running
) else (
    tasklist 2>nul | findstr /I "node.exe" >nul
    if %errorlevel% equ 0 (
        echo   [RUNNING] Frontend server is running
    ) else (
        echo   [STOPPED] Frontend server is not running
    )
)
echo.
echo Access URLs:
echo ========================================
echo Localhost Access:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
if %IP_COUNT% GTR 0 (
    echo Network Access (from other devices):
    for /L %%i in (1,1,%IP_COUNT%) do (
        echo   !IP_%%i! - http://!IP_%%i!:5173
    )
)
echo ========================================
echo.
pause
goto MENU

:FIRST_SETUP
echo.
echo First time setup requires setup_first_time.bat
echo Please run setup_first_time.bat manually if needed
echo.
pause
goto MENU

:EXIT
echo.
echo Stopping all services before exit...
call :STOP_ALL_SILENT
call :CLOSE_SERVER_WINDOWS
echo All services stopped
echo.
echo Exiting...
timeout /t 2 /nobreak >nul
exit /b 0
