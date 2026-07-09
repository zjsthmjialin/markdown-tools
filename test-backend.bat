@echo off
setlocal
cd /d "%~dp0src\python\dist\markany-backend"

echo ============================================
echo   Test backend exe directly (onedir)
echo ============================================
echo Running markany-backend.exe ...
echo If OK you should see: Python conversion service running on port 8765
echo If it crashes, the Python error will be shown below.
echo Press Ctrl+C to stop once you have read the output.
echo --------------------------------------------
markany-backend.exe
echo --------------------------------------------
echo Backend exited with code %ERRORLEVEL%
pause
