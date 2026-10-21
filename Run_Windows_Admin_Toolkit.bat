@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  py -3 app.py
) else (
  where python >nul 2>&1
  if %ERRORLEVEL% EQU 0 (
    python app.py
  ) else (
    echo Python 3.10 or newer is required.
    echo Install Python from https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )
)
if errorlevel 1 pause
