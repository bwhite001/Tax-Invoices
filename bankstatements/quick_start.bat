@echo off
echo ========================================
echo Bank Statement Extractor - Quick Start
echo ========================================
echo.
echo This script will help you set up and run the bank statement tools.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python is installed.
echo.

REM Check if packages are installed
echo Checking for required packages...
python -c "import pandas, pdfplumber, PyPDF2" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
) else (
    echo Required packages are already installed.
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To use the tools:
echo.
echo 1. Place your bank statement files (PDF or CSV) in the 'statements' folder
echo    - Suncorp files should contain 'suncorp' in filename
echo    - Beyond Bank files should contain 'beyond' in filename
echo    - Zip files should contain 'zip' in filename
echo    - Afterpay files should contain 'afterpay' in filename
echo.
echo 2. Run: python bank_statement_extractor.py
echo.
echo 3. Then run: python expense_cataloger.py
echo.
echo Your processed files will be in the 'extracted' folder
echo.
pause
