@echo off
setlocal

REM Run repomix workflow using Python wrapper
python "%~dp0scripts\run_repomix.py" %*

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Repomix generation failed.
    exit /b %ERRORLEVEL%
)

echo [OK] Done.
