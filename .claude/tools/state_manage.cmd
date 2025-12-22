@echo off
REM Power BI Analyst Skill - State Manager (CMD Fallback)
REM
REM Minimal fallback for environments where PowerShell is unavailable.
REM Delegates to PowerShell script when possible, provides basic operations otherwise.
REM
REM Usage:
REM   state_manage.cmd summary
REM   state_manage.cmd create-task "name" [workflow]
REM   state_manage.cmd complete "task_id"
REM   state_manage.cmd help

setlocal EnableDelayedExpansion

set "STATE_PATH=.claude\state.json"
set "TASKS_DIR=.claude\tasks"
set "SCRIPT_DIR=%~dp0"

REM Check if PowerShell is available (prefer it)
where powershell >nul 2>&1
if %ERRORLEVEL% equ 0 (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%state_manage.ps1" %*
    exit /b %ERRORLEVEL%
)

REM Fallback to minimal CMD implementation
if "%~1"=="" goto :help
if "%~1"=="help" goto :help
if "%~1"=="--help" goto :help
if "%~1"=="-h" goto :help
if "%~1"=="summary" goto :summary
if "%~1"=="reset" goto :reset
if "%~1"=="create-task" goto :create_task
if "%~1"=="list-tasks" goto :list_tasks
if "%~1"=="list-locks" goto :list_locks

echo ERROR: Unknown command: %~1
echo Use 'state_manage.cmd help' for usage information.
exit /b 1

:help
echo Power BI Analyst Skill - State Manager (CMD Fallback)
echo.
echo NOTE: This is a minimal fallback. For full functionality, use:
echo   - state_manage.ps1 (PowerShell - recommended for Windows)
echo   - state_manage.sh (Bash + jq - for macOS/Linux)
echo.
echo USAGE:
echo   state_manage.cmd summary                Show state summary
echo   state_manage.cmd create-task "name"     Create new task (basic)
echo   state_manage.cmd list-tasks             List active tasks
echo   state_manage.cmd list-locks             List all locks
echo   state_manage.cmd reset                  Reset all state
echo   state_manage.cmd help                   Show this help
echo.
echo For full operations (complete, fail, archive, lock, release):
echo   Install PowerShell or use state_manage.ps1 directly.
echo.
exit /b 0

:summary
if not exist "%STATE_PATH%" (
    echo {"error": "No state file found. Run create-task first."}
    exit /b 1
)
echo Reading state from %STATE_PATH%...
type "%STATE_PATH%"
exit /b 0

:reset
if exist "%STATE_PATH%" (
    del /f "%STATE_PATH%"
)
echo State reset complete
exit /b 0

:create_task
set "TASK_NAME=%~2"
if "%TASK_NAME%"=="" set "TASK_NAME=unnamed"
set "WORKFLOW=%~3"
if "%WORKFLOW%"=="" set "WORKFLOW=evaluate"

REM Get timestamp
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do (
    set "TIMESTAMP=%%a%%b%%c%%d"
)

REM Sanitize name (basic - lowercase not possible in pure CMD)
set "SAFE_NAME=%TASK_NAME: =-%"
set "TASK_ID=%SAFE_NAME%-%TIMESTAMP%"
set "TASK_PATH=%TASKS_DIR%\%TASK_ID%"

REM Create directories
if not exist ".claude" mkdir ".claude"
if not exist "%TASKS_DIR%" mkdir "%TASKS_DIR%"
mkdir "%TASK_PATH%"

REM Create findings.md
(
echo # Task Blackboard: %TASK_NAME%
echo.
echo **Status:** in_progress
echo **Task ID:** %TASK_ID%
echo **Workflow:** %WORKFLOW%
echo **Created:** %date% %time%
echo **Backend:** cmd
echo.
echo ---
echo.
echo ## Section 1: Requirements
echo *Pending...*
) > "%TASK_PATH%\findings.md"

REM Create minimal state.json if not exists
if not exist "%STATE_PATH%" (
    (
    echo {
    echo   "session": {
    echo     "started": "%date% %time%",
    echo     "last_activity": "%date% %time%",
    echo     "skill_version": "1.0.0",
    echo     "state_backend": "cmd",
    echo     "mcp_available": false
    echo   },
    echo   "active_tasks": {},
    echo   "resource_locks": {},
    echo   "archived_tasks": []
    echo }
    ) > "%STATE_PATH%"
)

echo %TASK_ID%
exit /b 0

:list_tasks
if not exist "%STATE_PATH%" (
    echo {}
    exit /b 0
)
echo Active tasks from %STATE_PATH%:
findstr /i "task_id" "%STATE_PATH%" 2>nul || echo No tasks found
exit /b 0

:list_locks
if not exist "%STATE_PATH%" (
    echo {}
    exit /b 0
)
echo Resource locks from %STATE_PATH%:
findstr /i "resource_locks" "%STATE_PATH%" 2>nul || echo No locks found
exit /b 0

endlocal
