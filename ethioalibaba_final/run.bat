@echo off
title EthioAlibaba - Website + Telegram Bot
echo ==========================================
echo   EthioAlibaba - Starting...
echo   Website:  http://127.0.0.1:5000
echo   Bot:      Polling started
echo ==========================================
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Download it from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during install!
    pause
    exit /b
)
pip install -r requirements.txt
python app.py
pause
