@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

rem Output MUST stay in a dot-folder: Obsidian ignores paths starting with ".".
rem A 50 MB .md at the vault root freezes the app (metadata cache parses every note).
if not exist ".export" mkdir ".export"
set OUT=%1
if "%OUT%"=="" set OUT=.export\vault_export.md
rem Guard: if the caller passed a bare filename, keep it out of the vault root.
if not "%OUT:~0,1%"=="." set OUT=.export\%OUT%

echo.
echo === Repomix Vault Export ===
echo Workspace: %CD%
echo Output file: %OUT%
echo.

call npx repomix --output "%OUT%"
if errorlevel 1 (
    echo.
    echo [ERROR] repomix failed or npx is not available.
    set FAILED=1
    goto :end
)

echo.
echo [SUCCESS] Wygenerowano plik: %OUT%
echo.

:end
if "%~1"=="" pause
if defined FAILED (endlocal & exit /b 1)
endlocal & exit /b 0
