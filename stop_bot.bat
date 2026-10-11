@echo off
chcp 65001 > nul
title AquaMaster Uzbekistan - Stop Bot
echo =======================================================
echo   AquaMaster Telegram Bot to'xtatilmoqda...
echo =======================================================
cd /d "%~dp0"
echo stop > stop.flag

powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*bot.py*' -or $_.CommandLine -like '*main.py*' -or $_.CommandLine -like '*run_bot_loop.bat*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host ('To''xtatildi PID: ' + $_.ProcessId) }"

timeout /t 1 > nul
if exist "stop.flag" del /f /q "stop.flag"

echo.
echo [OK] Bot muvaffaqiyatli to'xtatildi!
timeout /t 3 > nul
