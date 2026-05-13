@echo off
title Books Daily Updates

echo ============================================
echo   Books Daily Updates - Setup ^& Run
echo ============================================
echo.

:: Try to use Python 3.12 or 3.13 (best wheel support)
set PYTHON_CMD=python
py -3.12 --version >nul 2>&1 && set PYTHON_CMD=py -3.12 && goto :found
py -3.13 --version >nul 2>&1 && set PYTHON_CMD=py -3.13 && goto :found
py -3.11 --version >nul 2>&1 && set PYTHON_CMD=py -3.11 && goto :found
%PYTHON_CMD% --version >nul 2>&1 || (
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)
:found
%PYTHON_CMD% --version

:: Create venv if needed
if not exist "venv\" (
    echo [1/4] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)

:: Activate
call venv\Scripts\activate.bat

:: Install deps
echo [2/4] Installing dependencies...
pip install -q fastapi "uvicorn[standard]" sqlalchemy pydantic pydantic-settings apscheduler httpx python-multipart aiofiles
pip install -q pandas openpyxl 2>nul
pip install -q python-telegram-bot twilio sentence-transformers 2>nul

:: Generate sample data
echo [3/4] Generating sample Excel files...
python backend\data\generate_sample.py

:: Start backend
echo [4/4] Starting server...
echo.
echo ============================================
echo   App running at: http://localhost:8000
echo   API Docs at:    http://localhost:8000/docs
echo ============================================
echo.

python run.py

pause
