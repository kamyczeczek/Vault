@echo off
chcp 65001 >nul
cd /d "%~dp0"
set COUNT=%1
if "%COUNT%"=="" set COUNT=10
echo Generuje %COUNT% sesji EXACT (moze potrwac)...
python extract_exact_sessions.py --count %COUNT%
echo.
pause