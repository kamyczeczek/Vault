@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

REM Sprawdzenie czy python jest dostępny
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Nie znaleziono polecenia 'python' w systemie.
    echo Upewnij sie, ze Python jest zainstalowany i dodany do PATH.
    pause
    exit /b 1
)

python -u ask.py
pause
