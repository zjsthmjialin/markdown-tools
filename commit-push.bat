@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   MarkAny  commit ^& push packaging fix
echo ============================================
echo.

where git >nul 2>nul || (echo ERROR: git not found in PATH. & pause & exit /b 1)
if exist ".git\index.lock" del /f /q ".git\index.lock"

echo [1/4] Removing one-off diagnostic scripts ...
for %%f in (diag-backend.bat diag-wer.bat diag-wer.ps1 fix-try.bat fix-try.ps1 fix-try2.bat fix-try2.ps1 inspect.bat inspect.ps1 backend-verbose.log cleanup.bat) do (
  if exist "%%f" ( del /f /q "%%f" & echo   deleted %%f )
)
echo.

echo [2/4] Staging changes ...
git add -A
echo.

echo [3/4] Preview (git status) ...
echo ============================================
git status -s
echo ============================================
echo.
echo Press any key to COMMIT ^& PUSH, or close the window to abort.
pause >nul

git commit -m "fix(packaging): onedir build + exclude chardet (mypyc 0xC0000005 crash); force pure-Python charset-normalizer; add build/test scripts"
echo.
echo [4/4] Pushing to origin ...
git push origin master
echo.
echo Done.
pause
