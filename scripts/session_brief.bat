@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set COUNT=%1
if "%COUNT%"=="" set COUNT=20
set OUT=%2
if "%OUT%"=="" set OUT=scripts\_scratch\sessions\02_products\session_brief.md

echo.
echo === Session brief (valuable only) ===
echo Workspace: %CD%
echo Liczba sesji: %COUNT%
echo.

where python.exe >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python.exe not found in PATH.
    set FAILED=1
    goto :end
)

python.exe scripts\session_brief.py --last %COUNT% --valuable -o "%OUT%"
if errorlevel 1 (
    echo.
    echo [ERROR] session_brief.py exited with error.
    set FAILED=1
    goto :end
)

echo.
echo Zapisano: %OUT%
echo.

:end
if "%~1"=="" pause
if defined FAILED (endlocal & exit /b 1)
endlocal & exit /b 0
