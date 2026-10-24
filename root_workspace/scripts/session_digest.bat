@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set COUNT=%1
if "%COUNT%"=="" set COUNT=100
set CLASSIFY=%2

set OUTDIR=scripts\_scratch\sessions\02_products\session-digest

echo.
echo === Session digest (L0/L1) ===
echo Workspace: %CD%
echo Liczba sesji: %COUNT%
if /i "%CLASSIFY%"=="--classify" echo Tryb: mechanical + classify (candidate, no promotion)
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found in PATH.
    set FAILED=1
    goto :end
)

python scripts\session_digest.py --count %COUNT% --out-dir "%OUTDIR%"
if errorlevel 1 (
    echo.
    echo [ERROR] session_digest.py exited with error.
    set FAILED=1
    goto :end
)

if /i "%CLASSIFY%"=="--classify" (
    python scripts\session_digest.py --classify --count %COUNT% --out-dir "%OUTDIR%"
    if errorlevel 1 (
        echo.
        echo [ERROR] session_digest.py --classify exited with error.
        set FAILED=1
        goto :end
    )
)

echo.
echo Zapisano:
echo   %OUTDIR%\session_digest.md
echo   %OUTDIR%\session_cards.md
if /i "%CLASSIFY%"=="--classify" echo   %OUTDIR%\candidates\digest.judgment.md
echo.

:end
if "%~1"=="" pause
if defined FAILED (endlocal & exit /b 1)
endlocal & exit /b 0
