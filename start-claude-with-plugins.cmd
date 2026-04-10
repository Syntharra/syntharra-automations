@echo off
REM Start Claude with all local plugin directories from this workspace.
SETLOCAL
SET SCRIPT_DIR=%~dp0
SET PS1=%SCRIPT_DIR%start-claude-with-plugins.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
ENDLOCAL
