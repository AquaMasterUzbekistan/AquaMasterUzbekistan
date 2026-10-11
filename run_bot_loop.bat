@echo off
chcp 65001 > nul
cd /d "%~dp0"
if not exist "logs" mkdir "logs"

echo [%date% %time%] === AquaMaster 24/7 Xizmati Boshlandi === >> logs\service.log

:loop
echo [%date% %time%] Bot ishga tushirildi... >> logs\service.log
.venv\Scripts\python.exe bot.py >> logs\bot_output.log 2>&1
set EXITCODE=%errorlevel%

echo [%date% %time%] Bot to'xtadi (Chiqish kodi: %EXITCODE%). 5 soniyada qayta ishga tushiriladi... >> logs\service.log

REM Agar to'xtatish buyrug'i berilgan bo'lsa yoki to'xtatish fayli mavjud bo'lsa
if exist "stop.flag" (
    echo [%date% %time%] To'xtatish bayrog'i (stop.flag) topildi. Xizmat yakunlandi. >> logs\service.log
    del /f /q "stop.flag"
    exit /b 0
)

timeout /t 5 /nobreak > nul
goto loop
