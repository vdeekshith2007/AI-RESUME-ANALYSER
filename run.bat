@echo off
chcp 65001 >nul
title AI Resume Analyzer - Startup

echo ============================================================
echo           AI Resume Analyzer - Startup Script -analyzer
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.9 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed.
python --version
echo.

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Streamlit is not installed.
    echo Installing dependencies...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install dependencies.
        echo Please run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully.
) else (
    echo [OK] Streamlit is installed.
)

echo.
echo ============================================================
echo           Starting AI Resume Analyzer...
echo ============================================================
echo.
echo The application will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start Streamlit
python -m streamlit run app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start Streamlit.
    echo.
    pause
    exit /b 1
)