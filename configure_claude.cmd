@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" scripts\configure_claude.py
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python scripts\configure_claude.py
  ) else (
    py -3 scripts\configure_claude.py
  )
)
pause
