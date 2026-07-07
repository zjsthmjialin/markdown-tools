@echo off
cd /d "%~dp0"

echo ============================================
echo   MarkAny project cleanup
echo ============================================
echo.

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: git not found in PATH.
  echo.
  pause
  exit /b 1
)

echo [0/3] Removing stale git lock if present ...
if exist ".git\index.lock" (
  del /f /q ".git\index.lock"
  echo   removed .git\index.lock
) else (
  echo   no stale lock
)
echo.

echo [1/3] Deleting dead code dir src\python\markdown ...
if exist "src\python\markdown" (
  rmdir /s /q "src\python\markdown"
  echo   deleted src\python\markdown
) else (
  echo   not found, skipped
)
echo.

echo [2/3] Untracking ignored-but-committed files ...
git rm -r --cached --ignore-unmatch dist-electron
git rm --cached --ignore-unmatch ".claude/settings.local.json"
git rm -r --cached --ignore-unmatch test_files/output
git rm --cached --ignore-unmatch test_files/sample_output.html
echo.

echo [3/3] Staging changes ...
git add -A
echo.
echo ============================================
echo   Preview (git status)
echo ============================================
git status -s
echo.
echo Press any key to COMMIT, or close the window to abort.
pause >nul
git commit -m "chore: clean dead reverse-conversion code, fix tests/deps, update .gitignore"
echo.
echo Done.
pause
