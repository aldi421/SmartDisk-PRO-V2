@echo off
setlocal
cd /d "%~dp0"
title Build SmartDiskAnalyzer EXE

echo ============================================
echo   SmartDiskAnalyzer - Windows EXE Builder
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python Launcher tidak ditemukan.
  echo Install Python 3.11 atau lebih baru dari python.org, lalu centang Add Python to PATH.
  pause
  exit /b 1
)

echo [1/3] Installing dependencies...
py -m pip install --upgrade pip
if errorlevel 1 goto :failed
py -m pip install -r requirements.txt
if errorlevel 1 goto :failed
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto :failed

echo.
echo [2/3] Building standalone Windows application...
py -m PyInstaller --noconfirm --clean --windowed --onefile --name SmartDiskAnalyzer --collect-all customtkinter main.py
if errorlevel 1 goto :failed

echo.
echo [3/3] Done!
echo EXE location: %CD%\dist\SmartDiskAnalyzer.exe
echo Double-click that file to run the app. No CMD command needed.
echo.
pause
exit /b 0

:failed
echo.
echo [ERROR] Build failed. Baca pesan error di atas, lalu coba lagi.
pause
exit /b 1
