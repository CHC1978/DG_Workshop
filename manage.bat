@echo off
setlocal enabledelayedexpansion
title Marine Equipment QR System

set NETWORK_MODE=0
set SELECTED_IP=

:MENU
cls

REM Get IPs
set IP_COUNT=0
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set /a IP_COUNT+=1
    for /f "tokens=* delims= " %%b in ("%%a") do set IP_!IP_COUNT!=%%b
)

echo ========================================
echo Marine Equipment QR System
echo ========================================
echo.
echo Detected IPs:
if !IP_COUNT!==0 (
    echo   No IP detected
) else (
    for /L %%i in (1,1,!IP_COUNT!) do echo   [%%i] !IP_%%i!
)
echo.
if "!NETWORK_MODE!"=="1" echo Mode: Network (!SELECTED_IP!)
if "!NETWORK_MODE!"=="0" echo Mode: Localhost
echo.
echo [1] Start All - Localhost
echo [2] Stop All
echo [3] Restart All
echo.
echo [4] Start Backend
echo [5] Start Frontend
echo [6] Restart Backend
echo [7] Restart Frontend
echo.
echo [8] Stop Backend
echo [9] Stop Frontend
echo.
echo [N] Network Mode
echo [S] Status
echo.
echo [0] Exit
echo.
echo ========================================
set /p choice="Option: "

if /I "!choice!"=="1" goto START_LOCALHOST
if /I "!choice!"=="2" goto STOP_ALL
if /I "!choice!"=="3" goto START_ALL
if /I "!choice!"=="4" goto START_BACKEND
if /I "!choice!"=="5" goto START_FRONTEND
if /I "!choice!"=="6" goto START_BACKEND
if /I "!choice!"=="7" goto START_FRONTEND
if /I "!choice!"=="8" goto STOP_BACKEND
if /I "!choice!"=="9" goto STOP_FRONTEND
if /I "!choice!"=="N" goto SELECT_IP
if /I "!choice!"=="S" goto STATUS
if /I "!choice!"=="0" goto EXIT
goto MENU

:SELECT_IP
cls
echo ========================================
echo Select IP for Network Mode
echo ========================================
echo.
if !IP_COUNT!==0 (
    echo No IP detected
    pause
    goto MENU
)
for /L %%i in (1,1,!IP_COUNT!) do echo   [%%i] !IP_%%i!
echo.
echo [0] Cancel
echo.
set /p ip_choice="Select (1-!IP_COUNT!): "

if "!ip_choice!"=="0" goto MENU
if "!ip_choice!"=="" goto SELECT_IP
if !ip_choice! LEQ 0 goto SELECT_IP
if !ip_choice! GTR !IP_COUNT! goto SELECT_IP

set SELECTED_IP=!IP_%ip_choice%!
set NETWORK_MODE=1
goto START_ALL

:START_LOCALHOST
set NETWORK_MODE=0
set SELECTED_IP=
goto START_ALL

:START_ALL
call :STOP_ALL_SILENT
timeout /t 1 >nul 2>&1

if "!NETWORK_MODE!"=="1" (
    echo Starting Network Mode: !SELECTED_IP!
    cd backend
    start /min cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    cd ..
    timeout /t 2 >nul 2>&1
    cd frontend
    start /min cmd /k "bun dev --host 0.0.0.0"
    cd ..
    echo.
    echo Backend: http://!SELECTED_IP!:8000
    echo Frontend: http://!SELECTED_IP!:5173
) else (
    echo Starting Localhost Mode
    cd backend
    start /min cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --port 8000"
    cd ..
    timeout /t 2 >nul 2>&1
    cd frontend
    start /min cmd /k "bun dev"
    cd ..
    echo.
    echo Backend: http://localhost:8000
    echo Frontend: http://localhost:5173
)
echo.
echo Started
pause
goto MENU

:START_BACKEND
call :STOP_BACKEND_SILENT
timeout /t 1 >nul 2>&1

if "!NETWORK_MODE!"=="1" (
    cd backend
    start /min cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    cd ..
    echo Backend started - Network: !SELECTED_IP!:8000
) else (
    cd backend
    start /min cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --port 8000"
    cd ..
    echo Backend started - Localhost:8000
)
pause
goto MENU

:START_FRONTEND
call :STOP_FRONTEND_SILENT
timeout /t 1 >nul 2>&1

if "!NETWORK_MODE!"=="1" (
    cd frontend
    start /min cmd /k "bun dev --host 0.0.0.0"
    cd ..
    echo Frontend started - Network: !SELECTED_IP!:5173
) else (
    cd frontend
    start /min cmd /k "bun dev"
    cd ..
    echo Frontend started - Localhost:5173
)
pause
goto MENU

:STOP_ALL
echo.
echo Stopping all services...
call :STOP_ALL_SILENT
echo.
echo All services stopped
pause
goto MENU

:STOP_BACKEND
echo.
echo Stopping backend...
call :STOP_BACKEND_SILENT
echo Backend stopped
pause
goto MENU

:STOP_FRONTEND
echo.
echo Stopping frontend...
call :STOP_FRONTEND_SILENT
echo Frontend stopped
pause
goto MENU

:STOP_ALL_SILENT
echo Stopping processes...
REM Kill backend
taskkill /F /IM python.exe
taskkill /F /IM uvicorn.exe
REM Kill frontend
taskkill /F /IM bun.exe
taskkill /F /IM node.exe
REM Kill command windows
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq cmd.exe" /FO list ^| findstr /I "PID"') do (
    tasklist /FI "PID eq %%i" /V | findstr /I "backend frontend" >nul
    if !errorlevel!==0 taskkill /F /PID %%i >nul 2>&1
)
timeout /t 2 >nul 2>&1
goto :EOF

:STOP_BACKEND_SILENT
echo Stopping backend...
taskkill /F /IM python.exe
taskkill /F /IM uvicorn.exe
timeout /t 1 >nul 2>&1
goto :EOF

:STOP_FRONTEND_SILENT
echo Stopping frontend...
taskkill /F /IM bun.exe
taskkill /F /IM node.exe
timeout /t 1 >nul 2>&1
goto :EOF

:CLOSE_SERVER_WINDOWS
REM Not needed with simplified approach
goto :EOF

:STATUS
echo.
echo Status:
echo.
tasklist 2>nul | findstr /I "python.exe" >nul
if !errorlevel!==0 (echo   Backend: RUNNING) else (echo   Backend: STOPPED)

tasklist 2>nul | findstr /I "bun.exe node.exe" >nul
if !errorlevel!==0 (echo   Frontend: RUNNING) else (echo   Frontend: STOPPED)

echo.
echo URLs:
echo   Localhost: http://localhost:5173
if !IP_COUNT! GTR 0 (
    echo   Network:
    for /L %%i in (1,1,!IP_COUNT!) do echo     !IP_%%i!:5173
)
echo.
pause
goto MENU

:EXIT
echo.
echo Stopping all services before exit...
call :STOP_ALL_SILENT
echo.
echo All services stopped
echo Exiting...
timeout /t 2 >nul 2>&1
exit /b 0
