"""Configure Windows Startup shortcut for AquaMaster Bot."""

import os
import sys
from pathlib import Path

def create_startup_shortcut():
    try:
        import win32com.client
    except ImportError:
        # Fallback to creating a batch file in startup
        appdata = os.environ.get("APPDATA")
        if not appdata:
            print("APPDATA not found.")
            return False
        startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_dir.mkdir(parents=True, exist_ok=True)
        bat_path = startup_dir / "AquaMasterBot_Autostart.bat"
        project_dir = Path(__file__).resolve().parent
        vbs_path = project_dir / "start_bot_background.vbs"
        bat_content = f'@echo off\nwscript.exe "{vbs_path}"\n'
        bat_path.write_text(bat_content, encoding="utf-8")
        print(f"Startup batch file created at: {bat_path}")
        return True

    appdata = os.environ.get("APPDATA")
    startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)
    shortcut_path = startup_dir / "AquaMasterBot.lnk"
    
    project_dir = Path(__file__).resolve().parent
    vbs_path = project_dir / "start_bot_background.vbs"

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = "wscript.exe"
    shortcut.Arguments = f'"{vbs_path}"'
    shortcut.WorkingDirectory = str(project_dir)
    shortcut.Description = "AquaMaster Uzbekistan Telegram Bot 24/7 Autostart"
    shortcut.save()
    print(f"Startup shortcut successfully created at: {shortcut_path}")
    return True

if __name__ == "__main__":
    create_startup_shortcut()
