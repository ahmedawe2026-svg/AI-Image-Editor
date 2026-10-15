@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required.
  pause
  exit /b 1
)
start "" http://127.0.0.1:8765
python server.py
