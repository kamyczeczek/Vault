@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set COUNT=%1
if "%COUNT%"=="" set COUNT=10

echo.
echo === Raw sessions export ===
echo Workspace: %CD%
echo Liczba sesji: %COUNT%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found in PATH.
    set FAILED=1
    goto :end
)

python scripts\extract_exact_sessions.py --count %COUNT% -o "scripts\_scratch\sessions\02_products\raw_sessions.md"
if errorlevel 1 (
    echo.
    echo [ERROR] extract_exact_sessions.py exited with error.
    set FAILED=1
    goto :end
)

echo.
echo Zapisano: scripts\_scratch\sessions\02_products\raw_sessions.md
echo.

:end
if "%~1"=="" pause
if defined FAILED (endlocal & exit /b 1)
endlocal & exit /b 0
