@echo off
setlocal
echo Packing timeseries project with Repomix (config: repomix.config.json)...
node "%APPDATA%\npm\node_modules\repomix\bin\repomix.cjs" . --config repomix.config.json %*
endlocal
