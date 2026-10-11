import subprocess
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# PowerShell script to find all python processes with commandline
ps_cmd = """
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*python*' -or $_.CommandLine -like '*main.py*' -or $_.CommandLine -like '*bot.py*' } | Select-Object ProcessId, Name, CommandLine | ConvertTo-Json
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("OUTPUT:")
print(res.stdout)
