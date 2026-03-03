@echo off
REM TuniTech Advisor API - Quick Start Script for Windows
echo ======================================
echo TuniTech Advisor API - Starting...
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv venv
    echo [+] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/update dependencies
echo [*] Installing dependencies...
pip install -r requirements.txt --quiet
echo [+] Dependencies installed
echo.

REM Create .env if it doesn't exist
if not exist ".env" (
    echo [*] Creating .env file from template...
    copy .env.example .env
    echo [+] .env file created
    echo.
)

REM Check if data exists
if not exist "dataset\unified_smartphones_filled.csv" (
    echo [!] WARNING: Dataset not found!
    echo     Expected: dataset\unified_smartphones_filled.csv
    echo     Please ensure data is scraped and preprocessed.
    echo.
)

REM Check if models exist
if not exist "mlruns\" (
    echo [!] WARNING: MLflow runs not found!
    echo     Expected: mlruns\ directory
    echo     Please train models first (Week 2).
    echo.
)

echo ======================================
echo Starting FastAPI server...
echo ======================================
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/v1/health
echo.
echo Press Ctrl+C to stop the server
echo ======================================
echo.

REM Run the API
python run_api.py

pause
