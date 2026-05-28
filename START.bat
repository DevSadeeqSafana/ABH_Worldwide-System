@echo off
title ABH WORLDWIDE MULTIPURPOSE COMPANY - Server
color 0A
cls
echo.
echo  ============================================================
echo    ABH WORLDWIDE MULTIPURPOSE COMPANY
echo    Inventory ^& Sales Management System
echo  ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed.
    echo.
    echo  Download from: https://www.python.org/downloads/
    echo  IMPORTANT: Tick "Add Python to PATH" during install.
    echo.
    pause
    exit /b
)

echo  Setting up... please wait...
pip install flask flask-sqlalchemy werkzeug --quiet --disable-pip-version-check 2>nul

echo  Starting server...
echo.
echo  ============================================================
echo   Once started, this computer opens automatically.
echo   Other devices on the same WiFi: check the network address
echo   printed below and type it into any browser.
echo  ============================================================
echo.

python app.py

echo.
echo  Server stopped.
pause
