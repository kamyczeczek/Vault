@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set COUNT=%1
if "%COUNT%"=="" set COUNT=1
set OUT=%2
if "%OUT%"=="" set OUT=scripts\_scratch\sessions\02_products\did_sessions.md

echo.
echo === Agent did / produced export ===
echo Workspace: %CD%
echo Liczba sesji: %COUNT%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found in PATH.
    set FAILED=1
    goto :end
)

python scripts\extract_did.py %COUNT% -o "%OUT%"
if errorlevel 1 (
    echo.
    echo [ERROR] extract_did.py exited with error.
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
