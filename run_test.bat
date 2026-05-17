@echo off
cd /d "%~dp0win-unpacked"
echo Starting MarkAny...
MarkAny.exe --disable-gpu --no-sandbox 2>&1
echo.
echo Exit code: %ERRORLEVEL%
pause
