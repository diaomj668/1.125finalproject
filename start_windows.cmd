@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run.py --open-browser
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python run.py --open-browser
  ) else (
    py -3 run.py --open-browser
  )
)
pause
