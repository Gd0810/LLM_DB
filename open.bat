@echo off
title Flask Dev Server

:: ============================================================
::  CHANGE THESE TWO PATHS ONLY
:: ============================================================
set VENV_DIR=F:\students\voorhees\D_V\my_flask_app\.venv\Scripts\activate.bat
set PROJECT_DIR=F:\students\voorhees\D_V\my_flask_app
:: ============================================================

set PORT=5000

echo.
echo  =============================================
echo   Flask Dev Server
echo   Venv    : %VENV_DIR%
echo   Project : %PROJECT_DIR%
echo   Port    : %PORT%
echo  =============================================
echo.

:: Activate virtual environment
if not exist "%VENV_DIR%" (
    echo  [ERROR] Venv not found:
    echo          %VENV_DIR%
    pause
    exit /b 1
)
call "%VENV_DIR%"
echo  [OK] Virtual environment activated.
echo.

:: Go to project folder (where app.py lives)
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo  [ERROR] Project folder not found:
    echo          %PROJECT_DIR%
    pause
    exit /b 1
)

:: Confirm app.py is here
if not exist "app.py" (
    echo  [ERROR] app.py not found in:
    echo          %PROJECT_DIR%
    echo.
    echo  Run this in CMD to locate it:
    echo  dir /s /b "%PROJECT_DIR%\app.py"
    pause
    exit /b 1
)
echo  [OK] app.py found.
echo.

:: Open browser after delay
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:%PORT%"
echo  [OK] Browser opens in 3 seconds...
echo.

:: Start Flask server
echo  [OK] Starting server  --  press CTRL+C to stop
echo  -----------------------------------------------
python app.py

echo.
echo  [INFO] Server stopped.
pause