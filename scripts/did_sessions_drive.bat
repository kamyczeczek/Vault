@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set COUNT=%1
if "%COUNT%"=="" set COUNT=20
set OUT=%2
if "%OUT%"=="" set OUT=scripts\_scratch\sessions\02_products\did_sessions.md

echo.
echo === Agent did / produced export + sync do Google Drive ===
echo Workspace: %CD%
echo Liczba sesji: %COUNT%
echo Cel: %OUT%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found in PATH.
    set FAILED=1
    goto :end
)

call scripts\did_sessions.bat %COUNT% "%OUT%"
if errorlevel 1 (
    echo.
    echo [ERROR] did_sessions.bat exited with error.
    set FAILED=1
    goto :end
)

python scripts\sync_did_sessions.py "%OUT%"
if errorlevel 1 (
    echo.
    echo [ERROR] sync_did_sessions.py exited with error.
    echo         Cel synchronizacji rozpoznaj komenda:
    echo             python scripts\sync_did_sessions.py --detect
    set FAILED=1
    goto :end
)

echo.
echo Zapisano: %OUT%
echo Zsynchronizowano z Google Drive dla komputerow ^(ten sam plik, ten sam link^).
echo.

:end
if "%~1"=="" pause
if defined FAILED (endlocal & exit /b 1)
endlocal & exit /b 0
