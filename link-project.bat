@echo off
REM ============================================
REM AID - Link Project Script
REM Links an external project to AID methodology
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    AID Project Linker (Windows)
echo ========================================
echo.

REM Get AID path (where this script is located)
set "AID_PATH=%~dp0"
set "AID_PATH=%AID_PATH:~0,-1%"

echo AID Installation: %AID_PATH%
echo.

REM Get target project path
if "%~1"=="" (
    set /p "TARGET_PATH=Enter project path to link: "
) else (
    set "TARGET_PATH=%~1"
)

REM Remove trailing backslash if present
if "%TARGET_PATH:~-1%"=="\" set "TARGET_PATH=%TARGET_PATH:~0,-1%"

echo Target Project:   %TARGET_PATH%
echo.

REM Verify target exists
if not exist "%TARGET_PATH%" (
    echo [ERROR] Target folder does not exist: %TARGET_PATH%
    pause
    exit /b 1
)

REM Create .claude directory
echo Creating .claude directory...
if not exist "%TARGET_PATH%\.claude" mkdir "%TARGET_PATH%\.claude"

REM Create junctions (directory links - don't require admin)
echo.
echo Creating directory junctions...

if exist "%TARGET_PATH%\.claude\commands" (
    echo   [SKIP] commands already exists
) else (
    mklink /J "%TARGET_PATH%\.claude\commands" "%AID_PATH%\.claude\commands" >nul 2>nul
    if !errorlevel! equ 0 (
        echo   [OK] .claude\commands linked
    ) else (
        echo   [FALLBACK] Copying commands instead...
        xcopy /E /I /Y "%AID_PATH%\.claude\commands" "%TARGET_PATH%\.claude\commands" >nul
        echo   [OK] .claude\commands copied
    )
)

if exist "%TARGET_PATH%\.claude\skills" (
    echo   [SKIP] skills already exists
) else (
    mklink /J "%TARGET_PATH%\.claude\skills" "%AID_PATH%\.claude\skills" >nul 2>nul
    if !errorlevel! equ 0 (
        echo   [OK] .claude\skills linked
    ) else (
        echo   [FALLBACK] Copying skills instead...
        xcopy /E /I /Y "%AID_PATH%\.claude\skills" "%TARGET_PATH%\.claude\skills" >nul
        echo   [OK] .claude\skills copied
    )
)

REM Create .aid directory
echo.
echo Creating project state directory...
if not exist "%TARGET_PATH%\.aid" mkdir "%TARGET_PATH%\.aid"

REM Create state.json
if not exist "%TARGET_PATH%\.aid\state.json" (
    (
echo {
echo   "$schema": "aid-state-v1",
echo   "version": "1.0",
echo   "initialized_at": "%DATE% %TIME%",
echo   "last_updated": "%DATE% %TIME%",
echo   "current_phase": 1,
echo   "phase_name": "PRD",
echo   "phase_approved": false,
echo   "current_session": {
echo     "active": false,
echo     "role": null,
echo     "phase": null,
echo     "started_at": null,
echo     "revision_count": 0
echo   },
echo   "last_session": {
echo     "role": null,
echo     "phase": null,
echo     "completed_at": null
echo   },
echo   "statistics": {
echo     "total_sessions": 0,
echo     "total_feedback_collected": 0,
echo     "pending_feedback_count": 0,
echo     "last_improvement_run": null,
echo     "sessions_since_last_improvement": 0
echo   },
echo   "notifications": {
echo     "improvement_suggested": false,
echo     "reason": null
echo   }
echo }
    ) > "%TARGET_PATH%\.aid\state.json"
    echo [OK] state.json created
) else (
    echo [SKIP] state.json already exists
)

REM Create context.json
if not exist "%TARGET_PATH%\.aid\context.json" (
    (
echo {
echo   "$schema": "aid-context-v1",
echo   "version": "1.0",
echo   "last_updated": "%DATE% %TIME%",
echo   "current_task": null,
echo   "current_step": null,
echo   "progress": {
echo     "steps_completed": [],
echo     "steps_pending": []
echo   },
echo   "session_notes": [],
echo   "blockers": []
echo }
    ) > "%TARGET_PATH%\.aid\context.json"
    echo [OK] context.json created
) else (
    echo [SKIP] context.json already exists
)

REM Copy .mcp.json (prefer configured one over template)
echo.
echo Copying MCP configuration...
if not exist "%TARGET_PATH%\.mcp.json" (
    if exist "%AID_PATH%\.mcp.json" (
        copy "%AID_PATH%\.mcp.json" "%TARGET_PATH%\.mcp.json" >nul
        echo [OK] .mcp.json copied (with your API tokens)
    ) else if exist "%AID_PATH%\.mcp.json.example" (
        copy "%AID_PATH%\.mcp.json.example" "%TARGET_PATH%\.mcp.json" >nul
        echo [OK] .mcp.json created (edit with your API tokens)
    ) else (
        echo [WARNING] .mcp.json not found
    )
) else (
    echo [SKIP] .mcp.json already exists
)

REM Copy CLAUDE.md
echo.
echo Copying CLAUDE.md...
if not exist "%TARGET_PATH%\CLAUDE.md" (
    if exist "%AID_PATH%\CLAUDE.md" (
        copy "%AID_PATH%\CLAUDE.md" "%TARGET_PATH%\CLAUDE.md" >nul
        echo [OK] CLAUDE.md copied
    )
) else (
    echo [SKIP] CLAUDE.md already exists
)

echo.
echo ========================================
echo    Project Linked Successfully!
echo ========================================
echo.
echo Target: %TARGET_PATH%
echo.
echo Next steps:
echo.
echo 1. Edit %TARGET_PATH%\.mcp.json with your API tokens
echo.
echo 2. Open Claude Code in the project:
echo    cd "%TARGET_PATH%"
echo    claude
echo.
echo 3. Run /aid-start to begin working
echo.
echo ========================================
echo.
pause
