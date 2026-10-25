@echo off
rem Double-click: build one project's L3 deep pack with capped source. Prompts for the project name.
cd /d "%~dp0.."
set /p PROJECT=Project name:
if not exist "scripts\out" mkdir "scripts\out"
python scripts\build_context_txt.py --scope project --project %PROJECT% --level 3 --include-source -o "scripts\out\%PROJECT%-L3.txt"
echo.
echo Wrote scripts\out\%PROJECT%-L3.txt
pause
