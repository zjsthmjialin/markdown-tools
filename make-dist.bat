@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   MarkAny  make distribution zip
echo ============================================
echo.

if exist "_preview.png" del /f /q "_preview.png"

set "STAGE=dist-package\MarkAny-1.0.3"
set "EXE=release\MarkAny-Setup-1.0.3.exe"
set "ZIP=dist-package\MarkAny-1.0.3-dist.zip"

if not exist "%STAGE%" (echo ERROR: staging folder %STAGE% missing. & pause & exit /b 1)
if not exist "%EXE%" (echo ERROR: installer %EXE% not found - run build.bat first. & pause & exit /b 1)

echo [1/3] Copying installer into package ...
copy /y "%EXE%" "%STAGE%\" >nul
if errorlevel 1 (echo ERROR: copy failed. & pause & exit /b 1)
echo   done.
echo.

echo [2/3] Files to be packaged:
dir /b "%STAGE%"
echo.

echo [3/3] Creating zip with tar (UTF-8 filenames) ...
if exist "%ZIP%" del /f /q "%ZIP%"
tar -a -c -f "%ZIP%" -C "dist-package" "MarkAny-1.0.3"
if errorlevel 1 (echo ERROR: tar failed ^(need Windows 10 1803+^). & pause & exit /b 1)
echo.

echo ============================================
echo   PACKAGE OK
echo ============================================
for %%A in ("%ZIP%") do echo   %~fA  (%~zA bytes)
echo.
start "" explorer "%~dp0dist-package"
pause
