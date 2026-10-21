@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (set "PY=py -3") else (set "PY=python")
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 goto failed
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name "WindowsAdminToolkit" --icon "assets\toolkit.ico" --add-data "assets\toolkit.ico;assets" app.py
if errorlevel 1 goto failed
 echo.
 echo SUCCESS: dist\WindowsAdminToolkit.exe
 echo Test the EXE on a Windows computer before distributing it.
 pause
 exit /b 0
:failed
 echo.
 echo Build failed. Please check the errors above.
 pause
 exit /b 1
