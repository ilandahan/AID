@echo off
REM ============================================
REM AID - AI Development Methodology Installer
REM For Windows
REM ============================================

echo.
echo ========================================
echo    AID Installation Script (Windows)
echo ========================================
echo.

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js found

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm not found!
    pause
    exit /b 1
)

echo [OK] npm found

REM Install npm dependencies
echo.
echo [STEP 1/5] Installing npm dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] npm install had issues, continuing...
)

REM Create .claude directories
echo.
echo [STEP 2/5] Setting up Claude commands and skills...
if not exist ".claude\commands" mkdir ".claude\commands"
if not exist ".claude\skills" mkdir ".claude\skills"

REM Copy command files
copy /Y "memory-system\integration\commands\*.md" ".claude\commands\" >nul 2>nul
copy /Y "skills\commands\*.md" ".claude\commands\" >nul 2>nul
echo [OK] Commands installed

REM Copy skills to .claude/skills
echo Copying skills...
xcopy /E /I /Y "skills\atomic-design" ".claude\skills\atomic-design" >nul 2>nul
xcopy /E /I /Y "skills\atomic-page-builder" ".claude\skills\atomic-page-builder" >nul 2>nul
xcopy /E /I /Y "skills\code-review" ".claude\skills\code-review" >nul 2>nul
xcopy /E /I /Y "skills\context-tracking" ".claude\skills\context-tracking" >nul 2>nul
xcopy /E /I /Y "skills\learning-mode" ".claude\skills\learning-mode" >nul 2>nul
xcopy /E /I /Y "skills\phase-enforcement" ".claude\skills\phase-enforcement" >nul 2>nul
xcopy /E /I /Y "skills\system-architect" ".claude\skills\system-architect" >nul 2>nul
xcopy /E /I /Y "skills\test-driven" ".claude\skills\test-driven" >nul 2>nul
echo [OK] Skills installed

REM Create .aid directory
echo.
echo [STEP 3/5] Creating project state directory...
if not exist ".aid" mkdir ".aid"

REM Create state.json
echo [STEP 4/5] Creating state files...
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
) > ".aid\state.json"

REM Create context.json
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
) > ".aid\context.json"

echo [OK] State files created

REM Create global ~/.aid directory for learning system
echo.
echo [STEP 5/6] Setting up global AID learning system...
set "AID_HOME=%USERPROFILE%\.aid"
if not exist "%AID_HOME%" mkdir "%AID_HOME%"
if not exist "%AID_HOME%\feedback" mkdir "%AID_HOME%\feedback"
if not exist "%AID_HOME%\feedback\pending" mkdir "%AID_HOME%\feedback\pending"
if not exist "%AID_HOME%\feedback\processed" mkdir "%AID_HOME%\feedback\processed"
if not exist "%AID_HOME%\metrics" mkdir "%AID_HOME%\metrics"
if not exist "%AID_HOME%\logs" mkdir "%AID_HOME%\logs"
if not exist "%AID_HOME%\skills" mkdir "%AID_HOME%\skills"

REM Copy templates to global config
if exist "memory-system\templates\config.yaml" (
    if not exist "%AID_HOME%\config.yaml" (
        copy "memory-system\templates\config.yaml" "%AID_HOME%\config.yaml" >nul
    )
)
if exist "memory-system\templates\state.json" (
    if not exist "%AID_HOME%\state.json" (
        copy "memory-system\templates\state.json" "%AID_HOME%\state.json" >nul
    )
)
echo [OK] Global learning system initialized at %AID_HOME%

REM Create .mcp.json if not exists
echo.
echo [STEP 6/6] Creating MCP configuration...
if not exist ".mcp.json" (
    if exist ".mcp.json.example" (
        copy ".mcp.json.example" ".mcp.json" >nul
        echo [OK] MCP configuration created from template
    ) else (
        echo [WARNING] .mcp.json.example not found, skipping MCP config
    )
) else (
    echo [OK] MCP configuration already exists
)

REM Create .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env from template
    )
)

:finish
echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo MCP servers configured in .mcp.json:
if exist ".mcp.json" (
    node -e "const f=require('./.mcp.json'); Object.keys(f.mcpServers||{}).forEach(s=>console.log('  - '+s))" 2>nul
)
echo.
echo Next steps:
echo.
echo 1. Edit .mcp.json with your API tokens:
echo    - ATLASSIAN_API_TOKEN (for Jira)
echo    - FIGMA_API_KEY (for Figma)
echo    - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)
echo.
echo 2. Start Claude Code FROM THIS FOLDER:
echo    cd "%CD%"
echo    claude
echo.
echo 3. Inside Claude Code, verify MCP with: /mcp
echo.
echo 4. Run /aid-start to begin working!
echo.
echo NOTE: MCP servers are PROJECT-SCOPED.
echo       They only work when running Claude from this folder.
echo.
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
