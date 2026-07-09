@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   MarkAny  one-click build  (onedir)
echo ============================================
echo.

where npm >nul 2>nul || (echo ERROR: npm not found in PATH. & pause & exit /b 1)
python -m PyInstaller --version >nul 2>nul || echo WARNING: PyInstaller not found - run: pip install pyinstaller
echo.

echo [1/6] Cleaning old backend build output ...
if exist "src\python\dist" rmdir /s /q "src\python\dist"
if exist "src\python\build" rmdir /s /q "src\python\build"
echo   cleaned src\python\dist and src\python\build
echo.

echo [2/6] Forcing pure-Python charset-normalizer (avoids mypyc 0xC0000005 crash) ...
python -m pip install --force-reinstall --no-binary charset-normalizer charset-normalizer
if errorlevel 1 (echo WARNING: charset-normalizer reinstall failed - check internet/pip.) else (echo   pure-Python charset-normalizer installed)
echo.

echo [3/6] Tesseract bundle ...
if exist "src\python\tesseract-portable\tesseract.exe" (
  echo   already bundled, skipping bash setup
) else (
  echo   not found, running npm run tesseract:setup ...
  call npm run tesseract:setup
  if errorlevel 1 (echo ERROR: tesseract:setup failed - install Git Bash or run it manually. & pause & exit /b 1)
)
echo.

echo [4/6] Building Python backend with PyInstaller (onedir) ...
call npm run python:build
if errorlevel 1 (echo ERROR: python:build failed. See output above. & pause & exit /b 1)
if not exist "src\python\dist\markany-backend\markany-backend.exe" (echo ERROR: onedir exe not produced. & pause & exit /b 1)
rem Safety net: chardet ships mypyc .pyd that crash when frozen; charset_normalizer covers it.
if exist "src\python\dist\markany-backend\_internal\chardet" (
  rmdir /s /q "src\python\dist\markany-backend\_internal\chardet"
  echo   removed bundled chardet (safety net)
)
echo   onedir backend OK
echo.

echo [5/6] Compiling frontend - tsc then vite ...
call npx tsc
if errorlevel 1 (echo ERROR: tsc failed. & pause & exit /b 1)
call npx vite build
if errorlevel 1 (echo ERROR: vite build failed. & pause & exit /b 1)
echo.

echo [6/6] Packaging installer with electron-builder ...
call npx electron-builder --win
if errorlevel 1 (echo ERROR: electron-builder failed. & pause & exit /b 1)
echo.

echo ============================================
echo   BUILD OK
echo ============================================
if exist "release" (
  echo Installer^(s^) in release folder:
  dir /b "release\*.exe"
  echo.
  start "" explorer "%~dp0release"
) else (
  echo WARNING: release folder not found.
)
echo.
echo Tip: run test-backend.bat before installing to confirm the backend starts.
pause
