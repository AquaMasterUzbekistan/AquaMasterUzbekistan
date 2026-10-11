' AquaMaster Uzbekistan Telegram Bot - Fonda (oynasiz / yashirin) 24/7 ishga tushirish
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath
WshShell.Run "cmd.exe /c run_bot_loop.bat", 0, False
Set WshShell = Nothing
Set fso = Nothing
