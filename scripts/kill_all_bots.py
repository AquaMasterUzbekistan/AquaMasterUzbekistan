import subprocess
import os

ps_kill = """
Get-CimInstance Win32_Process | Where-Object { 
    $_.CommandLine -like '*bot.py*' -or 
    $_.CommandLine -like '*main.py*' -or 
    $_.CommandLine -like '*run_bot_loop.bat*' 
} | ForEach-Object {
    Write-Host "Killing PID $($_.ProcessId): $($_.CommandLine)"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("KILL RESULTS:")
print(res.stdout)
