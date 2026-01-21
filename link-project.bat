@echo off
REM ============================================
REM AID - Link Project Script
REM Creates junctions/links from project to AID
REM Usage: link-project.bat [path] [--force] [--copy]
REM NOTE: Uses junctions (no admin required)
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

echo AID Installation: "!AID_PATH!"
echo.

REM Check for flags
set "FORCE_MODE=0"
set "COPY_MODE=0"
for %%a in (%*) do (
    if /i "%%a"=="--force" set "FORCE_MODE=1"
    if /i "%%a"=="-f" set "FORCE_MODE=1"
    if /i "%%a"=="--copy" set "COPY_MODE=1"
)

REM Get target project path (skip flags)
set "TARGET_PATH="
for %%a in (%*) do (
    if /i not "%%a"=="--force" if /i not "%%a"=="-f" if /i not "%%a"=="--copy" (
        if "!TARGET_PATH!"=="" set "TARGET_PATH=%%~a"
    )
)

REM If no path provided, ask for it
if "!TARGET_PATH!"=="" (
    set /p "TARGET_PATH=Enter project path to link: "
)

REM Remove trailing backslash if present
if "!TARGET_PATH:~-1!"=="\" set "TARGET_PATH=!TARGET_PATH:~0,-1!"

echo Target Project:   "!TARGET_PATH!"
if "!FORCE_MODE!"=="1" (
    echo Mode:             FORCE (will recreate links/copies^)
)
if "!COPY_MODE!"=="1" (
    echo Mode:             COPY (not using symlinks^)
)
echo.

REM Verify target exists
if not exist "!TARGET_PATH!" (
    echo [ERROR] Target folder does not exist: "!TARGET_PATH!"
    pause
    exit /b 1
)

REM Check for existing links and ask to update
if "!FORCE_MODE!"=="0" (
    if exist "!TARGET_PATH!\.claude" (
        echo Existing .claude folder detected.
        echo   [Y] Yes, recreate links/copies
        echo   [N] No, keep existing
        echo.
        set /p "UPDATE_CHOICE=Your choice (Y/N): "
        if /i "!UPDATE_CHOICE!"=="Y" set "FORCE_MODE=1"
        echo.
    )
)

REM ============================================
REM Create .claude directory
REM ============================================
echo Creating .claude directory...
if not exist "!TARGET_PATH!\.claude" mkdir "!TARGET_PATH!\.claude"

REM ============================================
REM Create junctions OR copy (based on mode)
REM ============================================
if "!COPY_MODE!"=="1" (
    echo.
    echo Copying AID content to project...
    echo (You will need to re-run this script to get AID updates^)
    echo.
    goto :do_copy
)

echo.
echo Creating junctions to AID...
echo (Changes in AID will automatically apply to this project^)
echo.

REM Create junctions for directories (no admin required)
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\commands" rmdir /S /Q "!TARGET_PATH!\.claude\commands" 2>nul
)
if not exist "!TARGET_PATH!\.claude\commands" (
    mklink /J "!TARGET_PATH!\.claude\commands" "!AID_PATH!\.claude\commands" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\commands -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for commands
    )
) else (
    echo   [SKIP] commands already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\skills" rmdir /S /Q "!TARGET_PATH!\.claude\skills" 2>nul
)
if not exist "!TARGET_PATH!\.claude\skills" (
    mklink /J "!TARGET_PATH!\.claude\skills" "!AID_PATH!\.claude\skills" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\skills -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for skills
    )
) else (
    echo   [SKIP] skills already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\agents" rmdir /S /Q "!TARGET_PATH!\.claude\agents" 2>nul
)
if not exist "!TARGET_PATH!\.claude\agents" (
    mklink /J "!TARGET_PATH!\.claude\agents" "!AID_PATH!\.claude\agents" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\agents -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for agents
    )
) else (
    echo   [SKIP] agents already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\references" rmdir /S /Q "!TARGET_PATH!\.claude\references" 2>nul
)
if not exist "!TARGET_PATH!\.claude\references" (
    mklink /J "!TARGET_PATH!\.claude\references" "!AID_PATH!\.claude\references" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\references -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for references
    )
) else (
    echo   [SKIP] references already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\rules" rmdir /S /Q "!TARGET_PATH!\.claude\rules" 2>nul
)
if not exist "!TARGET_PATH!\.claude\rules" (
    mklink /J "!TARGET_PATH!\.claude\rules" "!AID_PATH!\.claude\rules" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\rules -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for rules
    )
) else (
    echo   [SKIP] rules already exists
)

REM For CLAUDE.md (file), try hard link first, fall back to copy
echo.
echo Linking CLAUDE.md...
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\CLAUDE.md" del "!TARGET_PATH!\CLAUDE.md" 2>nul
)
if not exist "!TARGET_PATH!\CLAUDE.md" (
    mklink /H "!TARGET_PATH!\CLAUDE.md" "!AID_PATH!\CLAUDE.md" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] CLAUDE.md -^> AID (hard link^)
    ) else (
        REM Hard link failed (different drives?), copy instead
        copy "!AID_PATH!\CLAUDE.md" "!TARGET_PATH!\CLAUDE.md" >nul
        echo   [COPY] CLAUDE.md (different drives, copied^)
    )
) else (
    echo   [SKIP] CLAUDE.md already exists
)

goto :after_copy

REM ============================================
REM Copy mode (fallback when symlinks not available)
REM ============================================
:do_copy

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\commands" rmdir /S /Q "!TARGET_PATH!\.claude\commands" 2>nul
)
if not exist "!TARGET_PATH!\.claude\commands" (
    xcopy /E /I /Q "!AID_PATH!\.claude\commands" "!TARGET_PATH!\.claude\commands" >nul
    echo   [COPY] .claude\commands
) else (
    echo   [SKIP] commands already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\skills" rmdir /S /Q "!TARGET_PATH!\.claude\skills" 2>nul
)
if not exist "!TARGET_PATH!\.claude\skills" (
    xcopy /E /I /Q "!AID_PATH!\.claude\skills" "!TARGET_PATH!\.claude\skills" >nul
    echo   [COPY] .claude\skills
) else (
    echo   [SKIP] skills already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\agents" rmdir /S /Q "!TARGET_PATH!\.claude\agents" 2>nul
)
if not exist "!TARGET_PATH!\.claude\agents" (
    xcopy /E /I /Q "!AID_PATH!\.claude\agents" "!TARGET_PATH!\.claude\agents" >nul
    echo   [COPY] .claude\agents
) else (
    echo   [SKIP] agents already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\references" rmdir /S /Q "!TARGET_PATH!\.claude\references" 2>nul
)
if not exist "!TARGET_PATH!\.claude\references" (
    xcopy /E /I /Q "!AID_PATH!\.claude\references" "!TARGET_PATH!\.claude\references" >nul
    echo   [COPY] .claude\references
) else (
    echo   [SKIP] references already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\rules" rmdir /S /Q "!TARGET_PATH!\.claude\rules" 2>nul
)
if not exist "!TARGET_PATH!\.claude\rules" (
    xcopy /E /I /Q "!AID_PATH!\.claude\rules" "!TARGET_PATH!\.claude\rules" >nul
    echo   [COPY] .claude\rules
) else (
    echo   [SKIP] rules already exists
)

REM Copy CLAUDE.md
echo.
echo Copying CLAUDE.md...
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\CLAUDE.md" del "!TARGET_PATH!\CLAUDE.md" 2>nul
)
if not exist "!TARGET_PATH!\CLAUDE.md" (
    copy "!AID_PATH!\CLAUDE.md" "!TARGET_PATH!\CLAUDE.md" >nul
    echo   [COPY] CLAUDE.md
) else (
    echo   [SKIP] CLAUDE.md already exists
)

:after_copy

REM ============================================
REM Copy project-specific files (always copied)
REM ============================================
echo.
echo Copying project-specific files...

REM Copy settings.json template (project may customize)
if not exist "!TARGET_PATH!\.claude\settings.json" (
    if exist "!AID_PATH!\.claude\settings.json" (
        copy "!AID_PATH!\.claude\settings.json" "!TARGET_PATH!\.claude\settings.json" >nul
        echo   [COPY] .claude\settings.json (customize as needed)
    )
) else (
    echo   [SKIP] settings.json already exists
)

REM ============================================
REM Create .aid directory structure
REM ============================================
echo.
echo Creating project state directory...
if not exist "!TARGET_PATH!\.aid" mkdir "!TARGET_PATH!\.aid"
if not exist "!TARGET_PATH!\.aid\qa" mkdir "!TARGET_PATH!\.aid\qa"

REM Create state.json if doesn't exist
if not exist "!TARGET_PATH!\.aid\state.json" (
    call :create_state_json
    echo   [OK] state.json created
) else (
    echo   [SKIP] state.json already exists
)

REM Create context.json if doesn't exist
if not exist "!TARGET_PATH!\.aid\context.json" (
    call :create_context_json
    echo   [OK] context.json created
) else (
    echo   [SKIP] context.json already exists
)

REM ============================================
REM Create docs directory structure
REM ============================================
echo.
echo Creating docs directories (phase outputs)...
if not exist "!TARGET_PATH!\docs" mkdir "!TARGET_PATH!\docs"
if not exist "!TARGET_PATH!\docs\research" mkdir "!TARGET_PATH!\docs\research"
if not exist "!TARGET_PATH!\docs\prd" mkdir "!TARGET_PATH!\docs\prd"
if not exist "!TARGET_PATH!\docs\tech-spec" mkdir "!TARGET_PATH!\docs\tech-spec"
if not exist "!TARGET_PATH!\docs\implementation-plan" mkdir "!TARGET_PATH!\docs\implementation-plan"
echo   [OK] docs/ structure created

REM ============================================
REM Copy .mcp.json template
REM ============================================
echo.
echo Copying MCP configuration...
if not exist "!TARGET_PATH!\.mcp.json" (
    if exist "!AID_PATH!\.mcp.json.windows" (
        copy "!AID_PATH!\.mcp.json.windows" "!TARGET_PATH!\.mcp.json" >nul
        echo   [COPY] .mcp.json (edit with your API tokens)
    ) else (
        echo   [ERROR] .mcp.json.windows template not found
    )
) else (
    echo   [SKIP] .mcp.json already exists (preserving your tokens)
)

REM ============================================
REM Summary
REM ============================================
echo.
echo ========================================
echo    Project Linked Successfully
echo ========================================
echo.
echo Target: "!TARGET_PATH!"
echo.
if "!COPY_MODE!"=="1" (
    echo AID content (COPIED - re-run to update^):
    echo   .claude\commands\   - Slash commands
    echo   .claude\skills\     - Phase skills
    echo   .claude\agents\     - Sub-agents
    echo   .claude\references\ - Reference docs
    echo   .claude\rules\      - Rules
    echo   CLAUDE.md           - AID instructions
    echo.
    echo NOTE: Files were COPIED, not linked.
    echo       To get AID updates, re-run: link-project.bat --force
) else (
    echo Junctions (auto-update from AID^):
    echo   .claude\commands\   -^> AID
    echo   .claude\skills\     -^> AID
    echo   .claude\agents\     -^> AID
    echo   .claude\references\ -^> AID
    echo   .claude\rules\      -^> AID
    echo   CLAUDE.md           -^> AID
)
echo.
echo Project-specific (copied):
echo   .claude\settings.json - Permissions
echo   .aid\state.json       - Phase tracking
echo   .aid\context.json     - Work context
echo   .mcp.json             - MCP config (your tokens)
echo   docs\                 - Phase outputs
echo.
echo Next steps:
echo.
echo 1. Edit "!TARGET_PATH!\.mcp.json" with your API tokens
echo.
echo 2. Open Claude Code in the project:
echo    cd "!TARGET_PATH!"
echo    claude
echo.
echo 3. Run /aid-start to begin working
echo.
echo ========================================
echo.
pause
goto :eof

REM ============================================
REM Subroutines
REM ============================================

:create_state_json
(
echo {
echo   "$schema": "aid-state-v1",
echo   "version": "1.0",
echo   "initialized_at": "%DATE% %TIME%",
echo   "last_updated": "%DATE% %TIME%",
echo   "current_phase": 0,
echo   "phase_name": "Discovery",
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
) > "!TARGET_PATH!\.aid\state.json"
goto :eof

:create_context_json
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
) > "!TARGET_PATH!\.aid\context.json"
goto :eof
