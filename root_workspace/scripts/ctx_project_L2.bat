@echo off
rem Double-click: build one project's L2 pack. Prompts for the project name.
cd /d "%~dp0.."
set /p PROJECT=Project name:
if not exist "scripts\out" mkdir "scripts\out"
python scripts\build_context_txt.py --scope project --project %PROJECT% --level 2 -o "scripts\out\%PROJECT%-L2.txt"
echo.
echo Wrote scripts\out\%PROJECT%-L2.txt
pause
