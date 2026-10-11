@echo off
chcp 65001 > nul
title AquaMaster Uzbekistan Telegram Bot
echo =======================================================
echo   AquaMaster Uzbekistan Telegram Bot ishga tushmoqda...
echo =======================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [XATOLIK] Bot to'xtadi! ErrorLevel: %ERRORLEVEL%
    pause
)
