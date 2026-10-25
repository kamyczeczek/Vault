@echo off
rem Double-click: build the whole-workspace L2 standard pack.
cd /d "%~dp0.."
if not exist "scripts\out" mkdir "scripts\out"
python scripts\build_context_txt.py --scope root --level 2 -o "scripts\out\root-L2.txt"
echo.
echo Wrote scripts\out\root-L2.txt
pause
