@echo off
REM Simple launcher for MytharaConnect
REM Just double-click this file to run the bot

chcp 65001 >nul
echo Starting MytharaConnect...
echo.

"C:\Users\Mythara\AppData\Local\Programs\Python\Python311\python.exe" "%~dp0mythara_connect.py"

echo.
echo MytharaConnect finished.
pause
