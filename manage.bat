@echo off
setlocal enabledelayedexpansion
title Marine Equipment QR System

set NETWORK_MODE=0
set SELECTED_IP=
set TAILSCALE_IP=
set TAILSCALE_HOSTNAME=

:MENU
cls

REM Get Local IPs
set IP_COUNT=0
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set /a IP_COUNT+=1
    for /f "tokens=* delims= " %%b in ("%%a") do set IP_!IP_COUNT!=%%b
)

REM Get Tailscale IP (100.x.x.x)
set TAILSCALE_IP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=* delims= " %%b in ("%%a") do (
        echo %%b | findstr /b "100." >nul
        if !errorlevel!==0 set TAILSCALE_IP=%%b
    )
)

echo ========================================
echo Marine Equipment QR System - Manager
echo ========================================
echo.
echo Detected IPs:
if !IP_COUNT!==0 (
    echo   No IP detected
) else (
    for /L %%i in (1,1,!IP_COUNT!) do (
        set CURRENT_IP=!IP_%%i!
        echo !CURRENT_IP! | findstr /b "100." >nul
        if !errorlevel!==0 (
            echo   [%%i] !CURRENT_IP! [Tailscale]
        ) else (
            echo   [%%i] !CURRENT_IP!
        )
    )
)
echo.
if "!NETWORK_MODE!"=="2" (
    echo Mode: Tailscale [!TAILSCALE_IP!]
    echo NAS:  https://neptus-station.boga-ulmer.ts.net
) else if "!NETWORK_MODE!"=="1" (
    echo Mode: Network [!SELECTED_IP!]
) else (
    echo Mode: Localhost
)
echo.
echo ----------------------------------------
echo  Development Server Controls
echo ----------------------------------------
echo [1] Start All - Localhost
echo [2] Stop All
echo [3] Restart All
echo.
echo [4] Start Backend    [8] Stop Backend
echo [5] Start Frontend   [9] Stop Frontend
echo [6] Restart Backend
echo [7] Restart Frontend
echo.
echo ----------------------------------------
echo  Network Options
echo ----------------------------------------
echo [N] Network Mode (LAN IP)
echo [T] Tailscale Mode
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
if /I "!choice!"=="T" goto TAILSCALE_MODE
if /I "!choice!"=="S" goto STATUS
if /I "!choice!"=="0" goto EXIT
goto MENU

:TAILSCALE_MODE
cls
echo ========================================
echo Tailscale Mode
echo ========================================
echo.
if "!TAILSCALE_IP!"=="" (
    echo [!] Tailscale IP not detected
    echo     Make sure Tailscale is running
    echo.
    pause
    goto MENU
)
echo Tailscale IP: !TAILSCALE_IP!
echo.
echo This will start servers accessible via Tailscale network.
echo.
echo Access URLs:
echo   Local Dev:  http://!TAILSCALE_IP!:5173
echo   Backend:    http://!TAILSCALE_IP!:8000
echo.
echo   NAS Prod:   https://neptus-station.boga-ulmer.ts.net
echo.
echo [1] Start with Tailscale IP
echo [0] Cancel
echo.
set /p ts_choice="Option: "

if "!ts_choice!"=="0" goto MENU
if "!ts_choice!"=="1" (
    set SELECTED_IP=!TAILSCALE_IP!
    set NETWORK_MODE=2
    goto START_ALL
)
goto TAILSCALE_MODE

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
for /L %%i in (1,1,!IP_COUNT!) do (
    set CURRENT_IP=!IP_%%i!
    echo !CURRENT_IP! | findstr /b "100." >nul
    if !errorlevel!==0 (
        echo   [%%i] !CURRENT_IP! [Tailscale]
    ) else (
        echo   [%%i] !CURRENT_IP!
    )
)
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

if "!NETWORK_MODE!"=="2" (
    echo.
    echo Starting Tailscale Mode: !SELECTED_IP!
    echo.
    cd backend
    start /min "MarineBackend" cmd /k venv\Scripts\activate ^&^& python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    cd ..
    timeout /t 2 >nul 2>&1
    cd frontend
    start /min "MarineFrontend" cmd /k bun dev --host 0.0.0.0
    cd ..
    echo ========================================
    echo  Tailscale Mode Started
    echo ========================================
    echo.
    echo Development Server:
    echo   Frontend: http://!SELECTED_IP!:5173
    echo   Backend:  http://!SELECTED_IP!:8000
    echo   API Docs: http://!SELECTED_IP!:8000/docs
    echo.
    echo Production NAS:
    echo   https://neptus-station.boga-ulmer.ts.net
    echo.
) else if "!NETWORK_MODE!"=="1" (
    echo.
    echo Starting Network Mode: !SELECTED_IP!
    echo.
    cd backend
    start /min "MarineBackend" cmd /k venv\Scripts\activate ^&^& python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    cd ..
    timeout /t 2 >nul 2>&1
    cd frontend
    start /min "MarineFrontend" cmd /k bun dev --host 0.0.0.0
    cd ..
    echo ========================================
    echo  Network Mode Started
    echo ========================================
    echo.
    echo   Frontend: http://!SELECTED_IP!:5173
    echo   Backend:  http://!SELECTED_IP!:8000
    echo   API Docs: http://!SELECTED_IP!:8000/docs
    echo.
) else (
    echo.
    echo Starting Localhost Mode
    echo.
    cd backend
    start /min "MarineBackend" cmd /k venv\Scripts\activate ^&^& python -m uvicorn app.main:app --port 8000
    cd ..
    timeout /t 2 >nul 2>&1
    cd frontend
    start /min "MarineFrontend" cmd /k bun dev
    cd ..
    echo ========================================
    echo  Localhost Mode Started
    echo ========================================
    echo.
    echo   Frontend: http://localhost:5173
    echo   Backend:  http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
    echo.
)
pause
goto MENU

:START_BACKEND
call :STOP_BACKEND_SILENT
timeout /t 1 >nul 2>&1

if "!NETWORK_MODE!"=="2" (
    cd backend
    start /min "MarineBackend" cmd /k venv\Scripts\activate ^&^& python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    cd ..
    echo Backend started - Tailscale: !SELECTED_IP!:8000
) else if "!NETWORK_MODE!"=="1" (
    cd backend
    start /min "MarineBackend" cmd /k venv\Scripts\activate ^&^& python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    cd ..
    echo Backend started - Network: !SELECTED_IP!:8000
) else (
    cd backend
    start /min "MarineBackend" cmd /k venv\Scripts\activate ^&^& python -m uvicorn app.main:app --port 8000
    cd ..
    echo Backend started - Localhost:8000
)
pause
goto MENU

:START_FRONTEND
call :STOP_FRONTEND_SILENT
timeout /t 1 >nul 2>&1

if "!NETWORK_MODE!"=="2" (
    cd frontend
    start /min "MarineFrontend" cmd /k bun dev --host 0.0.0.0
    cd ..
    echo Frontend started - Tailscale: !SELECTED_IP!:5173
) else if "!NETWORK_MODE!"=="1" (
    cd frontend
    start /min "MarineFrontend" cmd /k bun dev --host 0.0.0.0
    cd ..
    echo Frontend started - Network: !SELECTED_IP!:5173
) else (
    cd frontend
    start /min "MarineFrontend" cmd /k bun dev
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
REM Kill backend processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
REM Kill frontend processes
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
REM Close windows by title
taskkill /FI "WINDOWTITLE eq MarineBackend" /F 2>nul
taskkill /FI "WINDOWTITLE eq MarineFrontend" /F 2>nul
echo Done
timeout /t 1 >nul 2>&1
goto :EOF

:STOP_BACKEND_SILENT
echo Stopping backend...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
taskkill /FI "WINDOWTITLE eq MarineBackend" /F 2>nul
timeout /t 1 >nul 2>&1
goto :EOF

:STOP_FRONTEND_SILENT
echo Stopping frontend...
taskkill /F /IM bun.exe 2>nul
taskkill /F /IM node.exe 2>nul
taskkill /FI "WINDOWTITLE eq MarineFrontend" /F 2>nul
timeout /t 1 >nul 2>&1
goto :EOF

:STATUS
cls
echo ========================================
echo Service Status
echo ========================================
echo.
echo Process Status:
tasklist 2>nul | findstr /I "python.exe" >nul
if !errorlevel!==0 (echo   Backend:  RUNNING) else (echo   Backend:  STOPPED)

tasklist 2>nul | findstr /I "bun.exe node.exe" >nul
if !errorlevel!==0 (echo   Frontend: RUNNING) else (echo   Frontend: STOPPED)

echo.
echo ----------------------------------------
echo Current Mode:
if "!NETWORK_MODE!"=="2" (
    echo   Tailscale Mode [!TAILSCALE_IP!]
) else if "!NETWORK_MODE!"=="1" (
    echo   Network Mode [!SELECTED_IP!]
) else (
    echo   Localhost Mode
)

echo.
echo ----------------------------------------
echo Development URLs:
echo   Localhost:
echo     http://localhost:5173
echo     http://localhost:8000/docs
echo.
if !IP_COUNT! GTR 0 (
    echo   Network:
    for /L %%i in (1,1,!IP_COUNT!) do (
        set CURRENT_IP=!IP_%%i!
        echo !CURRENT_IP! | findstr /b "100." >nul
        if !errorlevel!==0 (
            echo     !CURRENT_IP!:5173 [Tailscale]
        ) else (
            echo     !CURRENT_IP!:5173
        )
    )
)

echo.
echo ----------------------------------------
echo Production NAS (Docker):
echo   https://neptus-station.boga-ulmer.ts.net
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
