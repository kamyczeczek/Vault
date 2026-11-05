@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set COUNT=%1
if "%COUNT%"=="" set COUNT=5
set OUT=%2
if "%OUT%"=="" set OUT=scripts\_scratch\sessions\02_products\raw_sessions.md
set DRIVE_TARGET=%~3
if "%DRIVE_TARGET%"=="" set DRIVE_TARGET=G:\My Drive

echo.
echo === Raw sessions export + sync do Google Drive (G:\My Drive) ===
echo Workspace: %CD%
echo Liczba sesji: %COUNT%
echo Cel lokalny: %OUT%
echo Folder Google Drive: %DRIVE_TARGET%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python not found in PATH.
    set FAILED=1
    goto :end
)

python scripts\extract_exact_sessions.py --count %COUNT% -o "%OUT%"
if errorlevel 1 (
    echo.
    echo [ERROR] extract_exact_sessions.py exited with error.
    set FAILED=1
    goto :end
)

python scripts\sync_did_sessions.py "%OUT%" --target "%DRIVE_TARGET%"
if errorlevel 1 (
    echo.
    echo [ERROR] sync_did_sessions.py exited with error.
    echo         Cel synchronizacji rozpoznaj komenda:
    echo             python scripts\sync_did_sessions.py --detect
    set FAILED=1
    goto :end
)

echo.
echo Zapisano i zsynchronizowano z Google Drive: %OUT%
echo.

:end
if "%~1"=="" pause
if defined FAILED (endlocal & exit /b 1)
endlocal & exit /b 0
