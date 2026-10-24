@echo off
rem Double-click: build the whole-workspace L0 router pack.
cd /d "%~dp0.."
if not exist "scripts\out" mkdir "scripts\out"
python scripts\build_context_txt.py --scope root --level 0 -o "scripts\out\root-L0.txt"
echo.
echo Wrote scripts\out\root-L0.txt
pause
